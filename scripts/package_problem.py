#!/usr/bin/env python3
"""按白名单打包题面、题解、标程、样例和数据，不包含制作工作区。"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def paired_files(problem, folder, parser):
    items = sorted(p for p in (problem / folder).glob('*')
                   if p.is_file() and p.suffix in ('.in', '.ans', '.out'))
    if not items:
        parser.error(f'{folder} 中没有输入答案文件')
    inputs = {p.stem for p in items if p.suffix == '.in'}
    answers = {}
    for p in items:
        if p.suffix != '.in':
            answers.setdefault(p.stem, []).append(p)
    if inputs != set(answers) or any(len(paths) != 1 for paths in answers.values()):
        parser.error(f'{folder} 的每个输入必须恰有一个同名 .ans 或 .out，不得有孤立答案')
    return [str(p.relative_to(problem)) for p in items]


def sample_folder(problem, parser):
    populated = [folder for folder in ('down', 'samples')
                 if any(p.is_file() and p.suffix in ('.in', '.ans', '.out')
                        for p in (problem / folder).glob('*'))]
    if len(populated) != 1:
        parser.error('须有且仅有一套样例：down/，或兼容旧题的 samples/')
    return populated[0]


def statement_source(problem):
    source = (problem / 'statement.typ').read_text()
    pattern = r'^#import "\.\./problem-theme\.typ":[^\n]+\n'
    if re.search(pattern, source, flags=re.MULTILINE):
        source = re.sub(pattern, lambda _: (ROOT / 'problem-theme.typ').read_text() + '\n',
                        source, count=1, flags=re.MULTILINE)
    metadata = '#let limits = json("limits.json")'
    if metadata in source:
        limits = json.dumps(json.loads((problem / 'limits.json').read_text()), ensure_ascii=False)
        source = source.replace(metadata, '#let limits = json(bytes(' + json.dumps(limits, ensure_ascii=False) + '))')
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problem', help='项目内题目目录')
    parser.add_argument('--solution', default='solution.cpp', help='题目目录内的标程文件名')
    parser.add_argument('--editorial', default='editorial.md', help='题目目录内的题解文件名')
    parser.add_argument('--samples-only', action='store_true', help='仅打包整套下载样例')
    parser.add_argument('--participant-file', action='append', default=[],
                        help='额外下发的公开接口文件，须在样例目录内；可重复指定')
    args = parser.parse_args()
    problem = (ROOT / args.problem).resolve()
    if not problem.is_dir() or not problem.is_relative_to(ROOT) or problem == ROOT:
        parser.error('必须指定项目内题目目录')
    for name in (args.solution, args.editorial):
        if Path(name).name != name:
            parser.error('标程和题解参数须为文件名')
    folder = sample_folder(problem, parser)
    samples = paired_files(problem, folder, parser)
    attachments = []
    for name in args.participant_file:
        path = Path(name)
        if (path.is_absolute() or len(path.parts) != 2 or path.parts[0] != folder
                or path.suffix not in ('.h', '.hpp', '.cpp', '.md')):
            parser.error('公开接口附件须为样例目录内的 .h/.hpp/.cpp/.md 文件')
        if not (problem / path).is_file():
            parser.error(f'缺少公开接口附件：{name}')
        attachments.append(str(path))
    names = [] if args.samples_only else ['statement.md', 'statement.typ', 'statement.pdf', args.editorial, args.solution]
    for name in names:
        if not (problem / name).is_file():
            parser.error(f'缺少 {name}')
    names.extend(samples)
    names.extend(attachments)
    if not args.samples_only:
        names.extend(paired_files(problem, 'data', parser))
    if len(names) != len(set(names)):
        parser.error('题解、标程与题面文件名不能重复')
    for name in names:
        if not (problem / name).resolve().is_relative_to(problem):
            parser.error(f'文件不能链接到题目目录外：{name}')
    prefix = '' if args.samples_only else problem.name + '/'
    expected = {prefix + name for name in names}
    dist = problem / 'dist'
    dist.mkdir(exist_ok=True)
    archive = dist / f'{problem.name}-{"down" if args.samples_only else "local-package"}.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as output:
        for name in names:
            target = prefix + name
            if name == 'statement.typ':
                output.writestr(target, statement_source(problem))
            else:
                output.write(problem / name, target)
    manifest_path = problem / 'data/manifest.json'
    hashes = {}
    if not args.samples_only and manifest_path.is_file():
        for row in json.loads(manifest_path.read_text()):
            hashes[f'{problem.name}/data/{row["id"]}.in'] = row['input_sha256']
            hashes[f'{problem.name}/data/{row["id"]}.ans'] = row['answer_sha256']
    checked = 0
    with zipfile.ZipFile(archive) as output:
        if set(output.namelist()) != expected or len(output.namelist()) != len(names):
            raise RuntimeError('交付文件清单不匹配')
        for info in output.infolist():
            digest = hashlib.sha256()
            with output.open(info) as content:
                while chunk := content.read(1 << 20):
                    digest.update(chunk)
            if info.filename in hashes:
                if digest.hexdigest() != hashes[info.filename]:
                    raise RuntimeError(f'数据哈希不匹配：{info.filename}')
                checked += 1
    if checked != len(hashes):
        raise RuntimeError('数据清单包含未打包的文件')
    digest = hashlib.sha256()
    with archive.open('rb') as content:
        while chunk := content.read(1 << 20):
            digest.update(chunk)
    record = {'archive': str(archive.relative_to(ROOT)), 'archive_bytes': archive.stat().st_size,
              'sha256': digest.hexdigest(), 'file_count': len(names), 'included_files': sorted(expected),
              'data_pairs': sum(name.startswith('data/') and name.endswith('.in') for name in names),
              'data_files_sha256_checked': checked, 'all_zip_entries_crc_checked': True,
              'sample_folder': folder, 'sample_pairs': len(samples) // 2,
              'participant_files': attachments,
              'samples_only': args.samples_only,
              'typst_theme_and_limits_inlined': not args.samples_only, 'external_publication': False}
    sums = 'down-SHA256SUMS' if args.samples_only else 'SHA256SUMS'
    (dist / sums).write_text(f'{record["sha256"]}  {archive.name}\n')
    reports = problem / 'reports'
    reports.mkdir(exist_ok=True)
    report = 'sample-delivery-validation.json' if args.samples_only else 'delivery-validation.json'
    (reports / report).write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(record, ensure_ascii=False))


if __name__ == '__main__':
    main()

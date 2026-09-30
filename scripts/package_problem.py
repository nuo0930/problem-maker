#!/usr/bin/env python3
"""按白名单打包题面、题解、标程、样例和数据，不包含制作工作区。"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


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
    args = parser.parse_args()
    problem = (ROOT / args.problem).resolve()
    if not problem.is_dir() or not problem.is_relative_to(ROOT) or problem == ROOT:
        parser.error('必须指定项目内题目目录')
    for name in (args.solution, args.editorial):
        if Path(name).name != name:
            parser.error('标程和题解参数须为文件名')
    names = ['statement.md', 'statement.typ', 'statement.pdf', args.editorial, args.solution]
    for name in names:
        if not (problem / name).is_file():
            parser.error(f'缺少 {name}')
    for folder in ('samples', 'data'):
        items = sorted(p for p in (problem / folder).glob('*') if p.is_file() and p.suffix in ('.in', '.ans', '.out'))
        if not items:
            parser.error(f'{folder} 中没有样例或数据文件')
        names.extend(str(p.relative_to(problem)) for p in items)
    if len(names) != len(set(names)):
        parser.error('题解、标程与题面文件名不能重复')
    for name in names:
        if not (problem / name).resolve().is_relative_to(problem):
            parser.error(f'文件不能链接到题目目录外：{name}')
    expected = {f'{problem.name}/{name}' for name in names}
    dist = problem / 'dist'
    dist.mkdir(exist_ok=True)
    archive = dist / f'{problem.name}-local-package.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as output:
        for name in names:
            target = f'{problem.name}/{name}'
            if name == 'statement.typ':
                output.writestr(target, statement_source(problem))
            else:
                output.write(problem / name, target)
    manifest_path = problem / 'data/manifest.json'
    hashes = {}
    if manifest_path.is_file():
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
              'typst_theme_and_limits_inlined': True, 'external_publication': False}
    (dist / 'SHA256SUMS').write_text(f'{record["sha256"]}  {archive.name}\n')
    reports = problem / 'reports'
    reports.mkdir(exist_ok=True)
    (reports / 'delivery-validation.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(record, ensure_ascii=False))


if __name__ == '__main__':
    main()

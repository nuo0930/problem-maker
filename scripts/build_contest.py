#!/usr/bin/env python3
"""Assemble an ordered local contest; keep participant files separate from solutions/data."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_SUFFIXES = {'.in', '.ans', '.out'}
PUBLIC_SUFFIXES = DATA_SUFFIXES | {'.h', '.hpp', '.cpp', '.md'}


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def typst_string(value):
    return json.dumps(str(value), ensure_ascii=False)


def read_problem(name):
    source = (ROOT / name).resolve()
    if not source.is_relative_to(ROOT) or not source.is_dir():
        raise ValueError(f'Invalid source directory: {name}')
    brief = (source / 'BRIEF.md').read_text()
    title = re.search(r'题目全名[：:]\s*(.+)', brief).group(1).strip()
    identifier = re.search(r'题目标签[^：:\n]*[：:]\s*([a-z][a-z0-9_]*)', brief).group(1)
    limits = json.loads((source / 'limits.json').read_text())
    if 'test_count' not in limits:
        limits['test_count'] = limits.get('test_cases')
    if 'time_seconds' not in limits:
        limits['time_seconds'] = limits.get('time_limit_seconds')
        if limits['time_seconds'] is None and 'time_limit_ms' in limits:
            limits['time_seconds'] = limits['time_limit_ms'] / 1000
    if 'memory_mib' not in limits:
        limits['memory_mib'] = limits.get('memory_limit_mib')
    if limits['time_seconds'] is None or limits['memory_mib'] is None:
        raise ValueError(f'Missing time/memory limits: {name}')
    statement = (source / 'statement.typ').read_text()
    kind = 'interactive' if 'kind: "interactive"' in statement else 'batch'
    solution = source / f'{identifier}.cpp'
    if not solution.exists():
        solution = source / 'solution.cpp'
    for path in [solution, source / 'statement.md', source / 'editorial.md']:
        if not path.is_file():
            raise ValueError(f'Missing artifact: {path}')
    data = sorted(p for p in (source / 'data').iterdir() if p.is_file() and p.suffix in DATA_SUFFIXES)
    public = sorted(p for p in (source / 'down').iterdir() if p.is_file() and p.suffix in PUBLIC_SUFFIXES)
    for folder, paths in [('data', data), ('down', public)]:
        for path in paths:
            if path.suffix == '.in' and not any(path.with_suffix(ext) in paths for ext in ['.ans', '.out']):
                raise ValueError(f'Unpaired input: {path}')
        if not paths:
            raise ValueError(f'No files in {name}/{folder}')
    if kind == 'interactive':
        for filename in [f'{identifier}.h', 'grader.cpp', 'README.md']:
            if not any(p.name == filename for p in public):
                raise ValueError(f'Missing public interactive attachment: {filename}')
    return dict(source=source, id=identifier, title=title, kind=kind, limits=limits,
                statement=statement, solution=solution, data=data, public=public)


def statement_body(problem):
    # Remove only single-problem import/metadata/show wrapper; keep the content.
    text = problem['statement']
    match = re.search(r'^#show: problem\.with\([\s\S]*?^\)\s*\n', text, re.MULTILINE)
    if not match:
        raise ValueError(f"Cannot locate statement wrapper: {problem['id']}")
    metadata = ''
    if re.search(r'^#let limits = json\("limits.json"\)', text[:match.start()], re.MULTILINE):
        metadata = '#let limits = json("' + problem['id'] + '-limits.json")\n\n'
    text = metadata + text[match.end():].lstrip()
    # .build/<id>-statement.typ is one level below the contest root.
    text = text.replace('read("down/', f'read("../{problem["id"]}/down/')
    imports = ('#import "../../problem-theme.typ": contest-sample as sample, '
               'sample-reference, epigraph, io-note, cnoi-data-table, subtask-table\n\n')
    return imports + text


def table_rows(problems):
    fields = [
        ('题目名称', lambda p: p['title']),
        ('题目类型', lambda p: '交互型（函数接口）' if p['kind'] == 'interactive' else '传统型'),
        ('目录', lambda p: p['id']),
        ('输入文件名', lambda p: '公开接口' if p['kind'] == 'interactive' else p['id'] + '.in'),
        ('输出文件名', lambda p: '公开接口' if p['kind'] == 'interactive' else p['id'] + '.out'),
        ('每个测试点时限', lambda p: str(p['limits'].get('time_seconds', p['limits'].get('time_limit_seconds'))) + ' 秒'),
        ('内存限制', lambda p: str(p['limits'].get('memory_mib', p['limits'].get('memory_limit_mib'))) + ' MiB'),
        ('测试点／测试包', lambda p: f"{p['limits']['formal_cases']} 用例，{len(p['limits']['package_scores'])} 包" if p['kind'] == 'interactive' else f"{p['limits']['test_count']} 点"),
        ('评分方式', lambda p: '按包计分' if p['kind'] == 'interactive' else '测试点独立等分'),
        ('提交源程序文件名', lambda p: p['id'] + '.cpp'),
    ]
    return '\n'.join('  (label: ' + typst_string(label) + ', values: (' +
                     ', '.join(typst_string(function(p)) for p in problems) + ')), '
                     for label, function in fields)


def build(args):
    destination = (ROOT / args.destination).resolve()
    if destination == ROOT or not destination.is_relative_to(ROOT):
        raise ValueError('Contest destination must be a directory inside the project.')
    problems = [read_problem(name) for name in args.problems]
    if len(problems) != 3:
        raise ValueError('This provincial-selection cover requires three problems.')
    if len({p['id'] for p in problems}) != len(problems):
        raise ValueError('Problem ids must be unique inside a contest.')
    if any(destination == p['source'] or destination.is_relative_to(p['source']) or p['source'].is_relative_to(destination) for p in problems):
        raise ValueError('Contest output must be separate from original problem directories.')
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Contest destination must be empty; use a fresh directory to avoid stale files.')
    build_dir = destination / '.build'
    build_dir.mkdir(parents=True, exist_ok=True)
    participant = destination / 'down'
    participant.mkdir(exist_ok=True)
    records = []
    for problem in problems:
        identifier = problem['id']
        output = destination / identifier
        output.mkdir(exist_ok=True)
        for folder in ['data', 'down']:
            (output / folder).mkdir(exist_ok=True)
        (participant / identifier).mkdir(exist_ok=True)
        row = dict(id=identifier, title=problem['title'], kind=problem['kind'],
                   source=str(problem['source'].relative_to(ROOT)), copied_files=[])
        mappings = [(problem['source'] / 'statement.md', output / f'{identifier}.md'),
                    (problem['source'] / 'editorial.md', output / f'{identifier}_editorial.md'),
                    (problem['solution'], output / f'{identifier}.cpp')]
        mappings.extend((p, output / 'data' / p.name) for p in problem['data'])
        mappings.extend((p, output / 'down' / p.name) for p in problem['public'])
        mappings.extend((p, participant / identifier / p.name) for p in problem['public'])
        for src, dst in mappings:
            # Refuse to traverse symlinks outside the authoritative problem source.
            if not src.resolve().is_relative_to(problem['source']):
                raise ValueError(f'External source link: {src}')
            shutil.copy2(src, dst)
            adapted = False
            if src.name == 'README.md' and problem['solution'].name != identifier + '.cpp':
                text = dst.read_text().replace(problem['solution'].name, identifier + '.cpp')
                dst.write_text(text)
                adapted = True
            digest = sha(dst)
            if not adapted and digest != sha(src):
                raise RuntimeError(f'Copy hash mismatch: {dst}')
            row['copied_files'].append(dict(source=str(src.relative_to(ROOT)),
                target=str(dst.relative_to(destination)), sha256=digest, readme_filename_adapted=adapted))
        (build_dir / f'{identifier}-limits.json').write_text(
            json.dumps(problem['limits'], ensure_ascii=False) + '\n')
        (build_dir / f'{identifier}-statement.typ').write_text(statement_body(problem))
        # Preserve prose and mathematics exactly; only turn Markdown into Typst.
        converted = build_dir / f'{identifier}-editorial.typ'
        command = [args.pandoc, '--from', 'markdown+tex_math_dollars', '--to', 'typst',
                   '--wrap=none', str(output / f'{identifier}_editorial.md'), '-o', str(converted)]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if result.stderr.strip():
            raise RuntimeError(f'Unexpected math conversion warning: {result.stderr}')
        text = converted.read_text()
        # Pandoc emits the obsolete Typst symbol "sect" for TeX \cap.
        text = re.sub(r"\bsect\b", "∩", text)
        # The displayed problem title is provided by the shared contest template.
        text = re.sub(r'^= [^\n]+\n(?:<[^\n]+>\n)?', '', text, count=1)
        converted.write_text(text.lstrip())
        row['data_pairs'] = sum(p.suffix == '.in' for p in problem['data'])
        row['sample_pairs'] = sum(p.suffix == '.in' for p in problem['public'])
        records.append(row)
    statement = ('#import "../../problem-theme.typ": contest-document, contest-cover, contest-problem\n'
                 '#show: contest-document.with(title: ' + typst_string(args.title) +
                 ', session: ' + typst_string(args.session) + ')\n\n'
                 '#contest-cover(title: ' + typst_string(args.title) + ', session: ' +
                 typst_string(args.session) + ', duration: ' + typst_string(args.duration) +
                 ', rows: (\n' + table_rows(problems) + '))\n\n')
    editorial = ('#import "../../problem-theme.typ": contest-document, contest-problem\n'
                 '#show: contest-document.with(title: ' + typst_string(args.title) +
                 ', session: ' + typst_string(args.session) + ', editorial: true)\n\n')
    for i, problem in enumerate(problems):
        common = ('title: ' + typst_string(problem['title']) + ', id: ' + typst_string(problem['id']) +
                  ', contest: ' + typst_string(args.title) + ', session: ' + typst_string(args.session))
        statement += '#pagebreak()\n#contest-problem(' + common + ')[\n  #include "' + problem['id'] + '-statement.typ"\n]\n\n'
        if i:
            editorial += '#pagebreak()\n'
        editorial += '#contest-problem(' + common + ', editorial: true)[\n  #include "' + problem['id'] + '-editorial.typ"\n]\n\n'
    (build_dir / 'statement.typ').write_text(statement)
    (build_dir / 'editorial.typ').write_text(editorial)
    manifest = dict(title=args.title, session=args.session, duration=args.duration,
                    problem_order=[p['id'] for p in problems], problems=records,
                    compile_flags='-std=gnu++17 -O2', math_conversion='Pandoc Markdown+TeX to native Typst',
                    original_problem_directories_preserved=True)
    (build_dir / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    if not args.prepare_only:
        for stem in ['statement', 'editorial']:
            subprocess.run([args.compiler, 'compile', '--root', str(ROOT), '--font-path', str(ROOT / 'fonts'),
                            str(build_dir / f'{stem}.typ'), str(destination / f'{stem}.pdf')], check=True)
        shutil.copy2(destination / 'statement.pdf', participant / 'statement.pdf')
    print(json.dumps(dict(destination=str(destination.relative_to(ROOT)),
                         order=manifest['problem_order'],
                         data_pairs=sum(p['data_pairs'] for p in records),
                         sample_pairs=sum(p['sample_pairs'] for p in records),
                         prepared_only=args.prepare_only), ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination')
    parser.add_argument('problems', nargs='+')
    parser.add_argument('--title', default='省选模拟赛')
    parser.add_argument('--session', default='Day 1')
    parser.add_argument('--duration', default='5 小时')
    parser.add_argument('--pandoc', default='pandoc')
    parser.add_argument('--compiler', default='typst')
    parser.add_argument('--prepare-only', action='store_true')
    build(parser.parse_args())


if __name__ == '__main__':
    main()

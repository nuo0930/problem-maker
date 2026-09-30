#!/usr/bin/env python3
"""使用根目录共用主题编译题面，允许从任意目录调用。"""
import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('problem', help='项目内题目目录，如 example')
    parser.add_argument('--compiler', default=os.environ.get('TYPST_BIN', 'typst'))
    args = parser.parse_args()
    problem = (ROOT / args.problem).resolve()
    if not problem.is_relative_to(ROOT) or not (problem / 'statement.typ').is_file():
        parser.error('题目目录必须位于项目内并含 statement.typ')
    if not (ROOT / 'fonts/lxgw-bright/LXGWBright-Regular.ttf').is_file() or not (ROOT / 'fonts/lxgw-bright/LXGWBright-Medium.ttf').is_file():
        parser.error('缺少 LXGW Bright 字体，请先运行 python3 scripts/download_fonts.py')
    subprocess.run([args.compiler, 'compile', '--root', str(ROOT), '--font-path', str(ROOT / 'fonts'),
                    str(problem / 'statement.typ'), str(problem / 'statement.pdf')],
                   check=True, cwd=ROOT)


if __name__ == '__main__':
    main()

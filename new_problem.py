#!/usr/bin/env python3
"""创建一级题目目录，复制 BRIEF 模板并填入题名和文件标签。"""
import argparse
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent
KINDS = {'batch': '普通非交互', 'interactive': '交互', 'communication': '通信'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('id', help='文件名标签，例如 arena；允许与其他题目相同')
    parser.add_argument('--title', help='题目全名，省略时留待填写')
    parser.add_argument('--style', choices=['CNOI-style', 'IOI-style', 'ICPC-style'])
    parser.add_argument('--kind', choices=KINDS, default='batch')
    parser.add_argument('--directory', help='指定一级目录名，省略时采用 id 或 id-2 等')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', args.id):
        parser.error('id 应以英文字母开头，只含英文字母、数字、下划线或连字符')
    if args.title is not None and (not args.title.strip() or '\n' in args.title or '\r' in args.title):
        parser.error('题目全名须是非空单行文字')
    if args.style == 'CNOI-style' and args.kind == 'communication':
        parser.error('CNOI-style 不设通信题')
    if args.directory and not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', args.directory):
        parser.error('directory 须是一级目录名，不得包含路径分隔符')
    template = ROOT / 'docs/BRIEF.template.md'
    text = template.read_text()
    text = text.replace('- 题目全名：待填写', '- 题目全名：' + (args.title or '待填写'))
    text = text.replace('- 题目标签（[id]）：待填写', '- 题目标签（[id]）：' + args.id)
    if args.style:
        text = text.replace('- 赛制：CNOI-style / IOI-style / ICPC-style（选一项）', '- 赛制：' + args.style)
    text = text.replace('- 题型：普通非交互 / 交互 / 通信（选一项；CNOI-style 不设通信题）', '- 题型：' + KINDS[args.kind])
    if args.kind == 'batch' and args.style:
        io = (f'从 {args.id}.in 读入，输出到 {args.id}.out'
              if args.style == 'CNOI-style' else '标准输入、标准输出')
        text = text.replace('- 输入输出方式、交互接口或通信接口：待定', '- 输入输出方式：' + io)
    directory = args.directory or args.id
    suffix = 1
    while True:
        dest = ROOT / directory
        try:
            dest.mkdir()
            break
        except FileExistsError:
            if args.directory:
                parser.error('指定目录已存在，未覆盖任何文件')
            suffix += 1
            directory = f'{args.id}-{suffix}'
    shutil.copyfile(template, dest / 'BRIEF.md')
    (dest / 'BRIEF.md').write_text(text)
    print(f'Created {directory}/BRIEF.md (id={args.id})')


if __name__ == '__main__':
    main()

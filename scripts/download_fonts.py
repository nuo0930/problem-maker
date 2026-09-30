#!/usr/bin/env python3
"""从字体作者仓库下载固定版本的 LXGW Bright，并校验 SHA-256。"""
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / 'fonts/lxgw-bright'
    manifest = json.loads((folder / 'manifest.json').read_text())
    for entry in manifest['files']:
        target = folder / entry['name']
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == entry['sha256']:
            print(f'{target.name}: 已存在且哈希匹配')
            continue
        request = Request(entry['url'], headers={'User-Agent': 'problem-maker-font-downloader'})
        temporary = None
        try:
            digest = hashlib.sha256()
            count = 0
            with urlopen(request, timeout=60) as response, tempfile.NamedTemporaryFile(dir=folder, delete=False) as output:
                temporary = Path(output.name)
                while chunk := response.read(1 << 20):
                    digest.update(chunk)
                    count += len(chunk)
                    output.write(chunk)
            if digest.hexdigest() != entry['sha256'] or count != entry['bytes']:
                raise RuntimeError(f'{target.name}: 文件校验失败，未替换本地字体')
            temporary.replace(target)
            print(f'{target.name}: 下载完成，SHA-256 匹配')
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    main()

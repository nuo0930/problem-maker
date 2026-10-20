"""Synthetic contest fixtures only; no real problems or private data."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ContestBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'scripts').mkdir()
        shutil.copy2(ROOT / 'scripts/build_contest.py', self.root / 'scripts/build_contest.py')
        shutil.copy2(ROOT / 'problem-theme.typ', self.root / 'problem-theme.typ')
        font_root = Path(os.environ.get('CONTEST_TEST_FONT_PATH', ROOT / 'fonts'))
        (self.root / 'fonts').symlink_to(font_root, target_is_directory=True)
        self.pandoc = self.root / 'fake-pandoc'
        self.pandoc.write_text('#!/usr/bin/env python3\nimport sys\nfrom pathlib import Path\n'
                               'Path(sys.argv[sys.argv.index("-o")+1]).write_text("= Synthetic editorial\\n\\nOnly a fixture.\\n")\n')
        self.pandoc.chmod(0o755)
        for i in range(3):
            name = f'example_{chr(97+i)}'
            p = self.root / name
            (p / 'data').mkdir(parents=True)
            (p / 'down').mkdir()
            (p / 'BRIEF.md').write_text(f'题目全名：Example {i+1}\n题目标签 [id]：{name}\n')
            limits = {'time_limit_ms': 2000, 'memory_limit_mib': 256, 'test_cases': 25}
            if i == 1:
                limits = {'time_seconds': 1, 'memory_mib': 128, 'formal_cases': 10, 'package_scores': [100]}
                for f in [f'{name}.h', 'grader.cpp', 'README.md']:
                    (p / 'down' / f).write_text('Public fixture.\n')
            if i == 2:
                limits = {'time_limit_seconds': 3, 'memory_limit_mib': 512, 'test_count': 20}
            (p / 'limits.json').write_text(json.dumps(limits))
            kind = 'interactive' if i == 1 else 'batch'
            (p / 'statement.typ').write_text(
                '#import "../problem-theme.typ": problem, sample\n'
                '#let limits = json("limits.json")\n'
                '#show: problem.with(\n title: "Example", id: "'+name+'",\n'
                ' style: "CNOI-style", kind: "'+kind+'", test-count: 25,\n)\n\n'
                '= Description\nSynthetic problem. Memory: #limits.memory_mib. Formula: $x^2 + y_1 = 1$.\n'
                '#sample(read("down/'+name+'1.in"), read("down/'+name+'1.ans"))\n')
            for f in ['statement.md', 'editorial.md']:
                (p / f).write_text('# Synthetic document\nOnly a fixture.\n')
            (p / f'{name}.cpp').write_text('int main() { return 0; }\n')
            for folder in ['data', 'down']:
                for suffix in ['in', 'ans']:
                    (p / folder / f'{name}1.{suffix}').write_text('1\n')
            (p / 'down' / 'private.seed').write_text('DO NOT COPY')
        spec = importlib.util.spec_from_file_location('fixture_builder', self.root / 'scripts/build_contest.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def run_build(self, compile_pdf=False):
        cmd = ['python3', str(self.root / 'scripts/build_contest.py'), 'round',
               'example_c', 'example_b', 'example_a', '--pandoc', str(self.pandoc)]
        if os.environ.get('CONTEST_TEST_COMPILER'):
            cmd += ['--compiler', os.environ['CONTEST_TEST_COMPILER']]
        if not compile_pdf:
            cmd.append('--prepare-only')
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_order_whitelist_metadata_and_safe_destination(self):
        result = self.run_build()
        self.assertEqual(result.returncode, 0, result.stderr)
        contest = self.root / 'round'
        manifest = json.loads((contest / '.build/manifest.json').read_text())
        self.assertEqual(manifest['problem_order'], ['example_c', 'example_b', 'example_a'])
        for row in manifest['problems']:
            for copied in row['copied_files']:
                self.assertEqual(self.module.sha(contest / copied['target']), copied['sha256'])
        self.assertFalse(list((contest / 'down').rglob('private.seed')))
        self.assertFalse(list((contest / 'down').rglob('*editorial*')))
        self.assertFalse((contest / 'down/example_a/example_a.cpp').exists())
        body = (contest / '.build/example_a-statement.typ').read_text()
        self.assertIn('json("example_a-limits.json")', body)
        self.assertIn('read("../example_a/down/example_a1.in")', body)
        metadata = json.loads((contest / '.build/example_a-limits.json').read_text())
        self.assertEqual(metadata['time_seconds'], 2)
        self.assertEqual(metadata['test_count'], 25)
        self.assertEqual(self.run_build().returncode, 1)
        outside = self.root / 'external.in'
        outside.write_text('external')
        self.addCleanup(outside.unlink, missing_ok=True)
        (self.root / 'example_a/down/escape.in').symlink_to(outside)
        (self.root / 'example_a/down/escape.ans').write_text('1')
        p = self.module.read_problem('example_a')
        self.assertTrue(any(not f.resolve().is_relative_to(p['source']) for f in p['public']))
        # The build must reject that link, rather than copying external content.
        result = subprocess.run(['python3', str(self.root / 'scripts/build_contest.py'), 'unsafe',
                                 'example_a', 'example_b', 'example_c', '--prepare-only',
                                 '--pandoc', str(self.pandoc)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('External source link', result.stderr)

    @unittest.skipUnless(shutil.which('typst'), 'Typst is not installed')
    def test_typst_integration_with_stub_markdown_converter(self):
        result = self.run_build(compile_pdf=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        contest = self.root / 'round'
        for name in ['statement.pdf', 'editorial.pdf']:
            self.assertTrue((contest / name).read_bytes().startswith(b'%PDF'))
        self.assertEqual((contest / 'statement.pdf').read_bytes(),
                         (contest / 'down/statement.pdf').read_bytes())


if __name__ == '__main__':
    unittest.main()

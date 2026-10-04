"""Generic regression tests for sample selection and the private-file whitelist."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='problem-package-test-')
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        shutil.copyfile(ROOT / 'scripts/package_problem.py', self.root / 'scripts/package_problem.py')
        (self.root / 'problem-theme.typ').write_text('// generic test theme\n')
        self.problem = self.root / 'example'
        self.problem.mkdir()
        for name in ('statement.md', 'statement.pdf', 'solution.cpp', 'editorial.md'):
            (self.problem / name).write_text('generic test fixture\n')
        (self.problem / 'statement.typ').write_text('#import "../problem-theme.typ": problem\n')
        (self.problem / 'BRIEF.md').write_text('PRIVATE FIXTURE MUST NOT BE PACKAGED\n')
        (self.problem / 'reports').mkdir()
        (self.problem / 'reports/secret.txt').write_text('PRIVATE FIXTURE REPORT\n')
        self.pair('data', '01')

    def tearDown(self):
        self.temp.cleanup()

    def pair(self, folder, name):
        path = self.problem / folder
        path.mkdir(exist_ok=True)
        (path / (name + '.in')).write_text('1\n')
        (path / (name + '.ans')).write_text('1\n')

    def run_package(self, *args):
        return subprocess.run(['python3', str(self.root / 'scripts/package_problem.py'), 'example', *args],
                              capture_output=True, text=True)

    def test_down_whitelist_and_theme(self):
        self.pair('down', 'example1')
        self.assertEqual(self.run_package().returncode, 0)
        with zipfile.ZipFile(self.problem / 'dist/example-local-package.zip') as archive:
            names = set(archive.namelist())
            self.assertEqual(len(names), 9)
            self.assertIn('example/down/example1.in', names)
            self.assertNotIn('example/BRIEF.md', names)
            self.assertFalse(any('/reports/' in name for name in names))
            self.assertNotIn(b'../problem-theme.typ', archive.read('example/statement.typ'))

    def test_legacy_samples(self):
        self.pair('samples', '1')
        self.assertEqual(self.run_package().returncode, 0)

    def test_sample_only_without_other_artifacts(self):
        self.pair('down', 'example1')
        for name in ('statement.md', 'statement.typ', 'statement.pdf', 'editorial.md', 'solution.cpp'):
            (self.problem / name).unlink()
        shutil.rmtree(self.problem / 'data')
        self.assertEqual(self.run_package('--samples-only').returncode, 0)
        with zipfile.ZipFile(self.problem / 'dist/example-down.zip') as archive:
            self.assertEqual(set(archive.namelist()), {'down/example1.in', 'down/example1.ans'})

    def test_two_sample_sources_rejected(self):
        self.pair('down', 'example1')
        self.pair('samples', '1')
        self.assertNotEqual(self.run_package().returncode, 0)

    def test_orphan_input_rejected(self):
        self.pair('down', 'example1')
        (self.problem / 'down/example1.ans').unlink()
        self.assertNotEqual(self.run_package().returncode, 0)

    def test_orphan_answer_rejected(self):
        self.pair('down', 'example1')
        (self.problem / 'down/example2.ans').write_text('1\n')
        self.assertNotEqual(self.run_package('--samples-only').returncode, 0)

    def test_ambiguous_answers_rejected(self):
        self.pair('down', 'example1')
        (self.problem / 'down/example1.out').write_text('1\n')
        self.assertNotEqual(self.run_package().returncode, 0)

    def test_external_link_rejected(self):
        self.pair('down', 'example1')
        target = self.problem / 'down/example1.in'
        target.unlink()
        secret = self.root / 'outside.in'
        secret.write_text('PRIVATE EXTERNAL FIXTURE\n')
        target.symlink_to(secret)
        self.assertNotEqual(self.run_package().returncode, 0)


if __name__ == '__main__':
    unittest.main()

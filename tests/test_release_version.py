from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("check_version", ROOT / "scripts/check_version.py")
assert SPEC is not None and SPEC.loader is not None
VERSION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERSION)
sys.path.pop(0)


class ReleaseVersionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "VERSION").write_text("0.9.0\n")
        (self.root / "CHANGELOG.md").write_text("# Changes\n\n## [0.9.0]\n")
        self.skill = self.root / "skills/product/team-example/SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self.original = '---\nmetadata:\n  version: "1.0"\n---\n\nBody version: 1.0\n'
        self.skill.write_text(self.original)

    def test_check_is_read_only_and_sync_preserves_body(self) -> None:
        self.assertTrue(VERSION.check_release(self.root))
        self.assertEqual(self.original, self.skill.read_text())
        self.assertEqual([], VERSION.check_release(self.root, sync=True))
        self.assertEqual(self.original.replace('"1.0"', '"0.9.0"'), self.skill.read_text())
        self.assertEqual([], VERSION.check_release(self.root, tag="v0.9.0"))
        self.assertEqual([], VERSION.check_release(self.root, sync=True))

    def test_bad_tag_prevents_sync(self) -> None:
        self.assertTrue(VERSION.check_release(self.root, sync=True, tag="v0.9.1"))
        self.assertEqual(self.original, self.skill.read_text())

    def test_missing_changelog_entry_prevents_sync(self) -> None:
        (self.root / "CHANGELOG.md").write_text("## [0.8.0]\n")
        self.assertTrue(VERSION.check_release(self.root, sync=True))
        self.assertEqual(self.original, self.skill.read_text())

    def test_invalid_versions_are_rejected(self) -> None:
        for version in ("0.9", "01.9.0", "v0.9.0", "0.9.0\n1.0.0"):
            with self.subTest(version=version):
                (self.root / "VERSION").write_text(version)
                self.assertTrue(VERSION.check_release(self.root, sync=True))
                self.assertEqual(self.original, self.skill.read_text())


if __name__ == "__main__":
    unittest.main()

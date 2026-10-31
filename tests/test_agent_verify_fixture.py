from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent.audit_verify_case import audit
from agent.prepare_verify_case import git, prepare


ROOT = Path(__file__).resolve().parents[1]


class VerifyFixtureTests(unittest.TestCase):
    def test_reusing_a_case_refuses_to_overwrite_existing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "case"
            prepare(ROOT, destination, "automatic", False)
            evidence = destination / "response.md"
            evidence.write_text("existing evidence")
            with self.assertRaises(FileExistsError):
                prepare(ROOT, destination, "automatic", False)
            self.assertEqual(evidence.read_text(), "existing evidence")

    def test_artifact_audit_detects_code_change_staging_and_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "case"
            prepare(ROOT, destination, "single", False)
            project = destination / "project"
            before = audit(destination)
            self.assertTrue(before["head_unchanged"])
            self.assertTrue(before["index_empty"])
            self.assertEqual(before["protected_changes"], [])
            (project / "greet.py").write_text('print("Changed")\n')
            self.assertEqual(audit(destination)["protected_changes"], ["greet.py"])
            git(project, "add", "greet.py")
            self.assertFalse(audit(destination)["index_empty"])
            git(project, "commit", "-m", "Unexpected verifier commit")
            self.assertFalse(audit(destination)["head_unchanged"])

    def test_standalone_fixture_does_not_silently_install_neighbor_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "case"
            prepare(ROOT, destination, "single", True)
            self.assertEqual([p.name for p in (destination / "skills").iterdir()], ["team-task-verify"])


if __name__ == "__main__":
    unittest.main()

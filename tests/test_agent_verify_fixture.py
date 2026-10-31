from __future__ import annotations

import tempfile
import json
import subprocess
import sys
import unittest
from pathlib import Path

from agent.audit_verify_case import audit
from agent.prepare_verify_case import git, prepare
from agent.prepare_refactor_case import prepare as prepare_refactor


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


class RefactorFixtureTests(unittest.TestCase):
    def test_replays_have_identical_baseline_commits_and_refuse_existing_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "first", Path(directory) / "second"
            for destination in (first, second):
                prepare_refactor(ROOT, destination, "implement")
            snapshots = [json.loads((p / "before.json").read_text()) for p in (first, second)]
            self.assertEqual(snapshots[0]["head"], snapshots[1]["head"])
            self.assertEqual(snapshots[0]["files"], snapshots[1]["files"])
            with self.assertRaises(FileExistsError):
                prepare_refactor(ROOT, first, "implement")

    def test_cli_baseline_distinguishes_supported_contract_from_existing_defect(self):
        with tempfile.TemporaryDirectory() as directory:
            for case, success in (("implement", True), ("failed-baseline", False)):
                with self.subTest(case=case):
                    destination = Path(directory) / case
                    prepare_refactor(ROOT, destination, case)
                    result = subprocess.run([sys.executable, "-m", "unittest", "-v"], cwd=destination / "project", capture_output=True, text=True)
                    self.assertEqual(result.returncode == 0, success, result.stderr)


if __name__ == "__main__":
    unittest.main()

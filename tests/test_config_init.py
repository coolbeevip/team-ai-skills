from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "skills/config/team-config-init/scripts/init_team_config.py"
)


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


class ConfigInitTests(unittest.TestCase):
    def test_former_config_owners_delegate_initialization(self) -> None:
        skill_paths = [
            "skills/product/team-spec-refine/SKILL.md",
            "skills/product/team-concept-whitepaper/SKILL.md",
            "skills/product/team-discovery-robotics/SKILL.md",
            "skills/product/team-spec-review/SKILL.md",
            "skills/product/team-spec-to-prd/SKILL.md",
            "skills/delivery/team-prd-to-brief/SKILL.md",
            "skills/tech-debt/team-tech-debt-analyze/SKILL.md",
            "skills/tech-debt/team-tech-debt-refine/SKILL.md",
            "skills/tech-debt/team-tech-debt-review/SKILL.md",
            "skills/harness/team-codex-harness/SKILL.md",
            "skills/writing/team-writing-style/SKILL.md",
        ]
        for relative_path in skill_paths:
            with self.subTest(skill=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn("team-config-init", text)
                self.assertNotIn("询问一次并创建", text)
                self.assertNotIn("询问并创建", text)

    def test_dry_run_does_not_create_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run("--language", "zh-CN", "--json", cwd=root)
            self.assertEqual(0, result.returncode, result.stdout)
            plan = json.loads(result.stdout)
            self.assertEqual("dry-run", plan["mode"])
            self.assertEqual("created", plan["action"])
            self.assertIn("language: \"zh-CN\"", plan["content"])
            self.assertFalse((root / "team-spec/config.yml").exists())

    def test_execute_creates_minimal_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run("--language", "zh-CN", "--execute", "--json", cwd=root)
            self.assertEqual(0, result.returncode, result.stdout)
            config = (root / "team-spec/config.yml").read_text(encoding="utf-8")
            self.assertEqual('language: "zh-CN"\n', config)

    def test_full_scope_reports_missing_version_control(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "team-spec/config.yml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("language: zh-CN\n", encoding="utf-8")

            result = run("--scope", "all", "--json", cwd=root)

            self.assertEqual(2, result.returncode, result.stdout)
            plan = json.loads(result.stdout)
            self.assertEqual("unchanged", plan["action"])
            self.assertEqual("incomplete", plan["validation"]["status"])
            self.assertIn(
                "version_control.language", plan["validation"]["missing_fields"]
            )

    def test_configured_reference_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "team-spec/config.yml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(
                "language: zh-CN\n"
                "access_policy:\n"
                "  mode: default-readonly\n"
                "  directory_file: team-spec/access_policy/default.md\n"
                "  user_file_template: team-spec/access_policy/{user_name}.md\n",
                encoding="utf-8",
            )

            result = run("--json", cwd=root)

            self.assertEqual(2, result.returncode, result.stdout)
            plan = json.loads(result.stdout)
            self.assertEqual("incomplete", plan["validation"]["status"])
            self.assertEqual(
                [
                    {
                        "field": "access_policy.directory_file",
                        "path": "team-spec/access_policy/default.md",
                    }
                ],
                plan["validation"]["missing_files"],
            )

    def test_execute_is_blocked_when_selected_scope_is_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run(
                "--language",
                "zh-CN",
                "--scope",
                "all",
                "--execute",
                "--json",
                cwd=root,
            )

            self.assertEqual(2, result.returncode, result.stdout)
            plan = json.loads(result.stdout)
            self.assertEqual("created", plan["action"])
            self.assertEqual("blocked-incomplete", plan["write_status"])
            self.assertFalse((root / "team-spec/config.yml").exists())

    def test_user_file_template_does_not_require_concrete_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            policy_path = root / "team-spec/access_policy/default.md"
            policy_path.parent.mkdir(parents=True)
            policy_path.write_text("# Default access policy\n", encoding="utf-8")
            config_path = root / "team-spec/config.yml"
            config_path.write_text(
                "language: zh-CN\n"
                "access_policy:\n"
                "  mode: default-readonly\n"
                "  directory_file: team-spec/access_policy/default.md\n"
                "  user_file_template: team-spec/access_policy/{user_name}.md\n",
                encoding="utf-8",
            )

            result = run("--json", cwd=root)

            self.assertEqual(0, result.returncode, result.stdout)
            plan = json.loads(result.stdout)
            self.assertEqual("valid", plan["validation"]["status"])

    def test_incremental_update_preserves_unknown_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "team-spec/config.yml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(
                "language: zh-CN\ncustom:\n  enabled: true\n",
                encoding="utf-8",
            )
            result = run(
                "--version-control-language",
                "en-US",
                "--system",
                "git",
                "--execute",
                "--json",
                cwd=root,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            config = config_path.read_text(encoding="utf-8")
            self.assertIn("custom:\n  enabled: true", config)
            self.assertIn('version_control:\n  language: "en-US"\n  system: "git"', config)

    def test_existing_value_requires_overwrite_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "team-spec/config.yml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(
                "language: zh-CN # team default\n", encoding="utf-8"
            )
            rejected = run("--language", "en-US", "--execute", "--json", cwd=root)
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn("Use --overwrite", json.loads(rejected.stdout)["error"])
            self.assertEqual(
                "language: zh-CN # team default\n",
                config_path.read_text(encoding="utf-8"),
            )

            accepted = run(
                "--language",
                "en-US",
                "--overwrite",
                "--execute",
                "--json",
                cwd=root,
            )
            self.assertEqual(0, accepted.returncode, accepted.stdout)
            self.assertEqual(
                'language: "en-US" # team default\n',
                config_path.read_text(encoding="utf-8"),
            )

    def test_new_config_requires_explicit_field(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run("--json", cwd=Path(directory))
            self.assertNotEqual(0, result.returncode)
            self.assertIn("requires at least one explicit field", result.stdout)


if __name__ == "__main__":
    unittest.main()

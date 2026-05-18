from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

SKILL_CATALOG = ROOT / "scripts" / "skill_catalog.py"
ARCHIVE_SCRIPT = ROOT / "skills" / "product" / "team-spec-archive" / "scripts" / "archive_team_spec.py"
GITHUB_ISSUES_SCRIPT = ROOT / "skills" / "delivery" / "team-github-issue-publish" / "scripts" / "publish_github_issues.py"
GITLAB_ISSUES_SCRIPT = ROOT / "skills" / "delivery" / "team-gitlab-issue-publish" / "scripts" / "publish_gitlab_issues.py"
GITHUB_PR_SCRIPT = ROOT / "skills" / "delivery" / "team-github-pr-create" / "scripts" / "create_github_pr.py"


def run_command(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        command,
        cwd=cwd or ROOT,
        env=merged_env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def init_git_repo(path: Path, branch: str = "main") -> None:
    run_command(["git", "init", "-b", branch], cwd=path)
    run_command(["git", "config", "user.name", "Automation Test"], cwd=path)
    run_command(["git", "config", "user.email", "automation@example.com"], cwd=path)


class RepositoryAutomationSmokeTest(unittest.TestCase):
    def test_skill_catalog_validate_and_sync_check(self) -> None:
        run_command([PYTHON, str(SKILL_CATALOG), "validate"], cwd=ROOT)
        run_command([PYTHON, str(SKILL_CATALOG), "sync-website", "--check"], cwd=ROOT)

    def test_help_commands(self) -> None:
        for script in [ARCHIVE_SCRIPT, GITHUB_ISSUES_SCRIPT, GITLAB_ISSUES_SCRIPT, GITHUB_PR_SCRIPT]:
            with self.subTest(script=script.name):
                result = run_command([PYTHON, str(script), "--help"], cwd=ROOT)
                self.assertIn("usage:", result.stdout.lower())

    def test_archive_dry_run_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            slug = "2026-05-18-export-filter"
            (project / "team-spec" / "active" / "spec" / "refine").mkdir(parents=True)
            (project / "team-spec" / "active" / "prd").mkdir(parents=True)
            (project / "team-spec" / "active" / "issues" / slug).mkdir(parents=True)
            (project / "team-spec" / "active" / "spec" / "refine" / f"{slug}.md").write_text("# refine\n", encoding="utf-8")
            (project / "team-spec" / "active" / "prd" / f"{slug}.md").write_text("# prd\n", encoding="utf-8")
            (project / "team-spec" / "active" / "issues" / slug / "001-add-export-filter.md").write_text("# issue\n", encoding="utf-8")

            result = run_command(
                [
                    PYTHON,
                    str(ARCHIVE_SCRIPT),
                    "--team-spec-dir",
                    str(project / "team-spec"),
                    "--slug",
                    slug,
                    "--json",
                ],
                cwd=project,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["slug"], slug)
            self.assertEqual(payload["reason"], "manual")
            self.assertGreaterEqual(len(payload["moves"]), 3)

    def test_github_issue_publish_dry_run_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            issues_dir = project / "issues"
            issues_dir.mkdir(parents=True)
            (issues_dir / "001-add-export-filter.md").write_text(
                textwrap.dedent(
                    """
                    # Add export filter

                    ## What to build

                    - Add an export filter to the report page.

                    ## Acceptance criteria

                    - [ ] Users can filter exports by status.

                    ## Blocked by

                    - None
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            result = run_command(
                [
                    PYTHON,
                    str(GITHUB_ISSUES_SCRIPT),
                    "--issues-dir",
                    str(issues_dir),
                    "--repo",
                    "example/repo",
                    "--json",
                ],
                cwd=project,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["counts"], {"planned": 1})
            self.assertEqual(payload["issues"][0]["title"], "Add export filter")

    def test_gitlab_issue_publish_dry_run_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            issues_dir = project / "issues"
            issues_dir.mkdir(parents=True)
            (issues_dir / "001-add-export-filter.md").write_text(
                textwrap.dedent(
                    """
                    # Add export filter

                    ## What to build

                    - Add an export filter to the report page.

                    ## Acceptance criteria

                    - [ ] Users can filter exports by status.

                    ## Blocked by

                    - None
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            result = run_command(
                [
                    PYTHON,
                    str(GITLAB_ISSUES_SCRIPT),
                    "--issues-dir",
                    str(issues_dir),
                    "--project",
                    "example/repo",
                    "--json",
                ],
                cwd=project,
                env={"GITLAB_URL": "https://gitlab.example.com"},
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["counts"], {"planned": 1})
            self.assertEqual(payload["issues"][0]["title"], "Add export filter")

    def test_github_pr_dry_run_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            init_git_repo(project)
            (project / "README.md").write_text("hello\n", encoding="utf-8")
            run_command(["git", "add", "README.md"], cwd=project)
            run_command(["git", "commit", "-m", "initial"], cwd=project)
            run_command(["git", "checkout", "-b", "123-add-export-filter"], cwd=project)
            run_command(["git", "remote", "add", "origin", "https://github.com/example/repo.git"], cwd=project)

            result = run_command(
                [
                    PYTHON,
                    str(GITHUB_PR_SCRIPT),
                    "--target-branch",
                    "main",
                    "--json",
                ],
                cwd=project,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["mode"], "dry-run")
            self.assertEqual(payload["issue_number"], "123")
            self.assertEqual(payload["source_repo"], "example/repo")
            self.assertEqual(payload["target_repo"], "example/repo")
            self.assertFalse(payload["dirty_worktree"])


if __name__ == "__main__":
    unittest.main()

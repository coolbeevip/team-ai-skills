from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "2026-07-31-export-filter"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(
    script: Path,
    *args: str,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command_env = os.environ.copy()
    if env:
        command_env.update(env)
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd,
        env=command_env,
        check=True,
        capture_output=True,
        text=True,
    )


def run_failure(
    script: Path,
    *args: str,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command_env = os.environ.copy()
    if env:
        command_env.update(env)
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd,
        env=command_env,
        check=False,
        capture_output=True,
        text=True,
    )


def task_markdown(
    task_id: str,
    title: str,
    *,
    status: str,
    commit: str,
    blocked_by: str = "None",
) -> str:
    return f"""# {title}

## Task ID

{task_id}

## Status

{status}

## Type

AFK（可独立执行，无需人工决策）

## Acceptance criteria

- [ ] Given a user, When the behavior runs, Then the result is visible.

## Blocked by

- {blocked_by}

## Commit

{commit}
"""


def create_workspace(root: Path, tasks: list[tuple[str, str, str, str, str]]) -> Path:
    workspace = root / "team-spec" / "active" / SLUG
    write(
        workspace / "prd" / "prd.md",
        """# Export filtered rows

## Goal

Export only rows matching the active filters.

## Scope

Update the export path and its regression coverage.

## Acceptance criteria

- [ ] Filtered rows are exported.

## Compatibility / impact

No API compatibility changes.
""",
    )
    write(
        root / "team-spec" / "config.yml",
        """language: en-US
version_control:
  system: git
  trunk_branch: main
  source_remote: origin
  target_remote: origin
""",
    )
    for task_id, title, status, commit, blocked_by in tasks:
        write(
            workspace / "tasks" / f"{task_id}-{title.lower().replace(' ', '-')}.md",
            task_markdown(
                task_id,
                title,
                status=status,
                commit=commit,
                blocked_by=blocked_by,
            ),
        )
    return workspace


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def create_git_delivery_repo(remote_url: str) -> tuple[tempfile.TemporaryDirectory[str], Path, list[str]]:
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "tests@example.com")
    git(root, "config", "user.name", "Delivery Tests")
    write(root / "app.txt", "base\n")
    git(root, "add", "app.txt")
    git(root, "commit", "-m", "Base")
    base = git(root, "rev-parse", "HEAD")
    git(root, "remote", "add", "origin", remote_url)
    git(root, "update-ref", "refs/remotes/origin/main", base)
    git(root, "checkout", "-b", SLUG)

    commits: list[str] = []
    for index in (1, 2):
        write(root / f"task-{index}.txt", f"task {index}\n")
        git(root, "add", f"task-{index}.txt")
        git(root, "commit", "-m", f"T{index:03d}: task {index}")
        commits.append(git(root, "rev-parse", "HEAD"))

    create_workspace(
        root,
        [
            ("T001", "Add export path", "committed", commits[0], "None"),
            ("T002", "Add regression coverage", "committed", commits[1], "T001"),
        ],
    )
    return temporary, root, commits


class SpecDeliveryWorkflowTests(unittest.TestCase):
    def test_legacy_alignment_archives_as_brief(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(
                root
                / "team-spec"
                / "active"
                / "prd"
                / f"{SLUG}-alignment.md",
                "# Legacy alignment\n",
            )
            result = run(
                ROOT
                / "skills/product/team-spec-archive/scripts/archive_team_spec.py",
                "--slug",
                SLUG,
                "--json",
                cwd=root,
            )
            plan = json.loads(result.stdout)
            self.assertEqual(
                f"team-spec/archive/{SLUG}/prd/brief.md",
                plan["moves"][0]["target"],
            )

    def test_task_batch_uses_committed_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_workspace(
                root,
                [
                    ("T001", "Add export path", "committed", "abc1234", "None"),
                    ("T002", "Add tests", "draft", "Pending", "T001"),
                ],
            )
            result = run(
                ROOT
                / "skills/delivery/team-task-batch-implement/scripts/plan_task_batch.py",
                "--slug",
                SLUG,
                "--json",
                cwd=root,
            )
            plan = json.loads(result.stdout)
            self.assertEqual(["T002"], [item["key"] for item in plan["queue"]])
            self.assertEqual(["T001"], [item["key"] for item in plan["skipped"]])

    def test_github_issue_dry_run_aggregates_all_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_workspace(
                root,
                [
                    ("T001", "Add export path", "committed", "abc1234", "None"),
                    ("T002", "Add tests", "draft", "Pending", "T001"),
                ],
            )
            result = run(
                ROOT
                / "skills/delivery/team-spec-create-issue-github/scripts/create_github_issue.py",
                "--slug",
                SLUG,
                "--repo",
                "owner/repo",
                "--json",
                cwd=root,
            )
            plan = json.loads(result.stdout)
            self.assertEqual(2, plan["task_count"])
            self.assertEqual("create-or-sync", plan["action"])
            self.assertIn("T001 Add export path", plan["body"])
            self.assertIn("T002 Add tests", plan["body"])
            self.assertIn(f"team-spec-slug: {SLUG}", plan["body"])

    def test_gitlab_issue_dry_run_aggregates_all_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_workspace(
                root,
                [
                    ("T001", "Add export path", "committed", "abc1234", "None"),
                    ("T002", "Add tests", "draft", "Pending", "T001"),
                ],
            )
            result = run(
                ROOT
                / "skills/delivery/team-spec-create-issue-gitlab/scripts/create_gitlab_issue.py",
                "--slug",
                SLUG,
                "--project",
                "group/repo",
                "--json",
                cwd=root,
                env={"GITLAB_URL": "https://gitlab.example.com"},
            )
            plan = json.loads(result.stdout)
            self.assertEqual(2, plan["task_count"])
            self.assertEqual("create-or-sync", plan["action"])
            self.assertIn("T001 Add export path", plan["body"])
            self.assertIn("T002 Add tests", plan["body"])
            self.assertIn(f"team-spec-slug: {SLUG}", plan["body"])

    def test_github_pr_dry_run_requires_one_spec_branch_with_task_commits(self) -> None:
        temporary, root, commits = create_git_delivery_repo(
            "https://github.com/owner/repo.git"
        )
        self.addCleanup(temporary.cleanup)
        result = run(
            ROOT
            / "skills/delivery/team-spec-create-pr-github/scripts/create_github_pr.py",
            "--slug",
            SLUG,
            "--source-repo",
            "owner/repo",
            "--target-repo",
            "owner/repo",
            "--json",
            cwd=root,
        )
        plan = json.loads(result.stdout)
        self.assertEqual(SLUG, plan["branch"])
        self.assertEqual(commits, plan["branch_commits"])
        self.assertEqual(2, plan["task_count"])

    def test_gitlab_mr_dry_run_requires_one_spec_branch_with_task_commits(self) -> None:
        temporary, root, commits = create_git_delivery_repo(
            "https://gitlab.example.com/group/repo.git"
        )
        self.addCleanup(temporary.cleanup)
        result = run(
            ROOT
            / "skills/delivery/team-spec-create-mr-gitlab/scripts/create_gitlab_mr.py",
            "--slug",
            SLUG,
            "--source-project",
            "group/repo",
            "--target-project",
            "group/repo",
            "--json",
            cwd=root,
            env={"GITLAB_URL": "https://gitlab.example.com"},
        )
        plan = json.loads(result.stdout)
        self.assertEqual(SLUG, plan["branch"])
        self.assertEqual(commits, plan["branch_commits"])
        self.assertEqual(2, plan["task_count"])

    def test_github_pr_rejects_uncommitted_task_status(self) -> None:
        temporary, root, _ = create_git_delivery_repo(
            "https://github.com/owner/repo.git"
        )
        self.addCleanup(temporary.cleanup)
        task_path = next(
            (root / "team-spec" / "active" / SLUG / "tasks").glob("T002-*.md")
        )
        write(
            task_path,
            task_path.read_text(encoding="utf-8").replace(
                "## Status\n\ncommitted", "## Status\n\nverified"
            ),
        )
        result = run_failure(
            ROOT
            / "skills/delivery/team-spec-create-pr-github/scripts/create_github_pr.py",
            "--slug",
            SLUG,
            "--source-repo",
            "owner/repo",
            "--target-repo",
            "owner/repo",
            "--json",
            cwd=root,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("T002 is not committed", result.stderr)

    def test_github_pr_rejects_commit_not_mapped_to_a_task(self) -> None:
        temporary, root, _ = create_git_delivery_repo(
            "https://github.com/owner/repo.git"
        )
        self.addCleanup(temporary.cleanup)
        write(root / "unmapped.txt", "unmapped\n")
        git(root, "add", "unmapped.txt")
        git(root, "commit", "-m", "Unmapped integration change")
        result = run_failure(
            ROOT
            / "skills/delivery/team-spec-create-pr-github/scripts/create_github_pr.py",
            "--slug",
            SLUG,
            "--source-repo",
            "owner/repo",
            "--target-repo",
            "owner/repo",
            "--json",
            cwd=root,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("commits not mapped to Tasks", result.stderr)


if __name__ == "__main__":
    unittest.main()

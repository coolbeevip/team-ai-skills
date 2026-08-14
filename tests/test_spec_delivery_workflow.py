from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "2026-07-31-export-filter"


def load_script_module(script_path: Path) -> types.ModuleType:
    """Import a standalone `scripts/*.py` file, making its local
    `_team_common` sibling importable, without executing its `main()`.
    """
    scripts_dir = str(script_path.parent)
    inserted = scripts_dir not in sys.path
    if inserted:
        sys.path.insert(0, scripts_dir)
    try:
        spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(spec.name, None)
        return module
    finally:
        if inserted:
            sys.path.remove(scripts_dir)


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
  language: zh-CN
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
        git(root, "commit", "-m", f"Implement task {index}")
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
    def test_robotics_dashboard_does_not_overload_workspace_status(self) -> None:
        skill = (
            ROOT / "skills/product/team-discovery-robotics/SKILL.md"
        ).read_text(encoding="utf-8")
        status_format = (
            ROOT
            / "skills/product/team-discovery-robotics/references/STATUS-FORMAT.md"
        ).read_text(encoding="utf-8")
        dashboard_format = (
            ROOT
            / "skills/product/team-discovery-robotics/references/PROJECT-DASHBOARD-FORMAT.md"
        ).read_text(encoding="utf-8")

        self.assertIn("design/project-dashboard.md", skill)
        self.assertIn("只记录一个产品需求链路机器状态", skill)
        self.assertNotIn("STATUS.md`：项目仪表盘", skill)
        self.assertIn("只记录整个工作区的生命周期状态", status_format)
        self.assertNotIn("成本跟踪", status_format)
        self.assertIn("design/project-dashboard.md", dashboard_format)
        self.assertIn("本表不复制机器状态", dashboard_format)

    def test_direct_branch_initialization_switches_and_fast_forwards_trunk(self) -> None:
        for relative_path in (
            "skills/delivery/team-task-implement/SKILL.md",
            "skills/delivery/team-task-batch-implement/SKILL.md",
        ):
            with self.subTest(skill=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                direct_rule = next(
                    line
                    for line in text.splitlines()
                    if "`contribution_model = direct`" in line
                    and "git switch" in line
                )
                switched = direct_rule.index("git switch {trunk_branch}")
                fetched = direct_rule.index("git fetch {source_remote} {trunk_branch}")
                pulled = direct_rule.index(
                    "git pull --ff-only {source_remote} {trunk_branch}"
                )

                self.assertLess(switched, fetched)
                self.assertLess(fetched, pulled)
                self.assertIn("无法 fast-forward 时停止", direct_rule)

    def test_task_implement_requires_post_verification_commit_confirmation(self) -> None:
        text = (
            ROOT / "skills/delivery/team-task-implement/SKILL.md"
        ).read_text(encoding="utf-8")

        verified = text.index("9. 验证通过后、暂存任何文件之前")
        confirmed = text.index("11. 只有用户明确选择")
        committed = text.index("12. 创建一个逻辑 commit")

        self.assertLess(verified, confirmed)
        self.assertLess(confirmed, committed)
        self.assertIn("🔍 暂不提交，我要先查看 diff", text)
        self.assertIn("🔄 继续修改当前 Task", text)
        self.assertIn("不得把用户在任务开始时说的“实现并提交”", text)
        self.assertIn("不添加 `T001` 等 Task ID", text)
        self.assertNotIn("`T001: ", text)

    def test_task_batch_requires_confirmation_for_each_task(self) -> None:
        text = (
            ROOT / "skills/delivery/team-task-batch-implement/SKILL.md"
        ).read_text(encoding="utf-8")

        previewed = text.index("8. 当前 Task 达到 `verified` 后展示")
        confirmed = text.index("10. 只有用户明确确认当前 Task 后")
        next_task = text.index("11. 当前 Task 达到 `committed` 后继续下一个")

        self.assertLess(previewed, confirmed)
        self.assertLess(confirmed, next_task)
        self.assertIn("## 逐 Task 提交确认", text)
        self.assertIn("一次确认只覆盖一个 Task 的当前实际 diff", text)
        self.assertIn("🔍 暂不提交，我要先查看 diff", text)
        self.assertIn("不添加 `T001` 等 Task ID", text)

    def test_prd_to_tasks_defaults_to_cohesive_delivery_outcomes(self) -> None:
        text = (
            ROOT / "skills/delivery/team-prd-to-tasks/SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("一个内聚、完整且值得单独交付的工程结果", text)
        self.assertIn("不是缩小 Task 的目标", text)
        self.assertIn("实现及其单元、集成和回归测试", text)
        self.assertIn("超过 6 个候选 Task", text)
        self.assertIn("不设固定减少比例", text)
        self.assertNotIn("默认目标是将 Task 数量减少约三分之一", text)

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
            self.assertIn("## 目标", plan["body"])
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
            self.assertIn("## 目标", plan["body"])
            self.assertIn(f"team-spec-slug: {SLUG}", plan["body"])

    def test_issue_language_argument_overrides_version_control_language(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_workspace(
                root,
                [("T001", "Add export path", "draft", "Pending", "None")],
            )
            result = run(
                ROOT
                / "skills/delivery/team-spec-create-issue-github/scripts/create_github_issue.py",
                "--slug",
                SLUG,
                "--repo",
                "owner/repo",
                "--language",
                "en-US",
                "--json",
                cwd=root,
            )
            plan = json.loads(result.stdout)
            self.assertIn("## Goal", plan["body"])
            self.assertNotIn("## 目标", plan["body"])

    def test_github_issue_accepts_localized_body_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            create_workspace(
                root,
                [
                    ("T001", "Add export path", "committed", "abc1234", "None"),
                    ("T002", "Add tests", "draft", "Pending", "T001"),
                ],
            )
            body_file = root / "localized-issue.md"
            write(body_file, "# Localized issue\n\nLocalized summary.\n")
            result = run(
                ROOT
                / "skills/delivery/team-spec-create-issue-github/scripts/create_github_issue.py",
                "--slug",
                SLUG,
                "--repo",
                "owner/repo",
                "--body-file",
                str(body_file),
                "--json",
                cwd=root,
            )
            plan = json.loads(result.stdout)
            self.assertIn("Localized summary.", plan["body"])
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
        self.assertIn("## 变更目的", plan["body"])

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
        self.assertIn("## 变更目的", plan["body"])

    def test_github_issue_request_sends_real_bearer_token(self) -> None:
        module = load_script_module(
            ROOT
            / "skills/delivery/team-spec-create-issue-github/scripts/create_github_issue.py"
        )
        captured: dict[str, object] = {}

        def fake_api_request(method, url, token, headers, **kwargs):
            captured["headers"] = headers
            return {}

        module.api_request = fake_api_request
        token_value = "secret-token-123"
        module.request("GET", "https://api.github.com/repos/owner/repo/issues", token_value)
        headers = captured["headers"]
        expected = "AUTH_PREFIX" + " " + token_value
        expected = expected.replace("AUTH_PREFIX", "Bearer")
        self.assertEqual(expected, headers["Authorization"])

    def test_github_pr_request_sends_real_bearer_token(self) -> None:
        module = load_script_module(
            ROOT
            / "skills/delivery/team-spec-create-pr-github/scripts/create_github_pr.py"
        )
        captured: dict[str, object] = {}

        def fake_api_request(method, url, token, headers, **kwargs):
            captured["headers"] = headers
            return {}

        module.api_request = fake_api_request
        token_value = "secret-token-456"
        module.request("GET", "https://api.github.com/repos/owner/repo/pulls", token_value)
        headers = captured["headers"]
        expected = "AUTH_PREFIX" + " " + token_value
        expected = expected.replace("AUTH_PREFIX", "Bearer")
        self.assertEqual(expected, headers["Authorization"])

    def test_gitlab_issue_request_defaults_debug_to_false(self) -> None:
        module = load_script_module(
            ROOT
            / "skills/delivery/team-spec-create-issue-gitlab/scripts/create_gitlab_issue.py"
        )
        captured: dict[str, object] = {}

        def fake_api_request(method, url, token, headers, *, payload=None, service=None, debug=False):
            captured["debug"] = debug
            return {}

        module.api_request = fake_api_request
        module.request("GET", "https://gitlab.example.com/api/v4/projects/1/issues", "token")
        self.assertFalse(captured["debug"])
        module.request("GET", "https://gitlab.example.com/api/v4/projects/1/issues", "token", debug=True)
        self.assertTrue(captured["debug"])

    def test_gitlab_mr_request_defaults_debug_to_false(self) -> None:
        module = load_script_module(
            ROOT
            / "skills/delivery/team-spec-create-mr-gitlab/scripts/create_gitlab_mr.py"
        )
        captured: dict[str, object] = {}

        def fake_api_request(method, url, token, headers, *, payload=None, service=None, debug=False):
            captured["debug"] = debug
            return {}

        module.api_request = fake_api_request
        module.request("GET", "https://gitlab.example.com/api/v4/projects/1", "token")
        self.assertFalse(captured["debug"])
        module.request("GET", "https://gitlab.example.com/api/v4/projects/1", "token", debug=True)
        self.assertTrue(captured["debug"])

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

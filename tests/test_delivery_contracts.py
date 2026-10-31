from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_spec_delivery_workflow import ROOT, SLUG, create_workspace, git, run, run_failure, write

DELIVERY = ROOT / "skills/delivery"
PREPARE = DELIVERY / "team-task-implement/scripts/prepare_spec_branch.py"


def script(kind: str, provider: str) -> Path:
    name = "pr" if provider == "github" else "mr"
    return DELIVERY / f"team-spec-create-{kind if kind == 'issue' else name}-{provider}" / "scripts" / f"create_{provider}_{kind if kind == 'issue' else name}.py"


def repo(directory: Path, provider: str = "github") -> Path:
    root = directory / "project"
    root.mkdir()
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "tests@example.invalid")
    git(root, "config", "user.name", "Tests")
    for filename in ("a", "name with spaces.txt", "中文.txt", "old.txt", "team-spec/CONTEXT.md"):
        write(root / filename, "base\n")
    git(root, "add", ".")
    git(root, "commit", "-m", "Base")
    git(root, "remote", "add", "origin", f"git@{provider}.com:team/project.git")
    git(root, "update-ref", "refs/remotes/origin/main", git(root, "rev-parse", "HEAD"))
    git(root, "switch", "-c", SLUG)
    write(root / "app.txt", "implemented\n")
    git(root, "add", "app.txt")
    git(root, "commit", "-m", "Implement behavior")
    create_workspace(root, [("T001", "Implement behavior", "committed", git(root, "rev-parse", "HEAD"), "None")])
    return root


def invoke(root: Path, kind: str, provider: str, *args: str, slug: str = SLUG):
    return run_failure(script(kind, provider), "--slug", slug, "--json", *args, cwd=root,
                       env={"GITLAB_URL": "https://gitlab.com"})


class DeliveryContractsTests(unittest.TestCase):
    def test_tracked_context_changes_are_allowed_for_both_providers(self):
        for provider in ("github", "gitlab"):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as d:
                root = repo(Path(d), provider)
                write(root / "team-spec/CONTEXT.md", "updated context\n")
                result = invoke(root, "pull", provider)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((root / "team-spec/CONTEXT.md").read_text(), "updated context\n")
                self.assertEqual(git(root, "diff", "--cached", "--name-only"), "")

    def test_code_changes_with_short_unicode_and_space_paths_are_rejected(self):
        for provider in ("github", "gitlab"):
            for filename in ("a", "中文.txt", "name with spaces.txt", "new\nfile.txt"):
                with self.subTest(provider=provider, path=filename), tempfile.TemporaryDirectory() as d:
                    root = repo(Path(d), provider)
                    write(root / filename, "changed\n")
                    result = invoke(root, "pull", provider)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Non-team-spec", result.stderr)

    def test_rename_checks_both_paths_and_staged_documents_are_rejected(self):
        for provider in ("github", "gitlab"):
            for source, target in (("old.txt", "team-spec/moved.txt"), ("team-spec/CONTEXT.md", "moved.txt"), ("team-spec/CONTEXT.md", "team-spec/renamed 文档.md")):
                with self.subTest(provider=provider, source=source, target=target), tempfile.TemporaryDirectory() as d:
                    root = repo(Path(d), provider)
                    git(root, "mv", source, target)
                    result = invoke(root, "pull", provider)
                    self.assertNotEqual(result.returncode, 0)
                    expected = "team-spec files must not be staged" if source.startswith("team-spec/") and target.startswith("team-spec/") else "Non-team-spec"
                    self.assertIn(expected, result.stderr)

    def test_status_failure_is_not_treated_as_a_clean_worktree(self):
        spec = importlib.util.spec_from_file_location("common_review", ROOT / "scripts/_team_common.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as d:
            try:
                os.chdir(d)
                with self.assertRaisesRegex(SystemExit, "Cannot inspect Git"):
                    module.git_status_entries()
            finally:
                os.chdir(previous)

    def test_technical_debt_without_prd_generates_all_four_delivery_plans(self):
        import json
        for provider in ("github", "gitlab"):
            for kind in ("issue", "pull"):
                with self.subTest(provider=provider, kind=kind), tempfile.TemporaryDirectory() as d:
                    root = repo(Path(d), provider)
                    workspace = root / "team-spec/active" / SLUG
                    (workspace / "prd/prd.md").unlink()
                    write(workspace / "spec/refine.md", "# 修复连接泄漏\n\n## 目标\n\n释放连接\n\n## 影响范围\n\n连接池\n\n## 验收口径\n\n连接数恢复\n\n## 风险\n\n超时兼容\n")
                    write(workspace / "spec/reviews.md", "## Status\n\nready\n\n## Risks\n\n回滚窗口\n")
                    debt_slug = "2026-09-22-debt-connections"
                    workspace.rename(workspace.parent / debt_slug)
                    git(root, "branch", "-m", debt_slug)
                    result = invoke(root, kind, provider, slug=debt_slug)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    plan = json.loads(result.stdout)
                    self.assertEqual(plan["spec_type"], "technical-debt")
                    self.assertTrue(plan["source_path"].endswith("spec/refine.md"))
                    for value in ("释放连接", "连接池", "连接数恢复", "超时兼容", "回滚窗口", "T001"):
                        self.assertIn(value, plan["body"])
                    self.assertFalse((workspace.parent / debt_slug / "DELIVERY.md").exists())

    def test_debt_requires_ready_review_even_with_explicit_source_type(self):
        for provider in ("github", "gitlab"):
            for kind in ("issue", "pull"):
                for state in (None, "blocked", "needs-refinement", ""):
                    with self.subTest(provider=provider, kind=kind, state=state), tempfile.TemporaryDirectory() as d:
                        root = repo(Path(d), provider)
                        workspace = root / "team-spec/active" / SLUG
                        write(workspace / "spec/refine.md", "# Debt\n")
                        if state is not None:
                            write(workspace / "spec/reviews.md", f"## Status\n\n{state}\n")
                        result = invoke(root, kind, provider, "--spec-type", "technical-debt")
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("Technical-debt review", result.stderr)

    def test_custom_branch_is_rejected_consistently(self):
        for provider in ("github", "gitlab"):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as d:
                root = repo(Path(d), provider)
                git(root, "branch", "-m", "custom-branch")
                result = invoke(root, "pull", provider)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Current branch must be", result.stderr)

    def test_preparer_copies_match_and_skills_remain_self_contained(self):
        batch = DELIVERY / "team-task-batch-implement/scripts/prepare_spec_branch.py"
        self.assertEqual(PREPARE.read_bytes(), batch.read_bytes())
        for name in ("team-task-implement", "team-task-batch-implement"):
            with tempfile.TemporaryDirectory() as d:
                copied = Path(d) / "skill"
                shutil.copytree(DELIVERY / name, copied)
                result = run(copied / "scripts/prepare_spec_branch.py", "--help", cwd=Path(d))
                self.assertIn("--execute", result.stdout)

    def test_existing_branch_accepts_documents_without_fetch_or_staging(self):
        with tempfile.TemporaryDirectory() as d:
            root = repo(Path(d))
            git(root, "switch", "main")
            write(root / "team-spec/CONTEXT.md", "local context\n")
            before = git(root, "status", "--porcelain")
            preview = run(PREPARE, "--slug", SLUG, cwd=root)
            self.assertIn('"mode": "dry-run"', preview.stdout)
            self.assertEqual(git(root, "branch", "--show-current"), "main")
            self.assertEqual(git(root, "status", "--porcelain"), before)
            run(PREPARE, "--slug", SLUG, "--execute", cwd=root)
            self.assertEqual(git(root, "branch", "--show-current"), SLUG)
            self.assertEqual((root / "team-spec/CONTEXT.md").read_text(), "local context\n")
            self.assertEqual(git(root, "diff", "--cached", "--name-only"), "")

    def test_preparer_blocks_code_on_switch_but_can_resume_attributed_task(self):
        with tempfile.TemporaryDirectory() as d:
            root = repo(Path(d))
            write(root / "a", "task changes\n")
            rejected = run_failure(PREPARE, "--slug", SLUG, cwd=root)
            self.assertNotEqual(rejected.returncode, 0)
            run(PREPARE, "--slug", SLUG, "--task-path", "a", "--execute", cwd=root)
            git(root, "switch", "main")
            rejected = run_failure(PREPARE, "--slug", SLUG, "--task-path", "a", "--execute", cwd=root)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(git(root, "branch", "--show-current"), "main")

    def test_preparer_preserves_documents_that_would_be_overwritten(self):
        for mode in ("tracked", "untracked", "ignored"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                root = repo(Path(d))
                path = "team-spec/CONTEXT.md" if mode == "tracked" else "team-spec/new.txt"
                write(root / path, "branch value\n")
                git(root, "add", path)
                git(root, "commit", "-m", "Branch document")
                git(root, "switch", "main")
                if mode == "ignored":
                    write(root / ".git/info/exclude", "team-spec/new.txt\n")
                write(root / path, "local value\n")
                result = run_failure(PREPARE, "--slug", SLUG, "--execute", cwd=root)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((root / path).read_text(), "local value\n")
                self.assertEqual(git(root, "branch", "--show-current"), "main")

    def test_new_branch_fast_forwards_trunk_with_document_changes(self):
        for model in ("direct", "fork-pull"):
            with self.subTest(model=model), tempfile.TemporaryDirectory() as d:
                root = repo(Path(d))
                git(root, "switch", "main")
                remote = Path(d) / "upstream.git"
                git(root, "clone", "--bare", str(root), str(remote))
                git(root, "remote", "set-url", "origin", str(remote))
                if model == "fork-pull":
                    git(root, "remote", "add", "upstream", str(remote))
                clone = Path(d) / "other"
                git(root, "clone", str(remote), str(clone))
                git(clone, "config", "user.email", "tests@example.invalid")
                git(clone, "config", "user.name", "Tests")
                write(clone / "upstream.txt", "upstream\n")
                git(clone, "add", "upstream.txt")
                git(clone, "commit", "-m", "Advance trunk")
                git(clone, "push", "origin", "main")
                expected = git(clone, "rev-parse", "HEAD")
                slug = "2026-09-22-new-spec"
                (root / "team-spec/active" / slug).mkdir()
                write(root / "team-spec/CONTEXT.md", "local context\n")
                args = ("--slug", slug, "--trunk-branch", "main", "--contribution-model", model,
                        "--source-remote", "origin", "--target-remote", "upstream")
                run(PREPARE, *args, cwd=root)
                self.assertFalse((root / "upstream.txt").exists())
                run(PREPARE, *args, "--execute", cwd=root)
                self.assertEqual(git(root, "branch", "--show-current"), slug)
                self.assertEqual(git(root, "rev-parse", "HEAD"), expected)
                self.assertEqual((root / "team-spec/CONTEXT.md").read_text(), "local context\n")
                self.assertEqual(git(root, "diff", "--cached", "--name-only"), "")

    def test_product_source_and_explicit_legacy_debt_source_stay_distinct(self):
        import json
        for provider in ("github", "gitlab"):
            for kind in ("issue", "pull"):
                with self.subTest(provider=provider, kind=kind), tempfile.TemporaryDirectory() as d:
                    root = repo(Path(d), provider)
                    workspace = root / "team-spec/active" / SLUG
                    write(workspace / "spec/refine.md", "# Legacy debt\n\n## Goal\n\nDebt-only goal\n")
                    write(workspace / "spec/reviews.md", "Status: ready\n")
                    product = invoke(root, kind, provider)
                    self.assertEqual(product.returncode, 0, product.stderr)
                    product_plan = json.loads(product.stdout)
                    self.assertEqual(product_plan["spec_type"], "product")
                    self.assertIn("Export only rows", product_plan["body"])
                    self.assertNotIn("Debt-only goal", product_plan["body"])
                    debt = invoke(root, kind, provider, "--spec-type", "technical-debt")
                    self.assertEqual(debt.returncode, 0, debt.stderr)
                    self.assertIn("Debt-only goal", json.loads(debt.stdout)["body"])
                    write(workspace / "spec/reviews.md", "Status: blocked\n\n## Status\n\nready\n")
                    conflict = invoke(root, kind, provider, "--spec-type", "technical-debt")
                    self.assertNotEqual(conflict.returncode, 0)
                    self.assertIn("Conflicting", conflict.stderr)

    def test_preparer_rejects_staged_documents_without_unstaging(self):
        with tempfile.TemporaryDirectory() as d:
            root = repo(Path(d))
            write(root / "team-spec/CONTEXT.md", "staged context\n")
            git(root, "add", "team-spec/CONTEXT.md")
            before = git(root, "diff", "--cached")
            result = run_failure(PREPARE, "--slug", SLUG, "--execute", cwd=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must remain unstaged", result.stderr)
            self.assertEqual(git(root, "diff", "--cached"), before)

    def test_new_branch_refuses_divergence_and_document_overwrites(self):
        for scenario in ("ahead", "diverged", "document-conflict"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as d:
                root = repo(Path(d))
                git(root, "switch", "main")
                remote = Path(d) / "upstream.git"
                git(root, "clone", "--bare", str(root), str(remote))
                git(root, "remote", "set-url", "origin", str(remote))
                clone = Path(d) / "other"
                git(root, "clone", str(remote), str(clone))
                git(clone, "config", "user.email", "tests@example.invalid")
                git(clone, "config", "user.name", "Tests")
                if scenario != "ahead":
                    write(clone / "team-spec/CONTEXT.md", "upstream context\n")
                    git(clone, "add", "team-spec/CONTEXT.md")
                    git(clone, "commit", "-m", "Upstream context")
                    git(clone, "push", "origin", "main")
                if scenario != "document-conflict":
                    write(root / "local.txt", "local commit\n")
                    git(root, "add", "local.txt")
                    git(root, "commit", "-m", "Local trunk change")
                slug = "2026-09-22-new-spec"
                (root / "team-spec/active" / slug).mkdir()
                write(root / "team-spec/CONTEXT.md", "local context\n")
                before = git(root, "rev-parse", "HEAD")
                result = run_failure(PREPARE, "--slug", slug, "--trunk-branch", "main",
                                     "--contribution-model", "direct", "--source-remote", "origin", "--execute", cwd=root)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual((root / "team-spec/CONTEXT.md").read_text(), "local context\n")
                self.assertEqual(git(root, "rev-parse", "HEAD"), before)
                self.assertEqual(git(root, "branch", "--show-current"), "main")
                self.assertNotIn(slug, git(root, "branch", "--list", slug))
                self.assertEqual(git(root, "stash", "list"), "")
                self.assertEqual(git(root, "diff", "--cached", "--name-only"), "")


if __name__ == "__main__":
    unittest.main()

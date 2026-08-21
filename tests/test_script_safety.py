from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


TEAM_COMMON = load_module("team_common_for_tests", ROOT / "scripts" / "_team_common.py")
SCANNER = load_module(
    "scan_codebase_for_tests",
    ROOT
    / "skills"
    / "codebase"
    / "team-codebase-onboarding"
    / "scripts"
    / "scan_codebase.py",
)
ARCHIVER = load_module(
    "archive_team_spec_for_tests",
    ROOT
    / "skills"
    / "product"
    / "team-spec-archive"
    / "scripts"
    / "archive_team_spec.py",
)
SLUG = "2026-08-21-archive-safety"


class ScriptSafetyTests(unittest.TestCase):
    def test_request_debug_reports_shape_without_payload_content(self) -> None:
        output = io.StringIO()
        with redirect_stderr(output):
            TEAM_COMMON.print_request_debug(
                "GitLab",
                "POST",
                "https://gitlab.example.com/api/v4/projects/example/issues",
                {
                    "title": "Internal launch plan",
                    "description": "customer-secret-content",
                    "labels": ["private-roadmap"],
                    "milestone_id": 7,
                },
            )

        debug_text = output.getvalue()
        self.assertNotIn("Internal launch plan", debug_text)
        self.assertNotIn("customer-secret-content", debug_text)
        self.assertNotIn("private-roadmap", debug_text)
        self.assertIn("<redacted string:", debug_text)
        self.assertIn('"milestone_id": 7', debug_text)

    def test_scanner_stops_after_file_limit_with_one_warning(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index in range(5):
                path = root / f"module-{index}" / "source.py"
                path.parent.mkdir(parents=True)
                path.write_text(f"VALUE = {index}\n", encoding="utf-8")

            summary = SCANNER.scan_repo(
                SimpleNamespace(
                    repo_path=str(root),
                    exclude=[],
                    max_files=1,
                    max_content_bytes=2_000_000,
                    important_limit=2000,
                    marker_limit=500,
                    git_log_limit=20,
                    git_churn_days=90,
                    git_churn_limit=50,
                    skip_git=True,
                )
            )

        limit_warnings = [
            item
            for item in summary["unknowns"]
            if item.get("item") == "file-scan-limit"
        ]
        self.assertEqual(1, summary["repo_size"]["files"])
        self.assertEqual(1, len(limit_warnings))
        self.assertLess(summary["repo_size"]["directories"], 6)

    def test_todo_markers_do_not_echo_line_prefix_or_secret_values(self) -> None:
        markers = SCANNER.extract_todo_markers(
            "API_TOKEN=super-secret # TODO rotate value later\n"
            "# FIXME password=hunter2 before release\n"
            "# TODO Authorization: Bearer opaque-access-token\n"
            "# HACK token is natural-language-secret\n"
            '# XXX password="hunter 2" before release\n'
            "# FIXME OPENAI_API_KEY=provider-secret\n"
            "# FIXME AWS_SECRET_ACCESS_KEY=aws-secret-value\n"
            "# HACK GITHUB_TOKEN=github-secret-value\n"
            "# XXX clientSecret=camel-secret-value\n"
            "# TODO update tokenizer model\n",
            ".env",
            10,
        )

        rendered = "\n".join(item["text"] for item in markers)
        self.assertNotIn("super-secret", rendered)
        self.assertNotIn("hunter2", rendered)
        self.assertNotIn("API_TOKEN", rendered)
        self.assertNotIn("opaque-access-token", rendered)
        self.assertNotIn("natural-language-secret", rendered)
        self.assertNotIn("hunter 2", rendered)
        self.assertNotIn("provider-secret", rendered)
        self.assertNotIn("aws-secret-value", rendered)
        self.assertNotIn("github-secret-value", rendered)
        self.assertNotIn("camel-secret-value", rendered)
        self.assertIn("TODO: rotate value later", rendered)
        self.assertIn("TODO: update tokenizer model", rendered)
        self.assertEqual(8, rendered.count("[REDACTED: sensitive content]"))

    def test_archive_workspace_is_staged_before_becoming_visible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            team_spec = Path(directory) / "team-spec"
            source = team_spec / "active" / SLUG / "spec" / "refine.md"
            source.parent.mkdir(parents=True)
            source.write_text("# Refine\n", encoding="utf-8")

            archive = team_spec / "archive" / SLUG
            plan = ARCHIVER.build_plan(team_spec, SLUG)
            record = ARCHIVER.execute_plan(SLUG, "completed", plan, archive)

            self.assertFalse((team_spec / "active" / SLUG).exists())
            self.assertEqual("# Refine\n", (archive / "spec" / "refine.md").read_text())
            self.assertNotIn("Status: archived", record.read_text(encoding="utf-8"))
            self.assertFalse(
                (team_spec / "archive" / f".{SLUG}.archive-tmp").exists()
            )
            self.assertFalse(ARCHIVER.transaction_path(archive).exists())

    def test_interrupted_archive_is_detected_and_restored_from_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            team_spec = Path(directory) / "team-spec"
            source = team_spec / "active" / SLUG / "spec" / "refine.md"
            source.parent.mkdir(parents=True)
            source.write_text("# Refine\n", encoding="utf-8")

            archive = team_spec / "archive" / SLUG
            archive.parent.mkdir(parents=True)
            plan = ARCHIVER.build_plan(team_spec, SLUG)
            ARCHIVER.write_transaction(SLUG, "completed", plan, archive)
            staging = ARCHIVER.staging_dir(archive)
            ARCHIVER.shutil.move(str(team_spec / "active" / SLUG), str(staging))
            (staging / "ARCHIVE.md").write_text("partial record\n", encoding="utf-8")

            self.assertIn(SLUG, ARCHIVER.discover_incomplete_slugs(team_spec))
            result = ARCHIVER.recover_transaction(SLUG, archive)

            self.assertEqual("restored", result["status"])
            self.assertEqual(1, result["restored_moves"])
            self.assertEqual("# Refine\n", source.read_text(encoding="utf-8"))
            self.assertFalse(staging.exists())
            self.assertFalse(ARCHIVER.transaction_path(archive).exists())
            self.assertFalse(archive.exists())

    def test_staging_without_transaction_metadata_is_never_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            team_spec = Path(directory) / "team-spec"
            archive = team_spec / "archive" / SLUG
            staging = ARCHIVER.staging_dir(archive)
            staging.mkdir(parents=True)
            evidence = staging / "spec" / "refine.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("# Preserve me\n", encoding="utf-8")

            self.assertIn(SLUG, ARCHIVER.discover_incomplete_slugs(team_spec))
            with self.assertRaisesRegex(SystemExit, "without transaction metadata"):
                ARCHIVER.recover_transaction(SLUG, archive)

            self.assertEqual("# Preserve me\n", evidence.read_text(encoding="utf-8"))

    def test_archive_legacy_moves_roll_back_after_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            team_spec = Path(directory) / "team-spec"
            refine = team_spec / "active" / "spec" / "refine" / f"{SLUG}.md"
            prd = team_spec / "active" / "prd" / f"{SLUG}.md"
            refine.parent.mkdir(parents=True)
            prd.parent.mkdir(parents=True)
            refine.write_text("# Refine\n", encoding="utf-8")
            prd.write_text("# PRD\n", encoding="utf-8")

            archive = team_spec / "archive" / SLUG
            plan = ARCHIVER.build_plan(team_spec, SLUG)
            real_move = ARCHIVER.shutil.move
            calls = 0

            def fail_second_move(source: str, target: str):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated move failure")
                return real_move(source, target)

            with mock.patch.object(
                ARCHIVER.shutil, "move", side_effect=fail_second_move
            ):
                with self.assertRaisesRegex(OSError, "simulated move failure"):
                    ARCHIVER.execute_plan(SLUG, "manual", plan, archive)

            self.assertTrue(refine.exists())
            self.assertTrue(prd.exists())
            self.assertFalse(archive.exists())
            self.assertFalse(
                (team_spec / "archive" / f".{SLUG}.archive-tmp").exists()
            )
            self.assertFalse(ARCHIVER.transaction_path(archive).exists())

    def test_archive_restores_move_that_completed_before_raising(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            team_spec = Path(directory) / "team-spec"
            source = team_spec / "active" / SLUG / "spec" / "refine.md"
            source.parent.mkdir(parents=True)
            source.write_text("# Refine\n", encoding="utf-8")

            archive = team_spec / "archive" / SLUG
            plan = ARCHIVER.build_plan(team_spec, SLUG)
            real_move = ARCHIVER.shutil.move
            calls = 0

            def move_then_fail_once(source_path: str, target_path: str):
                nonlocal calls
                calls += 1
                result = real_move(source_path, target_path)
                if calls == 1:
                    raise OSError("simulated post-move failure")
                return result

            with mock.patch.object(
                ARCHIVER.shutil, "move", side_effect=move_then_fail_once
            ):
                with self.assertRaisesRegex(OSError, "simulated post-move failure"):
                    ARCHIVER.execute_plan(SLUG, "manual", plan, archive)

            self.assertEqual("# Refine\n", source.read_text(encoding="utf-8"))
            self.assertFalse(archive.exists())
            self.assertFalse(ARCHIVER.staging_dir(archive).exists())
            self.assertFalse(ARCHIVER.transaction_path(archive).exists())

    def test_archive_treats_published_rename_as_success_if_call_then_raises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            team_spec = Path(directory) / "team-spec"
            source = team_spec / "active" / SLUG / "spec" / "refine.md"
            source.parent.mkdir(parents=True)
            source.write_text("# Refine\n", encoding="utf-8")

            archive = team_spec / "archive" / SLUG
            plan = ARCHIVER.build_plan(team_spec, SLUG)
            real_rename = Path.rename

            def rename_then_fail(path: Path, target: Path):
                result = real_rename(path, target)
                raise OSError("simulated post-rename failure")

            with mock.patch.object(ARCHIVER.Path, "rename", new=rename_then_fail):
                record = ARCHIVER.execute_plan(SLUG, "completed", plan, archive)

            self.assertEqual(archive / "ARCHIVE.md", record)
            self.assertEqual("# Refine\n", (archive / "spec" / "refine.md").read_text())
            self.assertFalse(source.exists())
            self.assertFalse(ARCHIVER.staging_dir(archive).exists())
            self.assertFalse(ARCHIVER.transaction_path(archive).exists())


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SLUG_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[A-Za-z0-9][A-Za-z0-9-]*$")
REASONS = {"completed", "abandoned", "superseded", "paused", "manual"}
TRANSACTION_VERSION = 1


@dataclass(frozen=True)
class MovePlan:
    source: Path
    target: Path
    kind: str


def absolute_path(path: Path) -> Path:
    return Path(os.path.abspath(path))


def active_dir(team_spec_dir: Path) -> Path:
    return team_spec_dir / "active"


def active_workspace_dir(team_spec_dir: Path, slug: str) -> Path:
    return active_dir(team_spec_dir) / slug


def archive_dir(team_spec_dir: Path, slug: str) -> Path:
    return team_spec_dir / "archive" / slug


def staging_dir(archive: Path) -> Path:
    return archive.parent / f".{archive.name}.archive-tmp"


def transaction_path(archive: Path) -> Path:
    return archive.parent / f".{archive.name}.archive-transaction.json"


def discover_incomplete_slugs(team_spec_dir: Path) -> set[str]:
    archive_root = team_spec_dir / "archive"
    if not archive_root.exists():
        return set()

    slugs: set[str] = set()
    suffixes = (".archive-tmp", ".archive-transaction.json")
    for path in archive_root.iterdir():
        if not path.name.startswith("."):
            continue
        for suffix in suffixes:
            if not path.name.endswith(suffix):
                continue
            slug = path.name[1 : -len(suffix)]
            if SLUG_RE.match(slug):
                slugs.add(slug)
            break
    return slugs


def discover_slugs(team_spec_dir: Path) -> set[str]:
    active = active_dir(team_spec_dir)
    slugs: set[str] = set()
    if active.exists():
        slugs.update(path.name for path in active.iterdir() if path.is_dir() and SLUG_RE.match(path.name))

    candidates: list[Path] = []
    candidates.extend((active / "spec" / "refine").glob("*.md"))
    candidates.extend((active / "spec" / "reviews").glob("*.md"))
    candidates.extend((active / "prd").glob("*.md"))
    candidates.extend((active / "design").glob("*.md"))
    candidates.extend(path for path in (active / "issues").glob("*") if path.is_dir())

    for path in candidates:
        name = path.stem if path.is_file() else path.name
        if name.endswith("-alignment"):
            name = name.removesuffix("-alignment")
        if SLUG_RE.match(name):
            slugs.add(name)
    return slugs


def resolve_slug(team_spec_dir: Path, slug: str | None) -> str:
    if slug:
        if not SLUG_RE.match(slug):
            raise SystemExit(f"Invalid slug: {slug}")
        return slug

    slugs = discover_slugs(team_spec_dir)
    if len(slugs) == 1:
        return next(iter(slugs))
    if not slugs:
        raise SystemExit("Cannot infer slug: no active slug was found.")
    raise SystemExit("Cannot infer slug: multiple active slugs found: " + ", ".join(sorted(slugs)))


def build_plan(team_spec_dir: Path, slug: str) -> list[MovePlan]:
    active = active_dir(team_spec_dir)
    archive = archive_dir(team_spec_dir, slug)
    workspace = active_workspace_dir(team_spec_dir, slug)
    if workspace.exists():
        return [MovePlan(workspace, archive, "workspace")]

    candidates = [
        MovePlan(active / "spec" / "refine" / f"{slug}.md", archive / "spec" / "refine.md", "file"),
        MovePlan(active / "spec" / "reviews" / f"{slug}.md", archive / "spec" / "reviews.md", "file"),
        MovePlan(active / "prd" / f"{slug}.md", archive / "prd" / "prd.md", "file"),
        MovePlan(active / "prd" / f"{slug}-alignment.md", archive / "prd" / "brief.md", "file"),
        MovePlan(active / "issues" / slug, archive / "issues", "directory"),
        MovePlan(active / "design" / f"{slug}.md", archive / "design" / "functional-design.md", "file"),
    ]
    return [item for item in candidates if item.source.exists()]


def render_archive_record(slug: str, reason: str, plan: list[MovePlan]) -> str:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        f"# Archive: {slug}",
        "",
        f"Archived-At: {timestamp}",
        f"Reason: {reason}",
        "",
        "## Moved Files",
        "",
    ]
    for item in plan:
        lines.append(f"- `{item.source.as_posix()}` -> `{item.target.as_posix()}`")
    lines.append("")
    return "\n".join(lines)


def staged_target(item: MovePlan, archive: Path, staging: Path) -> Path:
    if item.kind == "workspace":
        return staging
    return staging / item.target.relative_to(archive)


def write_transaction(
    slug: str,
    reason: str,
    plan: list[MovePlan],
    archive: Path,
) -> Path:
    staging = staging_dir(archive)
    transaction = transaction_path(archive)
    payload = {
        "version": TRANSACTION_VERSION,
        "slug": slug,
        "reason": reason,
        "archive": str(absolute_path(archive)),
        "staging": str(absolute_path(staging)),
        "moves": [
            {
                "source": str(absolute_path(item.source)),
                "staged_target": str(
                    absolute_path(staged_target(item, archive, staging))
                ),
                "kind": item.kind,
            }
            for item in plan
        ],
    }
    with transaction.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    return transaction


def load_transaction(slug: str, archive: Path) -> list[tuple[Path, Path]]:
    transaction = transaction_path(archive)
    try:
        payload = json.loads(transaction.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(
            f"Cannot read archive transaction metadata: {transaction}: {error}"
        ) from error

    if payload.get("version") != TRANSACTION_VERSION or payload.get("slug") != slug:
        raise SystemExit(f"Invalid archive transaction metadata: {transaction}")

    expected_archive = absolute_path(archive)
    expected_staging = absolute_path(staging_dir(archive))
    if absolute_path(Path(str(payload.get("archive", "")))) != expected_archive:
        raise SystemExit(f"Archive transaction target mismatch: {transaction}")
    if absolute_path(Path(str(payload.get("staging", "")))) != expected_staging:
        raise SystemExit(f"Archive transaction staging mismatch: {transaction}")

    active_root = absolute_path(archive.parent.parent / "active")
    raw_moves = payload.get("moves")
    if not isinstance(raw_moves, list) or not raw_moves:
        raise SystemExit(f"Archive transaction has no moves: {transaction}")

    moves: list[tuple[Path, Path]] = []
    for raw_move in raw_moves:
        if not isinstance(raw_move, dict):
            raise SystemExit(f"Invalid archive transaction move: {transaction}")
        source = absolute_path(Path(str(raw_move.get("source", ""))))
        target = absolute_path(Path(str(raw_move.get("staged_target", ""))))
        if not source.is_relative_to(active_root):
            raise SystemExit(
                f"Archive recovery source is outside active/: {source}"
            )
        if target != expected_staging and not target.is_relative_to(expected_staging):
            raise SystemExit(
                f"Archive recovery target is outside staging: {target}"
            )
        moves.append((source, target))
    return moves


def recover_transaction(slug: str, archive: Path) -> dict[str, Any]:
    staging = staging_dir(archive)
    transaction = transaction_path(archive)

    if archive.exists():
        if staging.exists():
            raise SystemExit(
                f"Both final archive and staging exist; inspect manually: {archive}, {staging}"
            )
        if not transaction.exists():
            raise SystemExit(f"No incomplete archive transaction found for slug: {slug}")
        if not (archive / "ARCHIVE.md").exists():
            raise SystemExit(
                f"Final archive exists without ARCHIVE.md; inspect manually: {archive}"
            )
        transaction.unlink()
        return {
            "slug": slug,
            "status": "completed-cleanup",
            "archive": str(archive),
            "restored_moves": 0,
        }

    if not transaction.exists():
        if staging.exists():
            raise SystemExit(
                "Archive staging exists without transaction metadata; inspect it manually "
                f"and do not delete it: {staging}"
            )
        raise SystemExit(f"No incomplete archive transaction found for slug: {slug}")

    moves = load_transaction(slug, archive)
    for source, target in moves:
        if source.exists() and target.exists():
            raise SystemExit(
                f"Archive recovery is ambiguous because both paths exist: {source}, {target}"
            )
        if not source.exists() and not target.exists():
            raise SystemExit(
                f"Archive recovery cannot find either path: {source}, {target}"
            )

    staged_record = staging / "ARCHIVE.md"
    if staged_record.exists():
        staged_record.unlink()

    restored = 0
    for source, target in reversed(moves):
        if not target.exists():
            continue
        source.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(target), str(source))
        restored += 1

    if staging.exists():
        remaining = [
            path for path in staging.rglob("*") if path.is_file() or path.is_symlink()
        ]
        if remaining:
            raise SystemExit(
                "Archive recovery left untracked files in staging; inspect manually: "
                + ", ".join(str(path) for path in remaining)
            )
        shutil.rmtree(staging)
    transaction.unlink()
    return {
        "slug": slug,
        "status": "restored",
        "archive": str(archive),
        "restored_moves": restored,
    }


def execute_plan(slug: str, reason: str, plan: list[MovePlan], archive: Path) -> Path:
    archive.parent.mkdir(parents=True, exist_ok=True)
    staging = staging_dir(archive)
    transaction = transaction_path(archive)
    if staging.exists():
        raise SystemExit(f"Archive staging path already exists: {staging}")
    if transaction.exists():
        raise SystemExit(f"Archive transaction already exists: {transaction}")

    write_transaction(slug, reason, plan, archive)
    try:
        if len(plan) == 1 and plan[0].kind == "workspace":
            source = plan[0].source
            shutil.move(str(source), str(staging))
        else:
            staging.mkdir(parents=True, exist_ok=False)
            for item in plan:
                relative_target = item.target.relative_to(archive)
                staged_target = staging / relative_target
                staged_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(item.source), str(staged_target))

        staged_record = staging / "ARCHIVE.md"
        staged_record.write_text(
            render_archive_record(slug, reason, plan), encoding="utf-8"
        )
        staging.rename(archive)
    except BaseException:
        try:
            recovery = recover_transaction(slug, archive)
        except BaseException as rollback_error:
            raise RuntimeError(
                "Archive rollback could not prove a safe restore; keep the transaction "
                "and staging, inspect both paths, then run "
                f"--slug {slug} --recover-staging"
            ) from rollback_error
        if recovery["status"] == "completed-cleanup":
            return archive / "ARCHIVE.md"
        raise

    try:
        transaction.unlink()
    except OSError:
        # The archive is already complete. A later --recover-staging invocation
        # can safely remove this transaction marker after checking ARCHIVE.md.
        pass
    return archive / "ARCHIVE.md"


def result_dict(slug: str, reason: str, execute: bool, plan: list[MovePlan], record_path: Path) -> dict[str, Any]:
    return {
        "slug": slug,
        "reason": reason,
        "execute": execute,
        "archive_record": str(record_path),
        "moves": [
            {"source": str(item.source), "target": str(item.target), "kind": item.kind}
            for item in plan
        ],
    }


def print_text(result: dict[str, Any]) -> None:
    mode = "execute" if result["execute"] else "dry-run"
    print(f"Mode: {mode}")
    print(f"Slug: {result['slug']}")
    print(f"Reason: {result['reason']}")
    print(f"Archive record: {result['archive_record']}")
    print("Moves:")
    for item in result["moves"]:
        print(f"- {item['source']} -> {item['target']}")


def print_recovery(result: dict[str, Any]) -> None:
    print(f"Recovery status: {result['status']}")
    print(f"Slug: {result['slug']}")
    print(f"Archive: {result['archive']}")
    print(f"Restored moves: {result['restored_moves']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive one active team-spec slug.")
    parser.add_argument("--team-spec-dir", default="team-spec", help="Path to the target project's team-spec directory.")
    parser.add_argument("--slug", help="Requirement slug to archive. If omitted, infer only when unique.")
    parser.add_argument("--reason", default="manual", choices=sorted(REASONS), help="Archive reason.")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--execute", action="store_true", help="Move files. Omit for dry-run.")
    action.add_argument(
        "--recover-staging",
        action="store_true",
        help="Restore an interrupted transaction to active/. Requires --slug.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    team_spec_dir = Path(args.team_spec_dir)

    if args.recover_staging:
        if not args.slug:
            raise SystemExit("--recover-staging requires an explicit --slug.")
        slug = resolve_slug(team_spec_dir, args.slug)
        result = recover_transaction(slug, archive_dir(team_spec_dir, slug))
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_recovery(result)
        return

    incomplete_slugs = discover_incomplete_slugs(team_spec_dir)
    if args.slug and args.slug in incomplete_slugs:
        raise SystemExit(
            f"Incomplete archive transaction found for {args.slug}; run with "
            f"--slug {args.slug} --recover-staging before archiving again."
        )
    if not args.slug and incomplete_slugs:
        raise SystemExit(
            "Incomplete archive transaction(s) found: "
            + ", ".join(sorted(incomplete_slugs))
            + ". Recover each with explicit --slug and --recover-staging."
        )

    slug = resolve_slug(team_spec_dir, args.slug)
    archive = archive_dir(team_spec_dir, slug)

    if archive.exists():
        raise SystemExit(f"Archive already exists: {archive}")

    plan = build_plan(team_spec_dir, slug)
    if not plan:
        raise SystemExit(f"No active artifacts found for slug: {slug}")

    record_path = archive / "ARCHIVE.md"
    if args.execute:
        record_path = execute_plan(slug, args.reason, plan, archive)

    result = result_dict(slug, args.reason, args.execute, plan, record_path)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_text(result)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SLUG_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[A-Za-z0-9][A-Za-z0-9-]*$")
REASONS = {"completed", "abandoned", "superseded", "paused", "manual"}


@dataclass(frozen=True)
class MovePlan:
    source: Path
    target: Path
    kind: str


def active_dir(team_spec_dir: Path) -> Path:
    return team_spec_dir / "active"


def archive_dir(team_spec_dir: Path, slug: str) -> Path:
    return team_spec_dir / "archive" / slug


def discover_slugs(team_spec_dir: Path) -> set[str]:
    active = active_dir(team_spec_dir)
    slugs: set[str] = set()
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
    candidates = [
        MovePlan(active / "spec" / "refine" / f"{slug}.md", archive / "spec" / "refine" / f"{slug}.md", "file"),
        MovePlan(active / "spec" / "reviews" / f"{slug}.md", archive / "spec" / "reviews" / f"{slug}.md", "file"),
        MovePlan(active / "prd" / f"{slug}.md", archive / "prd" / f"{slug}.md", "file"),
        MovePlan(active / "prd" / f"{slug}-alignment.md", archive / "prd" / f"{slug}-alignment.md", "file"),
        MovePlan(active / "issues" / slug, archive / "issues", "directory"),
        MovePlan(active / "design" / f"{slug}.md", archive / "design" / f"{slug}.md", "file"),
    ]
    return [item for item in candidates if item.source.exists()]


def render_archive_record(slug: str, reason: str, plan: list[MovePlan]) -> str:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        f"# Archive: {slug}",
        "",
        f"Archived-At: {timestamp}",
        f"Reason: {reason}",
        "Status: archived",
        "",
        "## Moved Files",
        "",
    ]
    for item in plan:
        lines.append(f"- `{item.source.as_posix()}` -> `{item.target.as_posix()}`")
    lines.append("")
    return "\n".join(lines)


def execute_plan(slug: str, reason: str, plan: list[MovePlan], archive: Path) -> Path:
    archive.mkdir(parents=True, exist_ok=False)
    for item in plan:
        item.target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(item.source), str(item.target))
    record_path = archive / "ARCHIVE.md"
    record_path.write_text(render_archive_record(slug, reason, plan), encoding="utf-8")
    return record_path


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive one active team-spec slug.")
    parser.add_argument("--team-spec-dir", default="team-spec", help="Path to the target project's team-spec directory.")
    parser.add_argument("--slug", help="Requirement slug to archive. If omitted, infer only when unique.")
    parser.add_argument("--reason", default="manual", choices=sorted(REASONS), help="Archive reason.")
    parser.add_argument("--execute", action="store_true", help="Move files. Omit for dry-run.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    team_spec_dir = Path(args.team_spec_dir)
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

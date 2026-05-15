#!/usr/bin/env python3
"""Synchronize vendored _team_common.py files in skill script directories."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "_team_common.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check and synchronize vendored _team_common.py copies."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only report inconsistent copies. Do not overwrite.",
    )
    parser.add_argument(
        "--create-missing",
        action="store_true",
        help="Create _team_common.py in every skill scripts directory that does not have one.",
    )
    return parser.parse_args()


def skill_script_dirs() -> list[Path]:
    return sorted(
        path
        for path in (ROOT / "skills").glob("*/*/scripts")
        if path.is_dir()
    )


def vendored_paths(create_missing: bool) -> list[Path]:
    paths: list[Path] = []
    for scripts_dir in skill_script_dirs():
        target = scripts_dir / "_team_common.py"
        if target.exists() or create_missing:
            paths.append(target)
    return paths


def sync_target(source: Path, target: Path, *, check: bool) -> bool:
    if target.exists() and filecmp.cmp(source, target, shallow=False):
        return False
    if check:
        return True
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return True


def main() -> int:
    args = parse_args()
    if not SOURCE.exists():
        print(f"missing source: {SOURCE}", file=sys.stderr)
        return 2

    changed: list[Path] = []
    for target in vendored_paths(args.create_missing):
        if target == SOURCE:
            continue
        if sync_target(SOURCE, target, check=args.check):
            changed.append(target)

    if args.check and changed:
        print("Vendored _team_common.py is out of sync:")
        for path in changed:
            print(f"- {path.relative_to(ROOT)}")
        return 1

    if changed:
        print("Synchronized vendored _team_common.py:")
        for path in changed:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("All vendored _team_common.py files are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

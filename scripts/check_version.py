#!/usr/bin/env python3
"""Check release metadata; --sync updates skill versions from VERSION."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from check_skills import parse_frontmatter


ROOT = Path(__file__).resolve().parents[1]
VERSION_PATTERN = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"


def check_release(root: Path, *, sync: bool = False, tag: str | None = None) -> list[str]:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(VERSION_PATTERN, version):
        return ["VERSION must contain a major.minor.patch version without leading zeros"]
    errors = []
    if tag is not None and tag != f"v{version}":
        errors.append(f"tag {tag!r} must equal v{version}")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    if not re.search(rf"^## \[{re.escape(version)}\](?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?$", changelog, re.M):
        errors.append(f"CHANGELOG.md is missing ## [{version}]")
    updates = []
    paths = sorted((root / "skills").glob("*/*/SKILL.md"))
    if not paths:
        errors.append("no skill files found")
    for path in paths:
        data, parse_errors = parse_frontmatter(path)
        metadata = data.get("metadata")
        if parse_errors or not isinstance(metadata, dict) or "version" not in metadata:
            errors.append(f"{path.relative_to(root)}: missing or invalid metadata.version")
            continue
        if metadata["version"] == version:
            continue
        if not sync:
            errors.append(f"{path.relative_to(root)}: metadata.version must equal {version}")
            continue
        text = path.read_text(encoding="utf-8")
        front, body = text[4:].split("\n---\n", 1)
        front, count = re.subn(r'^  version:.*$', f'  version: "{version}"', front, flags=re.M)
        if count != 1:
            errors.append(f"{path.relative_to(root)}: expected exactly one version field")
        else:
            updates.append((path, f"---\n{front}\n---\n{body}"))
    if not errors:
        for path, text in updates:
            path.write_text(text, encoding="utf-8")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sync", action="store_true", help="Write skill versions; default is read-only")
    parser.add_argument("--tag", help="Require this release tag to match VERSION")
    args = parser.parse_args()
    try:
        errors = check_release(ROOT, sync=args.sync, tag=args.tag)
    except (OSError, ValueError) as error:
        errors = [str(error)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("OK: release metadata is consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

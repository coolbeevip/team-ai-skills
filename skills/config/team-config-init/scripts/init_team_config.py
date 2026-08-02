#!/usr/bin/env python3
"""Safely create or incrementally complete team-spec/config.yml."""

from __future__ import annotations

import argparse
import difflib
import json
import re
from pathlib import Path
from typing import Any


TOP_LEVEL_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s*(.*?))?\s*$")
CHILD_RE = re.compile(r"^  ([A-Za-z0-9_-]+):(?:\s*(.*?))?\s*$")
SCOPE_CHOICES = ("basic", "version-control", "access-policy", "writing-style", "all")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or incrementally complete team-spec/config.yml."
    )
    parser.add_argument("--path", default="team-spec/config.yml")
    parser.add_argument("--language")
    parser.add_argument("--version-control-language")
    parser.add_argument("--system")
    parser.add_argument("--trunk-branch")
    parser.add_argument("--contribution-model")
    parser.add_argument("--source-remote")
    parser.add_argument("--target-remote")
    parser.add_argument("--access-mode")
    parser.add_argument("--directory-file")
    parser.add_argument("--user-file-template")
    parser.add_argument("--writing-style-guide")
    parser.add_argument(
        "--scope",
        action="append",
        choices=SCOPE_CHOICES,
        help=(
            "Validation scope. Repeat for multiple scopes; use 'all' for the standalone "
            "project baseline check. Defaults to 'basic'."
        ),
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def split_scalar_comment(raw: str) -> tuple[str, str]:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(raw):
        if escaped:
            escaped = False
            continue
        if quote == '"' and character == "\\":
            escaped = True
            continue
        if character in {'"', "'"}:
            if quote == character:
                quote = None
            elif quote is None:
                quote = character
            continue
        if character == "#" and quote is None and (
            index == 0 or raw[index - 1].isspace()
        ):
            return raw[:index].rstrip(), " " + raw[index:].strip()
    return raw.strip(), ""


def scalar_value(raw: str) -> str:
    value, _ = split_scalar_comment(raw)
    if value.startswith(('"', "'")):
        try:
            parsed = json.loads(value) if value.startswith('"') else value[1:-1]
            return str(parsed)
        except (json.JSONDecodeError, IndexError):
            return value
    return value


def validate_lines(lines: list[str]) -> None:
    seen_top: set[str] = set()
    current_section: str | None = None
    seen_children: dict[str, set[str]] = {}
    for number, line in enumerate(lines, start=1):
        if "\t" in line[: len(line) - len(line.lstrip())]:
            raise ValueError(f"Tabs are not supported for indentation at line {number}.")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        top = TOP_LEVEL_RE.match(line)
        if top:
            key = top.group(1)
            if key in seen_top:
                raise ValueError(f"Duplicate top-level key {key!r} at line {number}.")
            seen_top.add(key)
            current_section = key if not (top.group(2) or "").strip() else None
            seen_children.setdefault(key, set())
            continue
        child = CHILD_RE.match(line)
        if child and current_section:
            key = child.group(1)
            if key in seen_children[current_section]:
                raise ValueError(
                    f"Duplicate key {current_section}.{key} at line {number}."
                )
            seen_children[current_section].add(key)
            continue
        if not line.startswith(" "):
            raise ValueError(f"Unsupported YAML root structure at line {number}: {line}")


def top_positions(lines: list[str]) -> list[tuple[int, str, str]]:
    positions: list[tuple[int, str, str]] = []
    for index, line in enumerate(lines):
        match = TOP_LEVEL_RE.match(line)
        if match:
            positions.append((index, match.group(1), (match.group(2) or "").strip()))
    return positions


def section_bounds(lines: list[str], section: str) -> tuple[int, int, str] | None:
    positions = top_positions(lines)
    for offset, (start, key, raw) in enumerate(positions):
        if key == section:
            end = positions[offset + 1][0] if offset + 1 < len(positions) else len(lines)
            return start, end, raw
    return None


def set_top_value(
    lines: list[str], key: str, value: str, overwrite: bool, changes: list[str]
) -> None:
    bounds = section_bounds(lines, key)
    rendered = f"{key}: {yaml_scalar(value)}"
    if bounds is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(rendered)
        changes.append(key)
        return
    start, end, raw = bounds
    if end > start + 1 and not raw:
        raise ValueError(f"Cannot replace mapping {key!r} with a scalar value.")
    existing = scalar_value(raw)
    if existing == value:
        return
    if not overwrite:
        raise ValueError(
            f"Configuration conflict for {key}: existing={existing!r}, requested={value!r}. "
            "Use --overwrite only after user confirmation."
        )
    _, comment = split_scalar_comment(raw)
    lines[start] = rendered + comment
    changes.append(key)


def set_child_value(
    lines: list[str],
    section: str,
    key: str,
    value: str,
    overwrite: bool,
    changes: list[str],
) -> None:
    bounds = section_bounds(lines, section)
    rendered = f"  {key}: {yaml_scalar(value)}"
    if bounds is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([f"{section}:", rendered])
        changes.append(f"{section}.{key}")
        return
    start, end, raw = bounds
    if raw:
        raise ValueError(f"Cannot add {section}.{key}: {section!r} is not a mapping.")
    for index in range(start + 1, end):
        match = CHILD_RE.match(lines[index])
        if not match or match.group(1) != key:
            continue
        existing = scalar_value((match.group(2) or "").strip())
        if existing == value:
            return
        if not overwrite:
            raise ValueError(
                f"Configuration conflict for {section}.{key}: existing={existing!r}, "
                f"requested={value!r}. Use --overwrite only after user confirmation."
            )
        _, comment = split_scalar_comment((match.group(2) or "").strip())
        lines[index] = rendered + comment
        changes.append(f"{section}.{key}")
        return
    lines.insert(end, rendered)
    changes.append(f"{section}.{key}")


def requested_updates(args: argparse.Namespace) -> list[tuple[tuple[str, ...], str]]:
    candidates = [
        (("language",), args.language),
        (("version_control", "language"), args.version_control_language),
        (("version_control", "system"), args.system),
        (("version_control", "trunk_branch"), args.trunk_branch),
        (("version_control", "contribution_model"), args.contribution_model),
        (("version_control", "source_remote"), args.source_remote),
        (("version_control", "target_remote"), args.target_remote),
        (("access_policy", "mode"), args.access_mode),
        (("access_policy", "directory_file"), args.directory_file),
        (("access_policy", "user_file_template"), args.user_file_template),
        (("writing_style", "guide"), args.writing_style_guide),
    ]
    return [(path, value) for path, value in candidates if value is not None]


def update_text(
    original: str, updates: list[tuple[tuple[str, ...], str]], overwrite: bool
) -> tuple[str, list[str]]:
    lines = original.splitlines()
    validate_lines(lines)
    changes: list[str] = []
    for path, value in updates:
        if len(path) == 1:
            set_top_value(lines, path[0], value, overwrite, changes)
        else:
            set_child_value(lines, path[0], path[1], value, overwrite, changes)
    updated = "\n".join(lines).rstrip()
    return (updated + "\n" if updated else "", changes)


def unified_diff(path: Path, original: str, updated: str) -> str:
    before = original.splitlines(keepends=True)
    after = updated.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            before,
            after,
            fromfile=str(path),
            tofile=str(path),
        )
    )


def configured_value(lines: list[str], path: tuple[str, ...]) -> str | None:
    bounds = section_bounds(lines, path[0])
    if bounds is None:
        return None
    start, end, raw = bounds
    if len(path) == 1:
        return scalar_value(raw) if raw else None
    if raw:
        return None
    for index in range(start + 1, end):
        match = CHILD_RE.match(lines[index])
        if match and match.group(1) == path[1]:
            child_raw = (match.group(2) or "").strip()
            return scalar_value(child_raw) if child_raw else None
    return None


def validation_scopes(args: argparse.Namespace, lines: list[str]) -> list[str]:
    requested = set(args.scope or ["basic"])
    if "all" in requested:
        requested = {"basic", "version-control"}
    if section_bounds(lines, "version_control") is not None:
        requested.add("version-control")
    if section_bounds(lines, "access_policy") is not None:
        requested.add("access-policy")
    if section_bounds(lines, "writing_style") is not None:
        requested.add("writing-style")
    order = ("basic", "version-control", "access-policy", "writing-style")
    return [scope for scope in order if scope in requested]


def resolve_reference(raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else Path.cwd() / path


def validate_configuration(args: argparse.Namespace, updated: str) -> dict[str, Any]:
    lines = updated.splitlines()
    scopes = validation_scopes(args, lines)
    required_fields: dict[str, tuple[tuple[str, ...], ...]] = {
        "basic": (("language",),),
        "version-control": (("version_control", "language"),),
        "access-policy": (
            ("access_policy", "mode"),
            ("access_policy", "directory_file"),
        ),
        "writing-style": (("writing_style", "guide"),),
    }
    missing_fields: list[str] = []
    for scope in scopes:
        for path in required_fields[scope]:
            if not configured_value(lines, path):
                missing_fields.append(".".join(path))

    missing_files: list[dict[str, str]] = []
    references = (
        ("access-policy", ("access_policy", "directory_file")),
        ("writing-style", ("writing_style", "guide")),
    )
    for scope, path in references:
        if scope not in scopes:
            continue
        value = configured_value(lines, path)
        if not value:
            continue
        resolved = resolve_reference(value)
        if not resolved.is_file():
            missing_files.append({"field": ".".join(path), "path": value})

    status = "valid" if not missing_fields and not missing_files else "incomplete"
    return {
        "status": status,
        "scopes": scopes,
        "missing_fields": missing_fields,
        "missing_files": missing_files,
    }


def plan(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.path)
    exists = path.exists()
    if exists and not path.is_file():
        raise ValueError(f"Configuration path is not a file: {path}")
    original = path.read_text(encoding="utf-8") if exists else ""
    updates = requested_updates(args)
    if not exists and not updates:
        raise ValueError("New configuration requires at least one explicit field.")
    updated, changes = update_text(original, updates, args.overwrite)
    action = "unchanged" if updated == original else ("updated" if exists else "created")
    return {
        "mode": "execute" if args.execute else "dry-run",
        "path": str(path),
        "action": action,
        "changes": changes,
        "diff": unified_diff(path, original, updated),
        "content": updated,
        "validation": validate_configuration(args, updated),
    }


def main() -> int:
    args = parse_args()
    try:
        result = plan(args)
        result["write_status"] = "not-requested"
        if args.execute:
            if result["validation"]["status"] != "valid":
                result["write_status"] = "blocked-incomplete"
            elif result["action"] == "unchanged":
                result["write_status"] = "not-needed"
            else:
                path = Path(args.path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(result["content"], encoding="utf-8")
                result["write_status"] = "written"
    except (OSError, ValueError) as error:
        if args.json:
            print(json.dumps({"error": str(error)}, ensure_ascii=False))
        else:
            print(f"Error: {error}")
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Mode: {result['mode']}")
        print(f"Action: {result['action']}")
        print(f"Path: {result['path']}")
        print(f"Write status: {result['write_status']}")
        if result["changes"]:
            print("Fields: " + ", ".join(result["changes"]))
        if result["diff"]:
            print(result["diff"], end="")
        print(f"Validation: {result['validation']['status']}")
        if result["validation"]["missing_fields"]:
            print("Missing fields: " + ", ".join(result["validation"]["missing_fields"]))
        for missing in result["validation"]["missing_files"]:
            print(f"Missing file: {missing['field']} -> {missing['path']}")
    return 0 if result["validation"]["status"] == "valid" else 2


if __name__ == "__main__":
    raise SystemExit(main())

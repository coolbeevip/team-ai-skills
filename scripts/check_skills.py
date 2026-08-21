#!/usr/bin/env python3
"""Generic structural checks for team skill SKILL.md files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
RE_CJK = re.compile(r"[\u4e00-\u9fff]")
RE_ALPHA = re.compile(r"[A-Za-z]")
RE_H2 = re.compile(r"^##\s+(.+?)\s*$")
RE_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
RE_MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
MAX_DESCRIPTION_CHARS = 220
CANONICAL_RUNTIME_HEADING = "运行时配置"
DEPRECATED_RUNTIME_HEADINGS = {"运行时语言配置", "语言约定"}
DEPRECATED_FINAL_REPLY_HEADING = "完成输出"
DEPRECATED_SKILL_NAMES = {
    "team-prd-to-alignment",
    "team-prd-to-issues",
    "team-tech-debt-to-issues",
    "team-issue-batch-implement",
    "team-issue-create-mr-gitlab",
    "team-issue-create-pr-github",
    "team-issue-implement",
    "team-issue-publish-github",
    "team-issue-publish-gitlab",
    "team-issue-verify",
}
DEPRECATED_RUNTIME_PATHS = {
    "team-spec/active/{slug}/prd/alignment.md",
    "team-spec/active/{slug}/issues/",
    "team-spec/archive/{slug}/prd/alignment.md",
    "team-spec/archive/{slug}/issues/",
}
DEPRECATED_BRANCH_TEMPLATE = "spec/{slug}"
RUNTIME_CONTRACT_EXEMPT_SKILLS = {"team-config-init"}


def parse_frontmatter(path: Path) -> tuple[dict[str, object], list[str]]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, ["missing YAML frontmatter"]

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, ["unterminated YAML frontmatter"]

    lines = text[4:end].splitlines()
    data: dict[str, object] = {}
    section: str | None = None
    parent: str | None = None

    for raw in lines:
        if not raw.strip():
            continue

        if raw.startswith("  - ") and section:
            value = raw[4:].strip()
            if section not in data or not isinstance(data[section], list):
                data[section] = []
            data[section].append(value)
            continue

        if raw.startswith("  ") and parent:
            key, sep, value = raw.strip().partition(":")
            if sep:
                parent_data = data.setdefault(parent, {})
                if isinstance(parent_data, dict):
                    parent_data[key] = value.strip().strip('"')
            continue

        key, sep, value = raw.partition(":")
        if not sep:
            errors.append(f"cannot parse frontmatter line: {raw}")
            continue

        key = key.strip()
        value = value.strip()
        section = None
        parent = None

        if value == "":
            if key == "triggers":
                data[key] = []
                section = key
            else:
                data[key] = {}
                parent = key
        else:
            data[key] = value.strip('"')

    return data, errors


def has_chinese(text: str) -> bool:
    return bool(RE_CJK.search(text))


def has_english(text: str) -> bool:
    return bool(RE_ALPHA.search(text))


def iter_unfenced_lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    fence_char: str | None = None
    fence_length = 0

    for line_number, line in enumerate(text.splitlines(), start=1):
        fence_match = RE_FENCE.match(line)
        if fence_match:
            token = fence_match.group(1)
            if fence_char is None:
                fence_char = token[0]
                fence_length = len(token)
            elif token[0] == fence_char and len(token) >= fence_length:
                fence_char = None
                fence_length = 0
            continue
        if fence_char is not None:
            continue
        lines.append((line_number, line))

    return lines


def iter_markdown_headings(text: str) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []

    for line_number, line in iter_unfenced_lines(text):
        match = RE_H2.match(line)
        if match:
            headings.append((line_number, match.group(1)))

    return headings


def h2_section_text(text: str, heading_name: str) -> str | None:
    headings = iter_markdown_headings(text)
    matching = [line_number for line_number, heading in headings if heading == heading_name]
    if not matching:
        return None

    start = matching[0]
    end = next(
        (line_number for line_number, _ in headings if line_number > start),
        len(text.splitlines()) + 1,
    )
    return "\n".join(
        line
        for line_number, line in iter_unfenced_lines(text)
        if start < line_number < end
    )


def iter_local_markdown_links(text: str) -> list[tuple[int, str]]:
    links: list[tuple[int, str]] = []
    for line_number, line in iter_unfenced_lines(text):
        for match in RE_MARKDOWN_LINK.finditer(line):
            raw_target = match.group(1).strip()
            if raw_target.startswith("<") and ">" in raw_target:
                target = raw_target[1 : raw_target.index(">")]
            else:
                target = raw_target.split(maxsplit=1)[0]
            if target.startswith(("./", "../")):
                links.append((line_number, target))
    return links


def check_skill(path: Path) -> list[str]:
    errors: list[str] = []
    data, parse_errors = parse_frontmatter(path)
    errors.extend(parse_errors)

    skill_dir = path.parent.name
    name = data.get("name")
    if name != skill_dir:
        errors.append(f"name must equal directory name {skill_dir!r}, got {name!r}")

    if not isinstance(name, str) or not name.startswith("team-"):
        errors.append("name must start with team-")

    description = data.get("description")
    if not isinstance(description, str) or not description:
        errors.append("description is required")
    elif not (has_chinese(description) and has_english(description)):
        errors.append("description must contain both Chinese and English")
    elif len(description) > MAX_DESCRIPTION_CHARS:
        errors.append(
            f"description should stay concise, found {len(description)} characters "
            f"(max {MAX_DESCRIPTION_CHARS})"
        )

    if data.get("license") != "MIT":
        errors.append("license must be MIT")

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata is required")
    else:
        if metadata.get("author") != "coolbeevip":
            errors.append("metadata.author must be coolbeevip")
        if metadata.get("version") != "1.0":
            errors.append('metadata.version must be "1.0"')

    triggers = data.get("triggers")
    if not isinstance(triggers, list):
        errors.append("triggers must be a list")
    else:
        zh_count = sum(1 for item in triggers if has_chinese(str(item)))
        en_count = sum(1 for item in triggers if has_english(str(item)) and not has_chinese(str(item)))
        if zh_count < 3:
            errors.append(f"triggers must include at least 3 Chinese phrases, found {zh_count}")
        if en_count < 3:
            errors.append(f"triggers must include at least 3 English phrases, found {en_count}")

    text = path.read_text(encoding="utf-8")
    if "## 输入物" not in text:
        errors.append("missing ## 输入物 section")
    if "## 输出物" not in text:
        errors.append("missing ## 输出物 section")
    if "## 触发边界" not in text:
        errors.append("missing ## 触发边界 section")
    if "## 完成标准" not in text:
        errors.append("missing ## 完成标准 section")
    if "## 最终回复" not in text:
        errors.append("missing ## 最终回复 section")

    for line_number, target in iter_local_markdown_links(text):
        file_target = target.partition("#")[0].partition("?")[0]
        if not (path.parent / file_target).resolve().exists():
            errors.append(
                f"missing local reference at line {line_number}: {target!r}"
            )

    heading_lines: dict[str, list[int]] = {}
    for line_number, heading in iter_markdown_headings(text):
        heading_lines.setdefault(heading, []).append(line_number)

    for heading, lines in heading_lines.items():
        if len(lines) > 1:
            errors.append(f"duplicate ## {heading} section at lines {lines}")

    for deprecated_heading in DEPRECATED_RUNTIME_HEADINGS:
        if deprecated_heading in heading_lines:
            errors.append(
                f"use ## {CANONICAL_RUNTIME_HEADING} instead of ## {deprecated_heading}"
            )

    if DEPRECATED_FINAL_REPLY_HEADING in heading_lines:
        errors.append("use ## 最终回复 instead of ## 完成输出")

    for deprecated_name in sorted(DEPRECATED_SKILL_NAMES):
        if deprecated_name in text:
            errors.append(f"deprecated skill reference: {deprecated_name}")

    for deprecated_path in sorted(DEPRECATED_RUNTIME_PATHS):
        if deprecated_path in text:
            errors.append(f"deprecated runtime path: {deprecated_path}")

    if DEPRECATED_BRANCH_TEMPLATE in text:
        errors.append(
            f"deprecated branch template: {DEPRECATED_BRANCH_TEMPLATE}; use {{slug}}"
        )

    if isinstance(name, str) and name not in RUNTIME_CONTRACT_EXEMPT_SKILLS:
        runtime_contract = h2_section_text(text, CANONICAL_RUNTIME_HEADING)
        if runtime_contract is None:
            errors.append(f"missing ## {CANONICAL_RUNTIME_HEADING} section")
            runtime_contract = ""
        for required_term in ("team-spec/config.yml", "team-config-init"):
            if required_term not in runtime_contract:
                errors.append(
                    f"runtime contract for {name} must reference {required_term!r}"
                )
        if not any(term in runtime_contract for term in ("language", "语言")):
            errors.append(
                f"runtime contract for {name} must define language handling"
            )
        if not any(
            term in runtime_contract
            for term in ("access_policy", "访问策略", "访问边界", "读写边界")
        ):
            errors.append(
                f"runtime contract for {name} must define access_policy handling"
            )

    return errors


def iter_skill_files() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*/*/SKILL.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check team skill SKILL.md structure.")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional SKILL.md paths or skill directories. Defaults to all skills.",
    )
    args = parser.parse_args()

    paths: list[Path] = []
    if args.paths:
        for path in args.paths:
            resolved = path if path.is_absolute() else ROOT / path
            if resolved.is_dir():
                resolved = resolved / "SKILL.md"
            paths.append(resolved)
    else:
        paths = iter_skill_files()

    failures = 0
    for path in paths:
        if not path.exists():
            print(f"{path.relative_to(ROOT)}: missing file", file=sys.stderr)
            failures += 1
            continue
        errors = check_skill(path)
        if errors:
            failures += 1
            print(f"{path.relative_to(ROOT)}:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)

    if failures:
        print(f"FAILED: {failures} skill file(s) have structural issues.", file=sys.stderr)
        return 1

    print(f"OK: checked {len(paths)} skill file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Lightweight structural checks for team skill SKILL.md files."""

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


def iter_markdown_headings(text: str) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []
    in_fence = False

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        match = RE_H2.match(line)
        if match:
            headings.append((line_number, match.group(1)))

    return headings


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

    if name == "team-prd-to-tasks":
        required_confirmation_contract = (
            "## 拆解确认交互",
            "所有需要用户介入的节点",
            "✅ 接受当前拆解并写入",
            "🔄 粒度偏细，希望合并",
            "🔄 粒度偏粗，希望拆分",
            "⚠️ 依赖或顺序需要调整",
            "👤 局部调整某个 Task",
            "⛔ 取消本次拆解",
            "## 请选择如何调整该 Task",
        )
        for required_text in required_confirmation_contract:
            if required_text not in text:
                errors.append(
                    f"missing task confirmation contract text {required_text!r}"
                )

    if name == "team-writing-style":
        required_emoji_contract = (
            "用户交互与 Emoji",
            "功能性标记",
            "正式产物默认不使用",
            "Emoji 后必须保留完整文字",
        )
        style_template = path.parent / "assets" / "STYLE.md"
        if not style_template.exists():
            errors.append("missing default style template assets/STYLE.md")
        else:
            style_text = style_template.read_text(encoding="utf-8")
            for required_text in required_emoji_contract:
                if required_text not in style_text:
                    errors.append(
                        f"missing emoji style contract text {required_text!r}"
                    )

    if name == "team-prd-to-brief":
        required_brief_contract = (
            "team-spec/active/{slug}/prd/brief.md",
            "## 评审简报结构",
            "## 评审简报表达",
            "team-prd-to-tasks",
        )
        for required_text in required_brief_contract:
            if required_text not in text:
                errors.append(f"missing PRD brief contract text {required_text!r}")

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

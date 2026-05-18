#!/usr/bin/env python3
"""Validate skill metadata and keep the website skill index in sync."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
WEBSITE_INDEX = ROOT / "website" / "index.html"

DOMAIN_ORDER = [
    "product",
    "architecture",
    "harness",
    "delivery",
    "tech-debt",
    "documentation",
]

DOMAIN_LABELS = {
    "product": "产品",
    "architecture": "架构",
    "harness": "Harness",
    "delivery": "交付",
    "tech-debt": "治理",
    "documentation": "文档",
}

DOC_FILES = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    WEBSITE_INDEX,
]

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
RELATIVE_REF_RE = re.compile(r"(?<![\w/])(\./[A-Za-z0-9][A-Za-z0-9_./-]*[A-Za-z0-9])")
SKILL_REF_RE = re.compile(r"\b(team-[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)\b(?!/)")
CJK_RE = re.compile(r"[\u3400-\u9fff]")
LATIN_RE = re.compile(r"[A-Za-z]")


@dataclass(frozen=True)
class Skill:
    name: str
    domain_key: str
    domain_label: str
    path: Path
    description: str
    summary: str
    triggers: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate SKILL metadata and sync generated website sections."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Run repository validation.")
    validate_parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")

    sync_parser = subparsers.add_parser(
        "sync-website", help="Update generated website sections from discovered skills."
    )
    sync_parser.add_argument(
        "--check",
        action="store_true",
        help="Only verify generated website sections are up to date.",
    )
    return parser.parse_args()


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def extract_frontmatter(text: str, path: Path) -> tuple[dict[str, object], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{path}: missing YAML frontmatter.")

    frontmatter = match.group(1).splitlines()
    data: dict[str, object] = {}
    current_list: str | None = None
    current_map: str | None = None

    for raw_line in frontmatter:
        if not raw_line.strip():
            continue

        if raw_line.startswith("  - "):
            if not current_list:
                raise ValueError(f"{path}: invalid list item in frontmatter: {raw_line!r}")
            items = data.setdefault(current_list, [])
            if not isinstance(items, list):
                raise ValueError(f"{path}: frontmatter key {current_list} is not a list.")
            items.append(strip_quotes(raw_line[4:]))
            continue

        if raw_line.startswith("  "):
            if not current_map:
                raise ValueError(f"{path}: invalid nested frontmatter entry: {raw_line!r}")
            key, sep, value = raw_line.strip().partition(":")
            if not sep:
                raise ValueError(f"{path}: invalid nested frontmatter entry: {raw_line!r}")
            mapping = data.setdefault(current_map, {})
            if not isinstance(mapping, dict):
                raise ValueError(f"{path}: frontmatter key {current_map} is not a map.")
            mapping[key.strip()] = strip_quotes(value)
            continue

        current_list = None
        current_map = None
        key, sep, value = raw_line.partition(":")
        if not sep:
            raise ValueError(f"{path}: invalid frontmatter line: {raw_line!r}")
        key = key.strip()
        value = value.strip()
        if not value:
            if key == "triggers":
                data[key] = []
                current_list = key
            elif key == "metadata":
                data[key] = {}
                current_map = key
            else:
                data[key] = ""
        else:
            data[key] = strip_quotes(value)

    return data, text[match.end() :]


def chinese_summary(description: str) -> str:
    description = description.strip()
    if not description:
        return ""
    first_sentence, separator, _ = description.partition("。")
    if separator:
        return first_sentence.strip() + "。"
    first_sentence, separator, _ = description.partition(".")
    if separator:
        return first_sentence.strip() + "."
    return description


def discover_skills() -> tuple[list[Skill], list[str]]:
    skills: list[Skill] = []
    errors: list[str] = []

    for path in sorted(SKILLS_ROOT.glob("*/*/SKILL.md")):
        domain_key = path.parent.parent.name
        try:
            text = path.read_text(encoding="utf-8")
            frontmatter, body = extract_frontmatter(text, path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            continue

        name = str(frontmatter.get("name", "")).strip()
        description = str(frontmatter.get("description", "")).strip()
        license_value = str(frontmatter.get("license", "")).strip()
        triggers_raw = frontmatter.get("triggers", [])
        metadata = frontmatter.get("metadata", {})
        triggers = tuple(item.strip() for item in triggers_raw if str(item).strip()) if isinstance(triggers_raw, list) else ()
        metadata_map = metadata if isinstance(metadata, dict) else {}

        if not name:
            errors.append(f"{path}: missing frontmatter field 'name'.")
        elif name != path.parent.name:
            errors.append(f"{path}: frontmatter name {name!r} does not match directory {path.parent.name!r}.")

        if not description:
            errors.append(f"{path}: missing frontmatter field 'description'.")
        if license_value != "MIT":
            errors.append(f"{path}: license must be MIT.")
        if metadata_map.get("author") != "coolbeevip":
            errors.append(f"{path}: metadata.author must be coolbeevip.")
        if metadata_map.get("version") != "1.0":
            errors.append(f"{path}: metadata.version must be 1.0.")

        zh_triggers = sum(1 for trigger in triggers if CJK_RE.search(trigger))
        en_triggers = sum(1 for trigger in triggers if LATIN_RE.search(trigger))
        if zh_triggers < 3:
            errors.append(f"{path}: triggers must include at least 3 Chinese phrases.")
        if en_triggers < 3:
            errors.append(f"{path}: triggers must include at least 3 English phrases.")

        if "## 输入物" not in body:
            errors.append(f"{path}: missing section '## 输入物'.")
        if "## 输出物" not in body:
            errors.append(f"{path}: missing section '## 输出物'.")

        for ref in sorted(set(RELATIVE_REF_RE.findall(text))):
            target = (path.parent / ref[2:]).resolve()
            if not target.exists():
                errors.append(f"{path}: referenced relative path does not exist: {ref}")

        if description:
            skills.append(
                Skill(
                    name=name or path.parent.name,
                    domain_key=domain_key,
                    domain_label=DOMAIN_LABELS.get(domain_key, domain_key),
                    path=path,
                    description=description,
                    summary=chinese_summary(description),
                    triggers=triggers,
                )
            )

    skills.sort(key=lambda skill: (DOMAIN_ORDER.index(skill.domain_key), skill.name))
    return skills, errors


def validate_doc_skill_refs(doc_path: Path, known_skills: set[str]) -> list[str]:
    errors: list[str] = []
    text = doc_path.read_text(encoding="utf-8")
    for ref in sorted(set(SKILL_REF_RE.findall(text))):
        if ref == "team-ai-skills":
            continue
        if ref not in known_skills and any(skill.startswith(ref + "-") for skill in known_skills):
            continue
        if ref not in known_skills:
            errors.append(f"{doc_path}: references unknown skill {ref}.")
    return errors


def marker_block(text: str, name: str, content: str) -> str:
    start = f"<!-- generated:{name}:start -->"
    end = f"<!-- generated:{name}:end -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    replacement = f"{start}\n{content.rstrip()}\n{end}"
    if not pattern.search(text):
        raise ValueError(f"Missing generated marker block: {name}")
    return pattern.sub(replacement, text, count=1)


def render_domain_stats(skills: list[Skill]) -> str:
    counts = Counter(skill.domain_label for skill in skills)
    parts = [f'<span class="skill-stat"><strong>{len(skills)}</strong> skills</span>']
    for domain_key in DOMAIN_ORDER:
        label = DOMAIN_LABELS[domain_key]
        parts.append(f'<span class="skill-stat">{escape(label)} {counts.get(label, 0)}</span>')
    return "".join(parts)


def ordered_trigger_cloud(skills: list[Skill], limit: int = 24) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for skill in skills:
        for trigger in skill.triggers:
            if trigger not in seen:
                seen.add(trigger)
                ordered.append(trigger)
            if len(ordered) >= limit:
                return ordered
    return ordered


def render_trigger_cloud(skills: list[Skill]) -> str:
    triggers = ordered_trigger_cloud(skills)
    chips = "".join(
        f'<span class="trigger-chip trigger-chip-cloud">{escape(trigger)}</span>'
        for trigger in triggers
    )
    return (
        '<div class="trigger-cloud">'
        '<span class="trigger-cloud-label">常见触发词</span>'
        f"{chips}"
        "</div>"
    )


def render_skill_rows(skills: list[Skill]) -> str:
    rows: list[str] = []
    for skill in skills:
        trigger_chips = "".join(
            f'<span class="trigger-chip">{escape(trigger)}</span>'
            for trigger in skill.triggers[:4]
        )
        rows.append(
            "\n".join(
                [
                    '<article class="index-row">',
                    f'  <span class="index-domain">{escape(skill.domain_label)}</span>',
                    '  <div class="index-main">',
                    f"    <code>{escape(skill.name)}</code>",
                    f"    <p>{escape(skill.summary)}</p>",
                    f'    <div class="index-triggers">{trigger_chips}</div>',
                    "  </div>",
                    "</article>",
                ]
            )
        )
    return "\n".join(rows)


def render_website(skills: list[Skill]) -> str:
    html = WEBSITE_INDEX.read_text(encoding="utf-8")
    html = marker_block(
        html,
        "hero-badge",
        f"MIT Licensed · {len(skills)} Skills · {len(DOMAIN_ORDER)} Domains",
    )
    html = marker_block(html, "skill-title", f"{len(skills)} 个技能，一张表查完")
    html = marker_block(html, "skill-stats", render_domain_stats(skills))
    html = marker_block(html, "trigger-cloud", render_trigger_cloud(skills))
    html = marker_block(html, "skill-index", render_skill_rows(skills))
    return html


def validate_repository() -> tuple[list[Skill], list[str]]:
    skills, errors = discover_skills()
    known_skills = {skill.name for skill in skills}

    for doc_path in DOC_FILES:
        errors.extend(validate_doc_skill_refs(doc_path, known_skills))

    try:
        expected = render_website(skills)
        current = WEBSITE_INDEX.read_text(encoding="utf-8")
        if current != expected:
            errors.append(
                "website/index.html generated sections are out of date. "
                "Run: python3 scripts/skill_catalog.py sync-website"
            )
    except (OSError, ValueError) as exc:
        errors.append(str(exc))

    return skills, errors


def command_validate(json_output: bool) -> int:
    skills, errors = validate_repository()
    result = {
        "skill_count": len(skills),
        "errors": errors,
    }
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if errors:
            print("Repository validation failed:")
            for error in errors:
                print(f"- {error}")
        else:
            print(f"Repository validation passed for {len(skills)} skills.")
    return 1 if errors else 0


def command_sync_website(check: bool) -> int:
    skills, errors = discover_skills()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    try:
        rendered = render_website(skills)
        current = WEBSITE_INDEX.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if check:
        if current != rendered:
            print("website/index.html is out of date. Run: python3 scripts/skill_catalog.py sync-website")
            return 1
        print("website/index.html is up to date.")
        return 0

    WEBSITE_INDEX.write_text(rendered, encoding="utf-8")
    print(f"Updated {WEBSITE_INDEX.relative_to(ROOT)} from {len(skills)} skills.")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "validate":
        return command_validate(args.json)
    if args.command == "sync-website":
        return command_sync_website(args.check)
    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

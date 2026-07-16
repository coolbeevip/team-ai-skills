#!/usr/bin/env python3
"""Plan a dependency-ordered batch of AFK issue implementations."""

from __future__ import annotations

import argparse
import json
import re
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
COMPLETED_MARKERS = {
    "verified",
    "pr-created",
    "mr-created",
    "ready for pr",
    "pr created",
    "mr created",
    "done",
    "completed",
    "closed",
}
IGNORED_SUFFIXES = (
    ".implementation.md",
    ".verification.md",
)


@dataclass
class Issue:
    key: str
    path: Path
    title: str
    issue_type: str
    status: str
    blocked_by: list[str]
    has_acceptance: bool
    dependencies: list[str] = field(default_factory=list)
    external_blockers: list[str] = field(default_factory=list)

    @property
    def is_afk(self) -> bool:
        return self.issue_type == "AFK"

    @property
    def is_hitl(self) -> bool:
        return self.issue_type == "HITL"

    @property
    def is_completed(self) -> bool:
        status = self.status.lower()
        return any(marker in status for marker in COMPLETED_MARKERS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan runnable AFK issue batches.")
    parser.add_argument("--slug", help="Slug under team-spec/active/{slug}/issues.")
    parser.add_argument("--issues-dir", help="Directory containing local issue drafts.")
    parser.add_argument(
        "--issue",
        action="append",
        default=[],
        help="Specific issue file, filename, or key to include. Repeat for multiple issues.",
    )
    parser.add_argument("--limit", type=int, default=3, help="Maximum runnable issues to list.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def resolve_issues_dir(args: argparse.Namespace) -> Path:
    if args.issues_dir:
        path = Path(args.issues_dir)
    elif args.slug:
        path = Path("team-spec") / "active" / args.slug / "issues"
    else:
        raise SystemExit("Provide --slug or --issues-dir.")
    if not path.exists() or not path.is_dir():
        raise SystemExit(f"Issues directory does not exist: {path}")
    return path


def split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[title.lower()] = text[start:end].strip()
    return sections


def issue_key_from_path(path: Path) -> str:
    match = re.match(r"^(\d+)", path.stem)
    return match.group(1) if match else path.stem


def issue_title(path: Path, text: str, sections: dict[str, str]) -> str:
    heading = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if heading:
        return heading.group(1).strip()
    title_section = sections.get("title")
    if title_section:
        return title_section.splitlines()[0].strip()
    return path.stem


def issue_type(sections: dict[str, str]) -> str:
    value = sections.get("type", "")
    upper = value.upper()
    if "HITL" in upper:
        return "HITL"
    if "AFK" in upper:
        return "AFK"
    return "unknown"


def issue_status(sections: dict[str, str], text: str) -> str:
    value = sections.get("status")
    if value:
        return value.splitlines()[0].strip()
    match = re.search(r"^\s*[-*]?\s*Status\s*:\s*(.+?)\s*$", text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def blocked_refs(sections: dict[str, str]) -> list[str]:
    value = sections.get("blocked by", "")
    refs: list[str] = []
    for raw in value.splitlines():
        line = raw.strip().lstrip("-*").strip()
        if not line:
            continue
        normalized = line.lower()
        if normalized.startswith("none") or normalized in {"无", "无依赖", "没有依赖"}:
            continue
        line_refs: list[str] = []
        for filename in re.findall(r"([0-9][A-Za-z0-9_-]*\.md)", line):
            line_refs.append(issue_key_from_path(Path(filename)))
        line_refs.extend(re.findall(r"#(\d+)", line))
        if not line_refs:
            match = re.match(r"^(\d+)(?:\s|$|[-_])", line)
            if match:
                line_refs.append(match.group(1))
        for number in line_refs:
            refs.append(number)
    return refs


def has_acceptance_criteria(sections: dict[str, str]) -> bool:
    value = sections.get("acceptance criteria", "")
    return bool(value.strip())


def read_issue(path: Path) -> Issue:
    text = path.read_text(encoding="utf-8")
    sections = split_sections(text)
    return Issue(
        key=issue_key_from_path(path),
        path=path,
        title=issue_title(path, text, sections),
        issue_type=issue_type(sections),
        status=issue_status(sections, text),
        blocked_by=blocked_refs(sections),
        has_acceptance=has_acceptance_criteria(sections),
    )


def issue_files(issues_dir: Path) -> list[Path]:
    files = []
    for path in sorted(issues_dir.glob("*.md")):
        if path.name == "batch-implementation.md":
            continue
        if path.name.endswith(IGNORED_SUFFIXES):
            continue
        files.append(path)
    return files


def issue_aliases(issue: Issue) -> set[str]:
    aliases = {issue.key, issue.key.lstrip("0") or "0", issue.path.name, issue.path.stem}
    return {alias for alias in aliases if alias}


def build_alias_map(issues: list[Issue]) -> dict[str, Issue]:
    aliases: dict[str, Issue] = {}
    for issue in issues:
        for alias in issue_aliases(issue):
            aliases.setdefault(alias, issue)
    return aliases


def select_issues(all_issues: list[Issue], selectors: list[str]) -> set[str] | None:
    if not selectors:
        return None
    aliases = build_alias_map(all_issues)
    selected: set[str] = set()
    for selector in selectors:
        key = Path(selector).name if "/" in selector else selector
        issue = aliases.get(key) or aliases.get(Path(key).stem) or aliases.get(key.lstrip("0") or "0")
        if not issue:
            raise SystemExit(f"Cannot match issue selector: {selector}")
        selected.add(issue.key)
    return selected


def resolve_dependency(ref: str, aliases: dict[str, Issue]) -> Issue | None:
    return aliases.get(ref) or aliases.get(ref.lstrip("0") or "0")


def plan_batch(all_issues: list[Issue], selected: set[str] | None, limit: int) -> dict[str, Any]:
    aliases = build_alias_map(all_issues)
    completed = {issue.key for issue in all_issues if issue.is_completed}
    candidates: dict[str, Issue] = {}
    skipped: list[dict[str, str]] = []

    for issue in all_issues:
        if selected is not None and issue.key not in selected:
            continue
        if issue.is_completed:
            skipped.append(summary(issue, "already completed"))
            continue
        if issue.is_hitl:
            skipped.append(summary(issue, "HITL requires human decision"))
            continue
        if not issue.is_afk:
            skipped.append(summary(issue, "Type is not AFK"))
            continue
        if not issue.has_acceptance:
            skipped.append(summary(issue, "missing acceptance criteria"))
            continue
        candidates[issue.key] = issue

    for issue in candidates.values():
        for ref in issue.blocked_by:
            dependency = resolve_dependency(ref, aliases)
            if dependency is None:
                issue.external_blockers.append(f"missing dependency {ref}")
            elif dependency.key in completed:
                issue.dependencies.append(dependency.key)
            elif dependency.key in candidates:
                issue.dependencies.append(dependency.key)
            else:
                issue.external_blockers.append(f"{dependency.key} {dependency.title}")

    blocked: list[dict[str, str]] = []
    sortable = {
        key: issue
        for key, issue in candidates.items()
        if not issue.external_blockers
    }
    for issue in candidates.values():
        if issue.external_blockers:
            blocked.append(summary(issue, "blocked by " + ", ".join(issue.external_blockers)))

    indegree = {key: 0 for key in sortable}
    outgoing: dict[str, list[str]] = {key: [] for key in sortable}
    for issue in sortable.values():
        for dep in issue.dependencies:
            if dep in sortable:
                indegree[issue.key] += 1
                outgoing[dep].append(issue.key)

    ready = deque(sorted(key for key, degree in indegree.items() if degree == 0))
    ordered: list[Issue] = []
    while ready:
        key = ready.popleft()
        issue = sortable[key]
        ordered.append(issue)
        for dependent in sorted(outgoing[key]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)

    cycle_keys = sorted(set(sortable) - {issue.key for issue in ordered})
    for key in cycle_keys:
        blocked.append(summary(sortable[key], "cycle detected in Blocked by graph"))

    queue = ordered[: max(limit, 0)]
    return {
        "queue": [summary(issue, "runnable") for issue in queue],
        "remaining_runnable": [summary(issue, "runnable after limit") for issue in ordered[len(queue) :]],
        "blocked": blocked,
        "skipped": skipped,
        "total_issues": len(all_issues),
        "limit": limit,
    }


def summary(issue: Issue, reason: str) -> dict[str, str]:
    return {
        "key": issue.key,
        "title": issue.title,
        "path": str(issue.path),
        "type": issue.issue_type,
        "status": issue.status,
        "reason": reason,
    }


def print_markdown(plan: dict[str, Any], issues_dir: Path) -> None:
    print("# Issue Batch Plan")
    print()
    print(f"- Issues dir: `{issues_dir}`")
    print(f"- Total issue files: {plan['total_issues']}")
    print(f"- Limit: {plan['limit']}")
    print()
    print("## Runnable Queue")
    queue = plan["queue"]
    if not queue:
        print()
        print("- None")
    for index, issue in enumerate(queue, start=1):
        print(f"{index}. `{issue['key']}` {issue['title']} - `{issue['path']}`")
    print()
    print("## Remaining Runnable")
    remaining = plan["remaining_runnable"]
    if not remaining:
        print()
        print("- None")
    for issue in remaining:
        print(f"- `{issue['key']}` {issue['title']} - {issue['reason']}")
    print()
    print("## Blocked")
    blocked = plan["blocked"]
    if not blocked:
        print()
        print("- None")
    for issue in blocked:
        print(f"- `{issue['key']}` {issue['title']}: {issue['reason']}")
    print()
    print("## Skipped")
    skipped = plan["skipped"]
    if not skipped:
        print()
        print("- None")
    for issue in skipped:
        print(f"- `{issue['key']}` {issue['title']}: {issue['reason']}")


def main() -> int:
    args = parse_args()
    issues_dir = resolve_issues_dir(args)
    issues = [read_issue(path) for path in issue_files(issues_dir)]
    selected = select_issues(issues, args.issue)
    plan = plan_batch(issues, selected, args.limit)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_markdown(plan, issues_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

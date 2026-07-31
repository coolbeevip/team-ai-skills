#!/usr/bin/env python3
"""Plan a dependency-ordered batch of AFK engineering tasks."""

from __future__ import annotations

import argparse
import json
import re
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TASK_ID_RE = re.compile(r"\bT(\d{1,6})\b", re.IGNORECASE)
IGNORED_SUFFIXES = (".implementation.md", ".verification.md")


@dataclass
class Task:
    key: str
    path: Path
    title: str
    task_type: str
    status: str
    blocked_by: list[str]
    has_acceptance: bool
    commit: str | None
    dependencies: list[str] = field(default_factory=list)
    external_blockers: list[str] = field(default_factory=list)

    @property
    def is_afk(self) -> bool:
        return self.task_type == "AFK"

    @property
    def is_hitl(self) -> bool:
        return self.task_type == "HITL"

    @property
    def is_committed(self) -> bool:
        return self.status.lower() == "committed" and bool(self.commit)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan runnable AFK task batches.")
    parser.add_argument("--slug", help="Slug under team-spec/active/{slug}/tasks.")
    parser.add_argument("--tasks-dir", help="Directory containing local Task files.")
    parser.add_argument(
        "--task",
        action="append",
        default=[],
        help="Specific Task file, filename, or T-number. Repeat for multiple Tasks.",
    )
    parser.add_argument("--limit", type=int, default=3, help="Maximum runnable Tasks to list.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def resolve_tasks_dir(args: argparse.Namespace) -> Path:
    if args.tasks_dir:
        path = Path(args.tasks_dir)
    elif args.slug:
        path = Path("team-spec") / "active" / args.slug / "tasks"
    else:
        raise SystemExit("Provide --slug or --tasks-dir.")
    if not path.is_dir():
        raise SystemExit(f"Tasks directory does not exist: {path}")
    return path


def split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip().lower()] = text[start:end].strip()
    return sections


def normalize_task_id(value: str) -> str | None:
    match = TASK_ID_RE.search(value)
    if not match:
        return None
    return f"T{int(match.group(1)):03d}"


def task_key(path: Path, sections: dict[str, str]) -> str:
    explicit = normalize_task_id(sections.get("task id", ""))
    filename = normalize_task_id(path.stem)
    key = explicit or filename
    if not key:
        raise SystemExit(f"Task file needs a T-number in Task ID or filename: {path}")
    return key


def task_title(path: Path, text: str, sections: dict[str, str]) -> str:
    heading = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if heading:
        return heading.group(1).strip()
    title = sections.get("title")
    return title.splitlines()[0].strip() if title else path.stem


def task_type(sections: dict[str, str]) -> str:
    value = sections.get("type", "").upper()
    if "HITL" in value:
        return "HITL"
    if "AFK" in value:
        return "AFK"
    return "unknown"


def first_line(sections: dict[str, str], name: str) -> str:
    value = sections.get(name, "")
    return value.splitlines()[0].strip() if value else ""


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
        refs.extend(
            task_id
            for task_id in (normalize_task_id(match.group(0)) for match in TASK_ID_RE.finditer(line))
            if task_id
        )
    return list(dict.fromkeys(refs))


def read_task(path: Path) -> Task:
    text = path.read_text(encoding="utf-8")
    sections = split_sections(text)
    commit = first_line(sections, "commit")
    if commit.lower() in {"", "pending", "none", "n/a"}:
        commit = None
    return Task(
        key=task_key(path, sections),
        path=path,
        title=task_title(path, text, sections),
        task_type=task_type(sections),
        status=first_line(sections, "status"),
        blocked_by=blocked_refs(sections),
        has_acceptance=bool(sections.get("acceptance criteria", "").strip()),
        commit=commit,
    )


def task_files(tasks_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(tasks_dir.glob("*.md")):
        if path.name == "batch-implementation.md" or path.name.endswith(IGNORED_SUFFIXES):
            continue
        if normalize_task_id(path.stem):
            files.append(path)
    return files


def aliases(task: Task) -> set[str]:
    numeric = str(int(task.key[1:]))
    return {task.key, task.key.lower(), numeric, task.path.name, task.path.stem}


def alias_map(tasks: list[Task]) -> dict[str, Task]:
    result: dict[str, Task] = {}
    for task in tasks:
        for alias in aliases(task):
            result.setdefault(alias, task)
    return result


def select_tasks(tasks: list[Task], selectors: list[str]) -> set[str] | None:
    if not selectors:
        return None
    known = alias_map(tasks)
    selected: set[str] = set()
    for selector in selectors:
        candidate = Path(selector).name if "/" in selector else selector
        normalized = normalize_task_id(candidate)
        task = known.get(candidate) or known.get(Path(candidate).stem)
        if not task and normalized:
            task = known.get(normalized)
        if not task:
            raise SystemExit(f"Cannot match Task selector: {selector}")
        selected.add(task.key)
    return selected


def summary(task: Task, reason: str) -> dict[str, str | None]:
    return {
        "key": task.key,
        "title": task.title,
        "path": str(task.path),
        "type": task.task_type,
        "status": task.status,
        "commit": task.commit,
        "reason": reason,
    }


def plan_batch(tasks: list[Task], selected: set[str] | None, limit: int) -> dict[str, Any]:
    known = alias_map(tasks)
    completed = {task.key for task in tasks if task.is_committed}
    candidates: dict[str, Task] = {}
    skipped: list[dict[str, str | None]] = []

    for task in tasks:
        if selected is not None and task.key not in selected:
            continue
        if task.is_committed:
            skipped.append(summary(task, "already committed"))
        elif task.is_hitl:
            skipped.append(summary(task, "HITL requires human decision"))
        elif not task.is_afk:
            skipped.append(summary(task, "Type is not AFK"))
        elif not task.has_acceptance:
            skipped.append(summary(task, "missing acceptance criteria"))
        else:
            candidates[task.key] = task

    for task in candidates.values():
        for ref in task.blocked_by:
            dependency = known.get(ref) or known.get(ref.lower())
            if dependency is None:
                task.external_blockers.append(f"missing dependency {ref}")
            elif dependency.key in completed:
                task.dependencies.append(dependency.key)
            elif dependency.key in candidates:
                task.dependencies.append(dependency.key)
            else:
                task.external_blockers.append(
                    f"{dependency.key} is not committed or selected"
                )

    blocked: list[dict[str, str | None]] = []
    sortable = {
        key: task for key, task in candidates.items() if not task.external_blockers
    }
    for task in candidates.values():
        if task.external_blockers:
            blocked.append(
                summary(task, "blocked by " + ", ".join(task.external_blockers))
            )

    indegree = {key: 0 for key in sortable}
    outgoing: dict[str, list[str]] = {key: [] for key in sortable}
    for task in sortable.values():
        for dependency in task.dependencies:
            if dependency in sortable:
                indegree[task.key] += 1
                outgoing[dependency].append(task.key)

    ready = deque(sorted(key for key, degree in indegree.items() if degree == 0))
    ordered: list[Task] = []
    while ready:
        key = ready.popleft()
        ordered.append(sortable[key])
        for dependent in sorted(outgoing[key]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)

    cycle_keys = sorted(set(sortable) - {task.key for task in ordered})
    for key in cycle_keys:
        blocked.append(summary(sortable[key], "cycle detected in Blocked by graph"))

    queue = ordered[: max(limit, 0)]
    return {
        "queue": [summary(task, "runnable") for task in queue],
        "remaining_runnable": [
            summary(task, "runnable after limit") for task in ordered[len(queue) :]
        ],
        "blocked": blocked,
        "skipped": skipped,
        "total_tasks": len(tasks),
        "limit": limit,
    }


def print_markdown(plan: dict[str, Any], tasks_dir: Path) -> None:
    print("# Task Batch Plan")
    print()
    print(f"- Tasks dir: `{tasks_dir}`")
    print(f"- Total Task files: {plan['total_tasks']}")
    print(f"- Limit: {plan['limit']}")
    for heading, key in (
        ("Runnable Queue", "queue"),
        ("Remaining Runnable", "remaining_runnable"),
        ("Blocked", "blocked"),
        ("Skipped", "skipped"),
    ):
        print()
        print(f"## {heading}")
        items = plan[key]
        if not items:
            print()
            print("- None")
            continue
        for index, task in enumerate(items, start=1):
            prefix = f"{index}." if key == "queue" else "-"
            print(
                f"{prefix} `{task['key']}` {task['title']} — "
                f"{task['reason']} (`{task['path']}`)"
            )


def main() -> int:
    args = parse_args()
    tasks_dir = resolve_tasks_dir(args)
    tasks = [read_task(path) for path in task_files(tasks_dir)]
    if not tasks:
        raise SystemExit(f"No T-numbered Task files found in {tasks_dir}")
    selected = select_tasks(tasks, args.task)
    plan = plan_batch(tasks, selected, args.limit)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_markdown(plan, tasks_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

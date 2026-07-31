#!/usr/bin/env python3
"""Create or synchronize one GitHub Issue for a complete team-spec workspace."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Any

from _team_common import ApiRequestError, api_request


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TASK_ID_RE = re.compile(r"\bT(\d{1,6})\b", re.IGNORECASE)
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "issue_body.md.tpl"


@dataclass
class Task:
    task_id: str
    title: str
    status: str
    path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or synchronize one GitHub Issue for a complete Spec."
    )
    parser.add_argument("--slug", required=True, help="Slug under team-spec/active.")
    parser.add_argument("--github-url", default="https://github.com")
    parser.add_argument("--repo", help="Target repository as owner/repo.")
    parser.add_argument("--remote", help="Git remote used to infer the target repo.")
    parser.add_argument("--title", help="Override the PRD-derived issue title.")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--milestone", type=int)
    parser.add_argument("--assignee", action="append", default=[])
    parser.add_argument("--language")
    parser.add_argument("--force", action="store_true", help="Ignore local Issue tracking.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def run_git(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def strip_yaml_scalar(value: str) -> str:
    value = value.split("#", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def config_values() -> dict[str, str]:
    path = Path("team-spec/config.yml")
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    section: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^(\s*)([A-Za-z0-9_-]+)\s*:\s*(.*?)\s*$", line)
        if not match:
            continue
        indent = len(match.group(1).replace("\t", "  "))
        key = match.group(2)
        value = strip_yaml_scalar(match.group(3))
        if indent == 0:
            section = key if not value else None
            if value:
                values[key] = value
        elif section and value:
            values[f"{section}.{key}"] = value
    return values


def remote_urls() -> dict[str, str]:
    output = run_git(["remote", "-v"]) or ""
    remotes: dict[str, str] = {}
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and "(fetch)" in line:
            remotes[parts[0]] = parts[1]
    return remotes


def parse_remote(url: str) -> tuple[str, str] | None:
    if url.startswith("git@"):
        match = re.match(r"git@([^:]+):(.+?)(?:\.git)?$", url)
        return (match.group(1), match.group(2)) if match else None
    parsed = urllib.parse.urlparse(url)
    if not parsed.hostname or not parsed.path:
        return None
    repo = parsed.path.strip("/")
    if repo.endswith(".git"):
        repo = repo[:-4]
    return parsed.hostname, repo


def infer_repo(args: argparse.Namespace, config: dict[str, str]) -> str:
    if args.repo:
        return args.repo.strip()
    remotes = remote_urls()
    remote = (
        args.remote
        or config.get("version_control.target_remote")
        or ("upstream" if "upstream" in remotes else None)
    )
    host = urllib.parse.urlparse(args.github_url).hostname or "github.com"
    if remote:
        parsed = parse_remote(remotes.get(remote, ""))
        if not parsed or parsed[0] != host:
            raise SystemExit(f"Remote {remote!r} is not a GitHub remote for {host}.")
        return parsed[1]
    candidates = {
        parsed[1]
        for url in remotes.values()
        if (parsed := parse_remote(url)) and parsed[0] == host
    }
    if len(candidates) != 1:
        raise SystemExit("Cannot infer one GitHub repo; provide --repo or --remote.")
    return candidates.pop()


def split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip().lower()] = text[start:end].strip()
    return sections


def first_heading(text: str) -> str | None:
    match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def section(sections: dict[str, str], *names: str) -> str | None:
    for name in names:
        value = sections.get(name.lower())
        if value:
            return value
    return None


def task_id(path: Path, sections: dict[str, str]) -> str | None:
    source = section(sections, "Task ID") or path.stem
    match = TASK_ID_RE.search(source)
    return f"T{int(match.group(1)):03d}" if match else None


def load_tasks(workspace: Path) -> list[Task]:
    tasks_dir = workspace / "tasks"
    if not tasks_dir.is_dir():
        raise SystemExit(f"Tasks directory does not exist: {tasks_dir}")
    tasks: list[Task] = []
    for path in sorted(tasks_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        sections = split_sections(text)
        identifier = task_id(path, sections)
        if not identifier:
            continue
        status = (section(sections, "Status") or "").splitlines()[0].strip().lower()
        tasks.append(Task(identifier, first_heading(text) or path.stem, status, path))
    if not tasks:
        raise SystemExit(f"No T-numbered Task files found in {tasks_dir}")
    return sorted(tasks, key=lambda task: int(task.task_id[1:]))


def language_labels(language: str) -> dict[str, str]:
    if language.lower().startswith("zh"):
        return {
            "goal_heading": "目标",
            "scope_heading": "范围",
            "acceptance_heading": "验收标准",
            "tasks_heading": "工程 Tasks",
        }
    return {
        "goal_heading": "Goal",
        "scope_heading": "Scope",
        "acceptance_heading": "Acceptance criteria",
        "tasks_heading": "Engineering tasks",
    }


def build_body(slug: str, prd_sections: dict[str, str], tasks: list[Task], language: str) -> str:
    zh = language.lower().startswith("zh")
    fallback = "未在 PRD 中单独说明。" if zh else "Not stated separately in the PRD."
    goal = section(prd_sections, "Goal", "目标", "Problem", "问题") or fallback
    scope = section(
        prd_sections,
        "Scope",
        "范围",
        "What to build",
        "功能范围",
        "User stories",
        "用户故事",
    ) or fallback
    acceptance = section(
        prd_sections, "Acceptance criteria", "验收标准", "Acceptance Criteria"
    ) or fallback
    checklist = "\n".join(
        f"- [{'x' if task.status == 'committed' else ' '}] "
        f"{task.task_id} {task.title}"
        for task in tasks
    )
    values = {
        **language_labels(language),
        "slug": slug,
        "goal": goal,
        "scope": scope,
        "acceptance": acceptance,
        "tasks": checklist,
    }
    return Template(TEMPLATE_PATH.read_text(encoding="utf-8")).substitute(values).strip() + "\n"


def delivery_sections(text: str) -> dict[str, str]:
    return split_sections(text)


def delivery_value(text: str, heading: str, key: str) -> str | None:
    value = delivery_sections(text).get(heading.lower(), "")
    match = re.search(rf"^\s*-\s+{re.escape(key)}:\s*(.+?)\s*$", value, re.MULTILINE)
    return match.group(1).strip() if match else None


def upsert_section(text: str, heading: str, body: str) -> str:
    if not text.strip():
        text = "# Delivery\n"
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$.*?(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    replacement = f"## {heading}\n\n{body.strip()}\n"
    if pattern.search(text):
        return pattern.sub(replacement, text).rstrip() + "\n"
    return text.rstrip() + "\n\n" + replacement


def write_delivery(path: Path, slug: str, number: int, url: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else "# Delivery\n"
    text = upsert_section(text, "Branch", slug)
    text = upsert_section(text, "GitHub Issue", f"- Number: {number}\n- URL: {url}")
    path.write_text(text, encoding="utf-8")


def normalize_github_url(url: str) -> str:
    return url.rstrip("/")


def api_base(github_url: str) -> str:
    normalized = normalize_github_url(github_url)
    return "https://api.github.com" if normalized == "https://github.com" else normalized + "/api/v3"


def request(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    return api_request(
        method,
        url,
        token,
        {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "team-spec-create-issue-github",
        },
        payload=payload,
        service="GitHub",
    )


def find_issue(
    github_url: str,
    repo: str,
    token: str,
    slug: str,
    tracked_number: int | None,
) -> dict[str, Any] | None:
    base = f"{api_base(github_url)}/repos/{repo}"
    marker = f"<!-- team-spec-slug: {slug} -->"
    if tracked_number:
        issue = request("GET", f"{base}/issues/{tracked_number}", token)
        if isinstance(issue, dict) and "pull_request" not in issue:
            if marker not in (issue.get("body") or ""):
                raise SystemExit(
                    f"Tracked GitHub Issue #{tracked_number} does not belong to Spec {slug}."
                )
            return issue
    issues = request("GET", f"{base}/issues?state=all&per_page=100", token)
    for issue in issues or []:
        if "pull_request" not in issue and marker in (issue.get("body") or ""):
            return issue
    return None


def execute(
    args: argparse.Namespace,
    repo: str,
    title: str,
    body: str,
    delivery_path: Path,
    tracked_number: int | None,
) -> dict[str, Any]:
    token = os.environ.get(args.token_env, "").strip()
    if not token:
        raise SystemExit(f"Missing token environment variable: {args.token_env}")
    existing = find_issue(
        args.github_url,
        repo,
        token,
        args.slug,
        None if args.force else tracked_number,
    )
    payload: dict[str, Any] = {"title": title, "body": body}
    if args.label:
        payload["labels"] = args.label
    if args.assignee:
        payload["assignees"] = args.assignee
    if args.milestone is not None:
        payload["milestone"] = args.milestone
    base = f"{api_base(args.github_url)}/repos/{repo}"
    if existing:
        issue = request("PATCH", f"{base}/issues/{existing['number']}", token, payload)
        action = "updated"
    else:
        issue = request("POST", f"{base}/issues", token, payload)
        action = "created"
    write_delivery(delivery_path, args.slug, int(issue["number"]), str(issue["html_url"]))
    return {
        "action": action,
        "issue_number": int(issue["number"]),
        "issue_url": str(issue["html_url"]),
    }


def main() -> int:
    args = parse_args()
    workspace = Path("team-spec") / "active" / args.slug
    prd_path = workspace / "prd" / "prd.md"
    if not prd_path.is_file():
        raise SystemExit(f"PRD does not exist: {prd_path}")
    prd_text = prd_path.read_text(encoding="utf-8")
    prd_sections = split_sections(prd_text)
    tasks = load_tasks(workspace)
    config = config_values()
    language = args.language or config.get("language") or "en-US"
    repo = infer_repo(args, config)
    title = args.title or first_heading(prd_text)
    if not title:
        raise SystemExit("Cannot derive Issue title from PRD; provide --title.")
    body = build_body(args.slug, prd_sections, tasks, language)
    delivery_path = workspace / "DELIVERY.md"
    delivery_text = (
        delivery_path.read_text(encoding="utf-8") if delivery_path.exists() else ""
    )
    tracked = delivery_value(delivery_text, "GitHub Issue", "Number")
    tracked_number = int(tracked) if tracked and tracked.isdigit() else None
    result: dict[str, Any] = {
        "mode": "execute" if args.execute else "dry-run",
        "slug": args.slug,
        "repo": repo,
        "title": title,
        "body": body,
        "task_count": len(tasks),
        "tracked_issue_number": tracked_number,
        "action": "create-or-sync",
    }
    if args.execute:
        try:
            result.update(
                execute(args, repo, title, body, delivery_path, tracked_number)
            )
        except ApiRequestError as error:
            raise SystemExit(str(error)) from error
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"Mode: {result['mode']}")
        print(f"Spec: {args.slug}")
        print(f"Repository: {repo}")
        print(f"Title: {title}")
        print(f"Tasks: {len(tasks)}")
        print(f"Action: {result['action']}")
        print("Body preview:")
        print(body)
        if result.get("issue_url"):
            print(f"Issue: {result['issue_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

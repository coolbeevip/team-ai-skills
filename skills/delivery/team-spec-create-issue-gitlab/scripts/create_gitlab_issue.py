#!/usr/bin/env python3
"""Create or synchronize one GitLab Issue for a complete team-spec workspace."""

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
        description="Create or synchronize one GitLab Issue for a complete Spec."
    )
    parser.add_argument("--slug", required=True, help="Slug under team-spec/active.")
    parser.add_argument("--project", help="Target project namespace/path or numeric ID.")
    parser.add_argument("--remote", help="Git remote used to infer the target project.")
    parser.add_argument("--title", help="Override the PRD-derived issue title.")
    parser.add_argument("--body-file", help="Use a prewritten localized Issue body.")
    parser.add_argument("--token-env", default="GITLAB_TOKEN")
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--milestone-id", type=int)
    parser.add_argument("--assignee-id", action="append", type=int, default=[])
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


def gitlab_url() -> str:
    value = os.environ.get("GITLAB_URL", "").strip()
    if not value:
        raise SystemExit("Missing GitLab base URL environment variable: GITLAB_URL")
    return value.rstrip("/")


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
    project = parsed.path.strip("/")
    if project.endswith(".git"):
        project = project[:-4]
    return parsed.hostname, project


def infer_project(
    args: argparse.Namespace, config: dict[str, str], base_url: str
) -> str:
    if args.project:
        return args.project.strip()
    remotes = remote_urls()
    remote = (
        args.remote
        or config.get("version_control.target_remote")
        or ("upstream" if "upstream" in remotes else None)
    )
    host = urllib.parse.urlparse(base_url).hostname or ""
    if remote:
        parsed = parse_remote(remotes.get(remote, ""))
        if not parsed or parsed[0] != host:
            raise SystemExit(f"Remote {remote!r} is not a GitLab remote for {host}.")
        return parsed[1]
    candidates = {
        parsed[1]
        for url in remotes.values()
        if (parsed := parse_remote(url)) and parsed[0] == host
    }
    if len(candidates) != 1:
        raise SystemExit("Cannot infer one GitLab project; provide --project or --remote.")
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


def build_body(
    slug: str,
    prd_sections: dict[str, str],
    tasks: list[Task],
    language: str,
    body_file: str | None = None,
) -> str:
    zh = language.lower().startswith("zh")
    fallback = "未在 PRD 中单独说明。" if zh else "Not stated separately in the PRD."
    values = {
        **language_labels(language),
        "slug": slug,
        "goal": section(prd_sections, "Goal", "目标", "Problem", "问题") or fallback,
        "scope": section(
            prd_sections,
            "Scope",
            "范围",
            "What to build",
            "功能范围",
            "User stories",
            "用户故事",
        )
        or fallback,
        "acceptance": section(
            prd_sections, "Acceptance criteria", "验收标准", "Acceptance Criteria"
        )
        or fallback,
        "tasks": "\n".join(
            f"- [{'x' if task.status == 'committed' else ' '}] "
            f"{task.task_id} {task.title}"
            for task in tasks
        ),
    }
    generated = (
        Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
        .substitute(values)
        .strip()
    )
    if not body_file:
        return generated + "\n"
    custom = Path(body_file).read_text(encoding="utf-8").strip()
    marker = f"<!-- team-spec-slug: {slug} -->"
    additions = []
    if marker not in custom:
        additions.append(marker)
    if any(task.task_id not in custom for task in tasks):
        additions.append(f"## {values['tasks_heading']}\n\n{values['tasks']}")
    return custom + ("\n\n" + "\n\n".join(additions) if additions else "") + "\n"


def delivery_value(text: str, heading: str, key: str) -> str | None:
    value = split_sections(text).get(heading.lower(), "")
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


def write_delivery(path: Path, slug: str, iid: int, url: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else "# Delivery\n"
    text = upsert_section(text, "Branch", slug)
    text = upsert_section(text, "GitLab Issue", f"- IID: {iid}\n- URL: {url}")
    path.write_text(text, encoding="utf-8")


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
        {"PRIVATE-TOKEN": token},
        payload=payload,
        service="GitLab",
    )


def project_api_base(base_url: str, project: str) -> str:
    return f"{base_url}/api/v4/projects/{urllib.parse.quote(project, safe='')}"


def find_issue(
    base_url: str,
    project: str,
    token: str,
    slug: str,
    tracked_iid: int | None,
) -> dict[str, Any] | None:
    base = project_api_base(base_url, project)
    marker = f"<!-- team-spec-slug: {slug} -->"
    if tracked_iid:
        issue = request("GET", f"{base}/issues/{tracked_iid}", token)
        if isinstance(issue, dict):
            if marker not in (issue.get("description") or ""):
                raise SystemExit(
                    f"Tracked GitLab Issue #{tracked_iid} does not belong to Spec {slug}."
                )
            return issue
    issues = request("GET", f"{base}/issues?scope=all&per_page=100", token)
    for issue in issues or []:
        if marker in (issue.get("description") or ""):
            return issue
    return None


def execute(
    args: argparse.Namespace,
    base_url: str,
    project: str,
    title: str,
    body: str,
    delivery_path: Path,
    tracked_iid: int | None,
) -> dict[str, Any]:
    token = os.environ.get(args.token_env, "").strip()
    if not token:
        raise SystemExit(f"Missing token environment variable: {args.token_env}")
    existing = find_issue(
        base_url,
        project,
        token,
        args.slug,
        None if args.force else tracked_iid,
    )
    payload: dict[str, Any] = {"title": title, "description": body}
    if args.label:
        payload["labels"] = ",".join(args.label)
    if args.assignee_id:
        payload["assignee_ids"] = args.assignee_id
    if args.milestone_id is not None:
        payload["milestone_id"] = args.milestone_id
    base = project_api_base(base_url, project)
    if existing:
        issue = request("PUT", f"{base}/issues/{existing['iid']}", token, payload)
        action = "updated"
    else:
        issue = request("POST", f"{base}/issues", token, payload)
        action = "created"
    write_delivery(delivery_path, args.slug, int(issue["iid"]), str(issue["web_url"]))
    return {
        "action": action,
        "issue_iid": int(issue["iid"]),
        "issue_url": str(issue["web_url"]),
    }


def main() -> int:
    args = parse_args()
    base_url = gitlab_url()
    workspace = Path("team-spec") / "active" / args.slug
    prd_path = workspace / "prd" / "prd.md"
    if not prd_path.is_file():
        raise SystemExit(f"PRD does not exist: {prd_path}")
    prd_text = prd_path.read_text(encoding="utf-8")
    prd_sections = split_sections(prd_text)
    tasks = load_tasks(workspace)
    config = config_values()
    language = (
        args.language
        or config.get("version_control.language")
        or config.get("language")
        or "en-US"
    )
    project = infer_project(args, config, base_url)
    title = args.title or first_heading(prd_text)
    if not title:
        raise SystemExit("Cannot derive Issue title from PRD; provide --title.")
    body = build_body(args.slug, prd_sections, tasks, language, args.body_file)
    delivery_path = workspace / "DELIVERY.md"
    delivery_text = (
        delivery_path.read_text(encoding="utf-8") if delivery_path.exists() else ""
    )
    tracked = delivery_value(delivery_text, "GitLab Issue", "IID")
    tracked_iid = int(tracked) if tracked and tracked.isdigit() else None
    result: dict[str, Any] = {
        "mode": "execute" if args.execute else "dry-run",
        "slug": args.slug,
        "project": project,
        "title": title,
        "body": body,
        "task_count": len(tasks),
        "tracked_issue_iid": tracked_iid,
        "action": "create-or-sync",
    }
    if args.execute:
        try:
            result.update(
                execute(
                    args,
                    base_url,
                    project,
                    title,
                    body,
                    delivery_path,
                    tracked_iid,
                )
            )
        except ApiRequestError as error:
            raise SystemExit(str(error)) from error
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"Mode: {result['mode']}")
        print(f"Spec: {args.slug}")
        print(f"Project: {project}")
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

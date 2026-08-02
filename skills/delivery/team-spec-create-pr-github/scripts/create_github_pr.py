#!/usr/bin/env python3
"""Create one GitHub Pull Request for all committed Tasks in a Spec."""

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
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "pr_body.md.tpl"


@dataclass
class ProjectRef:
    remote: str
    repo: str


@dataclass
class Task:
    task_id: str
    title: str
    status: str
    commit: str
    path: Path
    sections: dict[str, str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create one GitHub Pull Request for a complete Spec."
    )
    parser.add_argument("--slug", required=True, help="Slug under team-spec/active.")
    parser.add_argument("--github-url", default="https://github.com")
    parser.add_argument("--source-remote")
    parser.add_argument("--target-remote")
    parser.add_argument("--source-repo")
    parser.add_argument("--target-repo")
    parser.add_argument("--target-branch")
    parser.add_argument("--title")
    parser.add_argument("--body-file")
    parser.add_argument("--issue-number", type=int)
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--assignee", action="append", default=[])
    parser.add_argument("--language")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def run_git(args: list[str], check: bool = True) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def git_succeeds(args: list[str]) -> bool:
    try:
        return (
            subprocess.run(
                ["git", *args],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            == 0
        )
    except OSError:
        return False


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


def project_ref(
    remote: str, explicit_repo: str | None, host: str, remotes: dict[str, str]
) -> ProjectRef:
    if remote not in remotes:
        raise SystemExit(f"Git remote does not exist: {remote}")
    parsed = parse_remote(remotes[remote])
    if not parsed or parsed[0] != host:
        raise SystemExit(f"Remote {remote!r} is not a GitHub remote for {host}.")
    return ProjectRef(remote, explicit_repo.strip() if explicit_repo else parsed[1])


def infer_projects(
    args: argparse.Namespace, config: dict[str, str]
) -> tuple[ProjectRef, ProjectRef]:
    remotes = remote_urls()
    if not remotes:
        raise SystemExit("No git remotes found.")
    host = urllib.parse.urlparse(args.github_url).hostname or "github.com"
    target_remote = (
        args.target_remote
        or config.get("version_control.target_remote")
        or ("upstream" if "upstream" in remotes else "origin")
    )
    source_remote = (
        args.source_remote
        or config.get("version_control.source_remote")
        or ("origin" if "origin" in remotes else target_remote)
    )
    target = project_ref(target_remote, args.target_repo, host, remotes)
    source = project_ref(source_remote, args.source_repo, host, remotes)
    return source, target


def default_target_branch(target_remote: str, config: dict[str, str]) -> str:
    configured = config.get("version_control.trunk_branch")
    if configured:
        return configured
    symbolic = run_git(["symbolic-ref", f"refs/remotes/{target_remote}/HEAD"])
    if symbolic:
        return symbolic.rsplit("/", 1)[-1]
    for candidate in ("main", "master"):
        if git_succeeds(["show-ref", "--verify", "--quiet", f"refs/remotes/{target_remote}/{candidate}"]):
            return candidate
    raise SystemExit("Cannot infer target branch; provide --target-branch or configure trunk_branch.")


def split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip().lower()] = text[start:end].strip()
    return sections


def section(sections: dict[str, str], *names: str) -> str | None:
    for name in names:
        value = sections.get(name.lower())
        if value:
            return value
    return None


def first_heading(text: str) -> str | None:
    match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def task_identifier(path: Path, sections: dict[str, str]) -> str | None:
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
        identifier = task_identifier(path, sections)
        if not identifier:
            continue
        status = (section(sections, "Status") or "").splitlines()[0].strip().lower()
        commit = (section(sections, "Commit") or "").splitlines()[0].strip()
        if status != "committed":
            raise SystemExit(f"{identifier} is not committed: status={status or 'missing'}")
        if not commit or commit.lower() in {"pending", "none", "n/a"}:
            raise SystemExit(f"{identifier} has no recorded commit SHA.")
        tasks.append(
            Task(identifier, first_heading(text) or path.stem, status, commit, path, sections)
        )
    if not tasks:
        raise SystemExit(f"No T-numbered Task files found in {tasks_dir}")
    return sorted(tasks, key=lambda task: int(task.task_id[1:]))


def canonical_commit(value: str, task_id: str) -> str:
    commit = run_git(["rev-parse", "--verify", f"{value}^{{commit}}"])
    if not commit:
        raise SystemExit(f"{task_id} records an invalid commit: {value}")
    return commit


def worktree_issues() -> tuple[list[str], list[str]]:
    lines = (run_git(["status", "--porcelain"], check=False) or "").splitlines()
    non_spec: list[str] = []
    staged_spec: list[str] = []
    for line in lines:
        if len(line) < 4:
            continue
        status = line[:2]
        path = line[3:].split(" -> ")[-1]
        if path == "team-spec" or path.startswith("team-spec/"):
            if status[0] not in {" ", "?"}:
                staged_spec.append(line)
        else:
            non_spec.append(line)
    return non_spec, staged_spec


def validate_task_commits(
    tasks: list[Task], base_ref: str
) -> tuple[list[Task], list[str]]:
    branch_commits = (run_git(["rev-list", "--reverse", f"{base_ref}..HEAD"]) or "").splitlines()
    if not branch_commits:
        raise SystemExit(f"No commits found between {base_ref} and HEAD.")
    branch_set = set(branch_commits)
    task_set: set[str] = set()
    for task in tasks:
        task.commit = canonical_commit(task.commit, task.task_id)
        if task.commit not in branch_set:
            raise SystemExit(
                f"{task.task_id} commit {task.commit} is not in {base_ref}..HEAD."
            )
        task_set.add(task.commit)
    extra = [commit for commit in branch_commits if commit not in task_set]
    if extra:
        raise SystemExit(
            "Spec branch contains commits not mapped to Tasks: " + ", ".join(extra)
        )
    if len(task_set) != len(tasks):
        raise SystemExit("Multiple Tasks record the same commit; each Task needs one commit.")
    return tasks, branch_commits


def delivery_value(text: str, heading: str, key: str) -> str | None:
    value = split_sections(text).get(heading.lower(), "")
    match = re.search(rf"^\s*-\s+{re.escape(key)}:\s*(.+?)\s*$", value, re.MULTILINE)
    return match.group(1).strip() if match else None


def language_labels(language: str) -> dict[str, str]:
    if language.lower().startswith("zh"):
        return {
            "purpose_heading": "变更目的",
            "task_commits_heading": "Task 与 Commit",
            "testing_heading": "验证",
            "compatibility_heading": "兼容性与影响",
            "reviewer_notes_heading": "评审说明",
        }
    return {
        "purpose_heading": "Purpose",
        "task_commits_heading": "Tasks and commits",
        "testing_heading": "Testing",
        "compatibility_heading": "Compatibility and impact",
        "reviewer_notes_heading": "Reviewer notes",
    }


def build_body(
    args: argparse.Namespace,
    prd_sections: dict[str, str],
    tasks: list[Task],
    language: str,
    issue_number: int | None,
) -> str:
    task_lines = "\n".join(
        f"- `{task.task_id}` {task.title} — `{task.commit}`" for task in tasks
    )
    testing_parts: list[str] = []
    for task in tasks:
        evidence = section(
            task.sections,
            "Commands Run",
            "Verification",
            "Validation",
            "验证命令",
            "Acceptance Criteria Coverage",
        )
        if evidence:
            testing_parts.append(f"### {task.task_id}\n\n{evidence}")
    zh = language.lower().startswith("zh")
    fallback = "未在 PRD 中单独说明。" if zh else "Not stated separately in the PRD."
    values = {
        **language_labels(language),
        "slug": args.slug,
        "purpose": section(prd_sections, "Goal", "目标", "Problem", "问题") or fallback,
        "closing_line": f"Fixes #{issue_number}" if issue_number else "",
        "task_commits": task_lines,
        "testing": "\n\n".join(testing_parts)
        or ("见各 Task 验证记录。" if zh else "See each Task verification record."),
        "compatibility": section(
            prd_sections,
            "Compatibility / impact",
            "Compatibility",
            "兼容性",
            "影响",
            "Risks",
            "风险",
        )
        or fallback,
        "reviewer_notes": section(
            prd_sections, "Reviewer notes", "Notes", "评审说明", "备注"
        )
        or fallback,
    }
    generated = Template(TEMPLATE_PATH.read_text(encoding="utf-8")).substitute(values).strip()
    if not args.body_file:
        return generated + "\n"
    custom = Path(args.body_file).read_text(encoding="utf-8").strip()
    marker = f"<!-- team-spec-slug: {args.slug} -->"
    additions = []
    if marker not in custom:
        additions.append(marker)
    if any(task.task_id not in custom for task in tasks):
        additions.append(f"## {values['task_commits_heading']}\n\n{task_lines}")
    if issue_number and f"#{issue_number}" not in custom:
        additions.append(f"Fixes #{issue_number}")
    return custom + ("\n\n" + "\n\n".join(additions) if additions else "") + "\n"


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


def write_delivery(
    path: Path,
    branch: str,
    number: int,
    url: str,
    target_branch: str,
    tasks: list[Task],
) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else "# Delivery\n"
    text = upsert_section(text, "Branch", branch)
    text = upsert_section(
        text,
        "Task Commits",
        "\n".join(f"- {task.task_id}: `{task.commit}` — {task.title}" for task in tasks),
    )
    text = upsert_section(
        text,
        "GitHub Pull Request",
        f"- Number: {number}\n- URL: {url}\n- Target Branch: {target_branch}",
    )
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
            "User-Agent": "team-spec-create-pr-github",
        },
        payload=payload,
        service="GitHub",
    )


def find_existing_pr(
    args: argparse.Namespace,
    source: ProjectRef,
    target: ProjectRef,
    branch: str,
    target_branch: str,
    token: str,
) -> dict[str, Any] | None:
    owner = source.repo.split("/", 1)[0]
    query = urllib.parse.urlencode(
        {"state": "open", "head": f"{owner}:{branch}", "base": target_branch}
    )
    pulls = request(
        "GET",
        f"{api_base(args.github_url)}/repos/{target.repo}/pulls?{query}",
        token,
    )
    return pulls[0] if pulls else None


def execute(
    args: argparse.Namespace,
    plan: dict[str, Any],
    source: ProjectRef,
    target: ProjectRef,
    tasks: list[Task],
    delivery_path: Path,
) -> dict[str, Any]:
    token = os.environ.get(args.token_env, "").strip()
    if not token:
        raise SystemExit(f"Missing token environment variable: {args.token_env}")
    subprocess.run(
        ["git", "push", "-u", source.remote, plan["branch"]],
        check=True,
    )
    existing = find_existing_pr(
        args, source, target, plan["branch"], plan["target_branch"], token
    )
    if existing:
        pull = existing
        action = "existing"
    else:
        head = f"{source.repo.split('/', 1)[0]}:{plan['branch']}"
        payload: dict[str, Any] = {
            "title": plan["title"],
            "body": plan["body"],
            "head": head,
            "base": plan["target_branch"],
            "draft": args.draft,
        }
        pull = request(
            "POST",
            f"{api_base(args.github_url)}/repos/{target.repo}/pulls",
            token,
            payload,
        )
        action = "created"
    if args.assignee:
        request(
            "POST",
            f"{api_base(args.github_url)}/repos/{target.repo}/issues/{pull['number']}/assignees",
            token,
            {"assignees": args.assignee},
        )
    write_delivery(
        delivery_path,
        plan["branch"],
        int(pull["number"]),
        str(pull["html_url"]),
        plan["target_branch"],
        tasks,
    )
    return {
        "action": action,
        "pr_number": int(pull["number"]),
        "pr_url": str(pull["html_url"]),
    }


def main() -> int:
    args = parse_args()
    config = config_values()
    workspace = Path("team-spec") / "active" / args.slug
    prd_path = workspace / "prd" / "prd.md"
    if not prd_path.is_file():
        raise SystemExit(f"PRD does not exist: {prd_path}")
    expected_branch = args.slug
    branch = run_git(["branch", "--show-current"]) or ""
    if branch != expected_branch:
        raise SystemExit(
            f"Current branch must be {expected_branch!r}; found {branch or 'detached HEAD'}."
        )
    non_spec, staged_spec = worktree_issues()
    if non_spec:
        raise SystemExit("Non-team-spec worktree changes remain: " + "; ".join(non_spec))
    if staged_spec:
        raise SystemExit("team-spec files must not be staged: " + "; ".join(staged_spec))
    source, target = infer_projects(args, config)
    target_branch = args.target_branch or default_target_branch(target.remote, config)
    base_ref = f"{target.remote}/{target_branch}"
    if not git_succeeds(["rev-parse", "--verify", f"{base_ref}^{{commit}}"]):
        raise SystemExit(f"Target branch ref is unavailable locally: {base_ref}")
    tasks, branch_commits = validate_task_commits(load_tasks(workspace), base_ref)
    prd_text = prd_path.read_text(encoding="utf-8")
    prd_sections = split_sections(prd_text)
    title = args.title or first_heading(prd_text)
    if not title:
        raise SystemExit("Cannot derive PR title from PRD; provide --title.")
    delivery_path = workspace / "DELIVERY.md"
    delivery_text = (
        delivery_path.read_text(encoding="utf-8") if delivery_path.exists() else ""
    )
    tracked_issue = delivery_value(delivery_text, "GitHub Issue", "Number")
    issue_number = args.issue_number or (
        int(tracked_issue) if tracked_issue and tracked_issue.isdigit() else None
    )
    language = (
        args.language
        or config.get("version_control.language")
        or config.get("language")
        or "en-US"
    )
    body = build_body(args, prd_sections, tasks, language, issue_number)
    plan: dict[str, Any] = {
        "mode": "execute" if args.execute else "dry-run",
        "slug": args.slug,
        "branch": branch,
        "source_repo": source.repo,
        "source_remote": source.remote,
        "target_repo": target.repo,
        "target_remote": target.remote,
        "target_branch": target_branch,
        "base_ref": base_ref,
        "title": title,
        "body": body,
        "task_count": len(tasks),
        "task_commits": [
            {"task_id": task.task_id, "title": task.title, "commit": task.commit}
            for task in tasks
        ],
        "branch_commits": branch_commits,
        "issue_number": issue_number,
    }
    if args.execute:
        try:
            plan.update(execute(args, plan, source, target, tasks, delivery_path))
        except (ApiRequestError, subprocess.CalledProcessError) as error:
            raise SystemExit(str(error)) from error
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"Mode: {plan['mode']}")
        print(f"Spec: {args.slug}")
        print(f"Branch: {branch}")
        print(f"Target: {target.repo}:{target_branch}")
        print(f"Tasks: {len(tasks)}")
        for task in tasks:
            print(f"- {task.task_id}: {task.commit} {task.title}")
        print("Body preview:")
        print(body)
        if plan.get("pr_url"):
            print(f"Pull Request: {plan['pr_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

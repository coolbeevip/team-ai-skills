#!/usr/bin/env python3
"""Publish local team-spec issue drafts to GitLab Issues.

The script is intentionally dependency-free so agents can run it in most
project repositories without generating ad hoc GitLab API code.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from string import Template


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
LOCAL_KEY_RE = re.compile(r"^(\d+[-_][A-Za-z0-9][A-Za-z0-9_.-]*\.md)$")
ISSUE_REF_RE = re.compile(r"#(\d+)")
LOCAL_REF_RE = re.compile(r"(\d+[-_][A-Za-z0-9][A-Za-z0-9_.-]*\.md)")
PUBLISH_SECTION = "## Publish Status"
BODY_TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "issue_body.md.tpl"
GENERIC_TITLE_PREFIXES = {
    "fix",
    "update",
    "change",
    "improve",
    "refactor",
    "task",
    "todo",
    "work",
    "misc",
}


@dataclass
class IssueDraft:
    path: Path
    key: str
    title: str
    title_source: str
    description: str
    blocked_by: list[str] = field(default_factory=list)
    title_issues: list[str] = field(default_factory=list)
    status: str = "pending"
    remote_url: str | None = None
    remote_iid: int | None = None
    error: str | None = None

    @property
    def has_publish_record(self) -> bool:
        return self.status in {"created", "skipped"} and (
            self.remote_url is not None or self.remote_iid is not None
        )


class GitLabError(RuntimeError):
    pass


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish team-spec issue drafts to GitLab Issues."
    )
    parser.add_argument("--issues-dir", help="Directory containing local issue drafts.")
    parser.add_argument(
        "--slug",
        help="Slug under team-spec/active/issues/{slug}. Ignored when --issues-dir is set.",
    )
    parser.add_argument(
        "--issue",
        action="append",
        default=[],
        help="Specific issue draft to publish. Can be a filename, path, or draft identifier. Repeat to publish multiple specific issues.",
    )
    parser.add_argument(
        "--project",
        help="GitLab project path namespace/project or numeric project ID.",
    )
    parser.add_argument("--token-env", default="GITLAB_TOKEN")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Create issues. Omit for dry-run preview.",
    )
    parser.add_argument("--label", action="append", default=[], help="Label to add.")
    parser.add_argument("--milestone-id", type=int)
    parser.add_argument("--assignee-id", action="append", type=int, default=[])
    parser.add_argument("--remote", help="Force a git remote name for project inference.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore local Publish Status and re-check GitLab before creating.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def issue_dir_from_args(args: argparse.Namespace) -> Path:
    if args.issues_dir:
        return Path(args.issues_dir)
    if args.slug:
        return Path("team-spec") / "active" / "issues" / args.slug
    raise SystemExit("Provide --issues-dir or --slug.")


def normalize_gitlab_url(url: str) -> str:
    return url.rstrip("/")


def gitlab_url_from_env() -> str:
    url = os.environ.get("GITLAB_URL", "").strip()
    if not url:
        raise SystemExit("Missing GitLab base URL env var: GITLAB_URL")
    return normalize_gitlab_url(url)


def remote_urls() -> dict[str, str]:
    output = run_git(["remote", "-v"])
    remotes: dict[str, str] = {}
    if not output:
        return remotes
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and "(fetch)" in line:
            remotes[parts[0]] = parts[1]
    return remotes


def remote_host_and_project(url: str) -> tuple[str, str] | None:
    if url.startswith("git@"):
        match = re.match(r"git@([^:]+):(.+?)(?:\.git)?$", url)
        if not match:
            return None
        return match.group(1), match.group(2)

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme in {"http", "https", "ssh"} and parsed.netloc and parsed.path:
        project = parsed.path.strip("/")
        if project.endswith(".git"):
            project = project[:-4]
        return parsed.hostname or parsed.netloc, project

    return None


def infer_project(args: argparse.Namespace) -> str:
    if args.project:
        return args.project.strip()

    remotes = remote_urls()
    if not remotes:
        raise SystemExit("Cannot infer project: no git remotes found.")

    gitlab_host = urllib.parse.urlparse(args.gitlab_url).hostname or "gitlab.com"

    def as_project(remote_name: str) -> tuple[str, str] | None:
        url = remotes.get(remote_name)
        parsed = remote_host_and_project(url) if url else None
        if not parsed:
            return None
        host, project = parsed
        if host != gitlab_host:
            raise SystemExit(
                f"Remote {remote_name} host {host} does not match GitLab host {gitlab_host}."
            )
        return remote_name, project

    if args.remote:
        forced = as_project(args.remote)
        if not forced:
            raise SystemExit(f"Remote {args.remote} is not a valid GitLab remote.")
        return forced[1]

    upstream = as_project("upstream")
    if upstream:
        return upstream[1]

    branch_remote = run_git(["config", "--get", "branch." + current_branch() + ".remote"])
    if branch_remote:
        tracked = as_project(branch_remote)
        if tracked:
            return tracked[1]

    gitlab_projects: list[tuple[str, str]] = []
    for name in remotes:
        parsed = remote_host_and_project(remotes[name])
        if parsed and parsed[0] == gitlab_host:
            gitlab_projects.append((name, parsed[1]))

    unique_projects = sorted(set(project for _, project in gitlab_projects))
    if len(unique_projects) == 1:
        return unique_projects[0]

    details = ", ".join(f"{name}={project}" for name, project in gitlab_projects)
    raise SystemExit(
        "Cannot infer a unique GitLab project. Provide --project or --remote. "
        f"Candidates: {details or 'none'}"
    )


def current_branch() -> str:
    branch = run_git(["branch", "--show-current"])
    return branch or "HEAD"


def split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[title] = text[start:end].strip()
    return sections


def resolve_title(path: Path, text: str, sections: dict[str, str]) -> tuple[str, str]:
    first_heading = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if first_heading:
        return first_heading.group(1).strip(), "heading"
    if "Title" in sections and sections["Title"].strip():
        return sections["Title"].splitlines()[0].strip(), "title_section"
    return path.stem, "filename"


def validate_title(title: str, source: str, path: Path) -> list[str]:
    normalized = re.sub(r"\s+", " ", title).strip()
    issues: list[str] = []
    if not normalized:
        issues.append(f"{path.name}: title is empty.")
        return issues
    if source == "filename":
        issues.append(f"{path.name}: title falls back to the filename; add an explicit # heading or Title section.")
    if len(normalized) < 12:
        issues.append(f"{path.name}: title is too short ({len(normalized)} chars).")
    if len(normalized) > 120:
        issues.append(f"{path.name}: title is too long ({len(normalized)} chars).")

    contains_cjk = bool(re.search(r"[\u4e00-\u9fff]", normalized))
    words = [word for word in normalized.split(" ") if word]
    if contains_cjk:
        if len(normalized) < 6:
            issues.append(f"{path.name}: Chinese title is too short to be clear.")
    else:
        if len(words) < 3:
            issues.append(f"{path.name}: title should use at least 3 words.")
        first_word = words[0].rstrip(":").lower() if words else ""
        if first_word in GENERIC_TITLE_PREFIXES and len(words) < 4:
            issues.append(f"{path.name}: title is too generic; include a clearer object or scope.")

    return issues


def parse_publish_status(sections: dict[str, str]) -> dict[str, str]:
    publish_status = sections.get("Publish Status", "")
    values: dict[str, str] = {}
    for line in publish_status.splitlines():
        match = re.match(r"^\s*[-*]\s+([^:]+):\s*(.*?)\s*$", line)
        if match:
            values[match.group(1).strip().lower()] = match.group(2).strip()
    return values


def parse_blockers(section: str, known_keys: set[str]) -> list[str]:
    blockers: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped or "none" in stripped.lower():
            continue
        for key in LOCAL_REF_RE.findall(stripped):
            if key in known_keys:
                blockers.append(key)
        for issue_number in ISSUE_REF_RE.findall(stripped):
            matching = [key for key in known_keys if key.startswith(issue_number + "-")]
            blockers.extend(matching)
    return sorted(set(blockers))


def load_drafts(issue_dir: Path) -> list[IssueDraft]:
    if not issue_dir.exists():
        raise SystemExit(f"Issue directory does not exist: {issue_dir}")

    paths = sorted(path for path in issue_dir.glob("*.md") if path.is_file())
    if not paths:
        raise SystemExit(f"No Markdown issue drafts found in {issue_dir}")

    known_keys = {path.name for path in paths if LOCAL_KEY_RE.match(path.name)}
    drafts: list[IssueDraft] = []
    for path in paths:
        if not LOCAL_KEY_RE.match(path.name):
            continue
        text = path.read_text(encoding="utf-8")
        sections = split_sections(text)
        blocked_by = parse_blockers(sections.get("Blocked by", ""), known_keys)
        title, title_source = resolve_title(path, text, sections)
        description = render_issue_body(path.name, sections)
        publish_status = parse_publish_status(sections)
        remote_iid = None
        if publish_status.get("gitlab iid", "").isdigit():
            remote_iid = int(publish_status["gitlab iid"])
        drafts.append(
            IssueDraft(
                path=path,
                key=path.name,
                title=title,
                title_source=title_source,
                description=description,
                blocked_by=blocked_by,
                title_issues=validate_title(title, title_source, path),
                status=publish_status.get("status", "pending").lower() or "pending",
                remote_url=publish_status.get("gitlab url") or None,
                remote_iid=remote_iid,
                error=publish_status.get("error") or None,
            )
        )
    return drafts


def draft_matches_selector(draft: IssueDraft, selector: str) -> bool:
    normalized = selector.strip()
    path_str = draft.path.as_posix()
    candidates = {
        draft.key,
        draft.path.name,
        draft.path.stem,
        path_str,
        str(draft.path),
    }
    if normalized in candidates:
        return True
    if normalized.endswith(".md") and Path(normalized).name == draft.path.name:
        return True
    if normalized.isdigit():
        prefix = draft.path.stem.split("-", 1)[0]
        return prefix == normalized
    return False


def filter_drafts(drafts: list[IssueDraft], selectors: list[str]) -> list[IssueDraft]:
    if not selectors:
        return drafts
    selected: list[IssueDraft] = []
    missing: list[str] = []
    for selector in selectors:
        matched = [draft for draft in drafts if draft_matches_selector(draft, selector)]
        if not matched:
            missing.append(selector)
            continue
        if len(matched) > 1:
            raise SystemExit(
                f"Selector {selector!r} matched multiple issues: {', '.join(draft.key for draft in matched)}"
            )
        selected.append(matched[0])
    if missing:
        raise SystemExit(f"Could not find issue draft(s): {', '.join(missing)}")
    return selected


def section_text(text: str | None, fallback: str) -> str:
    if text and text.strip():
        return text.strip()
    return fallback


def metadata_lines(sections: dict[str, str]) -> str:
    lines: list[str] = []
    parent = sections.get("Parent", "").strip()
    issue_type = sections.get("Type", "").strip()
    if parent:
        lines.append(f"- Parent: {parent}")
    if issue_type:
        lines.append(f"- Type: {issue_type}")
    return "\n".join(lines) if lines else "- No explicit parent or type."


def render_issue_body(key: str, sections: dict[str, str]) -> str:
    template = Template(BODY_TEMPLATE_PATH.read_text(encoding="utf-8"))
    rendered = template.safe_substitute(
        summary=section_text(
            sections.get("What to build"),
            "No summary was provided in the local issue draft.",
        ),
        scope=metadata_lines(sections),
        acceptance_criteria=section_text(
            sections.get("Acceptance criteria"),
            "- [ ] Acceptance criteria were not provided in the local issue draft.",
        ),
        dependencies=section_text(
            sections.get("Blocked by"),
            "- None - can start immediately",
        ),
        implementation_notes=section_text(
            sections.get("Notes"),
            "- No additional notes.",
        ),
        local_issue_key=key,
    ).rstrip()
    return rendered + "\n"


def topo_sort(drafts: list[IssueDraft]) -> list[IssueDraft]:
    by_key = {draft.key: draft for draft in drafts}
    temp: set[str] = set()
    perm: set[str] = set()
    ordered: list[IssueDraft] = []

    def visit(key: str, stack: list[str]) -> None:
        if key in perm:
            return
        if key in temp:
            cycle = " -> ".join([*stack, key])
            raise SystemExit(f"Cycle detected in Blocked by dependencies: {cycle}")
        temp.add(key)
        for blocker in by_key[key].blocked_by:
            if blocker in by_key:
                visit(blocker, [*stack, key])
        temp.remove(key)
        perm.add(key)
        ordered.append(by_key[key])

    for draft in drafts:
        visit(draft.key, [])
    return ordered


def no_proxy_entries() -> list[str]:
    value = os.environ.get("no_proxy") or os.environ.get("NO_PROXY") or ""
    return [entry.strip() for entry in value.split(",") if entry.strip()]


def host_matches_no_proxy(host: str, entry: str) -> bool:
    host = host.lower().strip("[]")
    entry = entry.lower()
    if entry == "*":
        return True
    if "/" in entry:
        try:
            return ipaddress.ip_address(host) in ipaddress.ip_network(entry, strict=False)
        except ValueError:
            return False
    if entry.startswith("*."):
        suffix = entry[1:]
        return host.endswith(suffix)
    if entry.startswith("."):
        return host == entry[1:] or host.endswith(entry)
    return host == entry or host.endswith(f".{entry}")


def should_bypass_proxy(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    if not host:
        return False
    return any(host_matches_no_proxy(host, entry) for entry in no_proxy_entries())


def api_request(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    data = None
    headers = {"PRIVATE-TOKEN": token}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    print_request_debug(method, url, payload)
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    opener = (
        urllib.request.build_opener(urllib.request.ProxyHandler({}))
        if should_bypass_proxy(url)
        else urllib.request.build_opener()
    )
    try:
        with opener.open(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise GitLabError(f"GitLab API {method} {url} failed: {exc.code} {body}") from exc
    except urllib.error.URLError as exc:
        raise GitLabError(f"GitLab API {method} {url} failed: {exc.reason}") from exc


def print_request_debug(
    method: str,
    url: str,
    payload: dict[str, Any] | None,
) -> None:
    request_info = {
        "method": method,
        "url": url,
        "payload": payload or {},
    }
    print(
        "GitLab request: "
        + json.dumps(request_info, ensure_ascii=False, sort_keys=True),
        file=sys.stderr,
    )


def project_api_base(gitlab_url: str, project: str) -> str:
    encoded = urllib.parse.quote(project, safe="")
    return f"{normalize_gitlab_url(gitlab_url)}/api/v4/projects/{encoded}"


def find_existing_issue(
    gitlab_url: str,
    project: str,
    token: str,
    draft: IssueDraft,
) -> dict[str, Any] | None:
    query = urllib.parse.urlencode({"search": draft.key, "scope": "all", "per_page": "100"})
    url = f"{project_api_base(gitlab_url, project)}/issues?{query}"
    issues = api_request("GET", url, token)
    candidates = [
        issue
        for issue in issues
        if f"Local-Issue-Key: {draft.key}" in (issue.get("description") or "")
    ]
    title_matches = [
        issue for issue in candidates if (issue.get("title") or "").strip() == draft.title
    ]
    if len(title_matches) == 1:
        return title_matches[0]
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        raise GitLabError(f"Multiple remote issues match Local-Issue-Key {draft.key}.")
    return None


def create_issue(
    gitlab_url: str,
    project: str,
    token: str,
    draft: IssueDraft,
    args: argparse.Namespace,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": draft.title,
        "description": draft.description,
    }
    if args.label:
        payload["labels"] = ",".join(args.label)
    if args.milestone_id is not None:
        payload["milestone_id"] = args.milestone_id
    if args.assignee_id:
        payload["assignee_ids"] = args.assignee_id
    return api_request(
        "POST",
        f"{project_api_base(gitlab_url, project)}/issues",
        token,
        payload,
    )


def write_status(draft: IssueDraft) -> None:
    text = draft.path.read_text(encoding="utf-8")
    body = [
        PUBLISH_SECTION,
        "",
        f"- Status: {draft.status}",
        f"- Updated At: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
    ]
    if draft.remote_iid is not None:
        body.append(f"- GitLab IID: {draft.remote_iid}")
    if draft.remote_url:
        body.append(f"- GitLab URL: {draft.remote_url}")
    if draft.error:
        body.append(f"- Error: {draft.error}")
    replacement = "\n".join(body).rstrip() + "\n"

    if PUBLISH_SECTION in text:
        pattern = re.compile(
            rf"^##\s+Publish Status\s*$.*?(?=^##\s+|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        text = pattern.sub(replacement, text).rstrip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + replacement
    draft.path.write_text(text, encoding="utf-8")


def publish(args: argparse.Namespace) -> dict[str, Any]:
    args.gitlab_url = gitlab_url_from_env()
    issue_dir = issue_dir_from_args(args)
    project = infer_project(args)
    drafts = topo_sort(filter_drafts(load_drafts(issue_dir), args.issue))
    token = os.environ.get(args.token_env)

    if args.execute and not token:
        raise SystemExit(f"Missing token env var: {args.token_env}")

    title_issues = [issue for draft in drafts for issue in draft.title_issues]
    if title_issues:
        prefix = "Title validation failed:\n"
        message = prefix + "\n".join(f"- {issue}" for issue in title_issues)
        raise SystemExit(message)

    for draft in drafts:
        if draft.has_publish_record and not args.force:
            draft.status = "skipped"
            continue
        if not args.execute:
            draft.status = "planned"
            continue
        try:
            assert token is not None
            existing = find_existing_issue(args.gitlab_url, project, token, draft)
            if existing:
                draft.status = "skipped"
                draft.remote_iid = existing.get("iid")
                draft.remote_url = existing.get("web_url")
            else:
                created = create_issue(args.gitlab_url, project, token, draft, args)
                draft.status = "created"
                draft.remote_iid = created.get("iid")
                draft.remote_url = created.get("web_url")
            write_status(draft)
        except GitLabError as exc:
            draft.status = "failed"
            draft.error = str(exc)
            write_status(draft)

    counts: dict[str, int] = {}
    for draft in drafts:
        counts[draft.status] = counts.get(draft.status, 0) + 1

    return {
        "mode": "execute" if args.execute else "dry-run",
        "gitlab_url": normalize_gitlab_url(args.gitlab_url),
        "project": project,
        "issues_dir": str(issue_dir),
        "selected_issues": args.issue,
        "counts": counts,
        "issues": [
            {
                "key": draft.key,
                "title": draft.title,
                "title_source": draft.title_source,
                "blocked_by": draft.blocked_by,
                "title_issues": draft.title_issues,
                "status": draft.status,
                "remote_iid": draft.remote_iid,
                "remote_url": draft.remote_url,
                "error": draft.error,
            }
            for draft in drafts
        ],
    }


def print_text_summary(result: dict[str, Any]) -> None:
    print(f"Mode: {result['mode']}")
    print(f"GitLab: {result['gitlab_url']}")
    print(f"Project: {result['project']}")
    print(f"Issues: {result['issues_dir']}")
    print(f"Counts: {result['counts']}")
    print("")
    for issue in result["issues"]:
        suffix = f" -> {issue['remote_url']}" if issue.get("remote_url") else ""
        blockers = ", ".join(issue["blocked_by"]) or "None"
        print(f"- [{issue['status']}] {issue['key']} {issue['title']}{suffix}")
        print(f"  Blocked by: {blockers}")
        if issue.get("error"):
            print(f"  Error: {issue['error']}")


def main() -> int:
    args = parse_args()
    try:
        result = publish(args)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_text_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

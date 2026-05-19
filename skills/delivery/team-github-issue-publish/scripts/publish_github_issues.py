#!/usr/bin/env python3
"""Publish local team-spec issue drafts to GitHub Issues.

The script is dependency-free so agents can reuse a stable implementation
instead of generating ad hoc GitHub API code for every publishing run.
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
    body: str
    blocked_by: list[str] = field(default_factory=list)
    title_issues: list[str] = field(default_factory=list)
    status: str = "pending"
    remote_url: str | None = None
    remote_number: int | None = None
    error: str | None = None

    @property
    def has_publish_record(self) -> bool:
        return self.status in {"created", "skipped"} and (
            self.remote_url is not None or self.remote_number is not None
        )


class GitHubError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish team-spec issue drafts to GitHub Issues."
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
    parser.add_argument("--github-url", default="https://github.com")
    parser.add_argument("--repo", help="GitHub repo path owner/repo.")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Create issues. Omit for dry-run preview.",
    )
    parser.add_argument("--label", action="append", default=[], help="Label to add.")
    parser.add_argument("--milestone", type=int, help="Milestone number.")
    parser.add_argument("--assignee", action="append", default=[], help="Assignee login.")
    parser.add_argument("--remote", help="Force a git remote name for repo inference.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore local Publish Status and re-check GitHub before creating.",
    )
    parser.add_argument(
        "--language",
        help="Output language for rendered issue bodies. Defaults to team-spec/config.yml language, then en-US.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
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


def issue_dir_from_args(args: argparse.Namespace) -> Path:
    if args.issues_dir:
        return Path(args.issues_dir)
    if args.slug:
        return Path("team-spec") / "active" / "issues" / args.slug
    raise SystemExit("Provide --issues-dir or --slug.")


def normalize_github_url(url: str) -> str:
    return url.rstrip("/")


def api_base(github_url: str) -> str:
    normalized = normalize_github_url(github_url)
    if normalized == "https://github.com":
        return "https://api.github.com"
    return normalized + "/api/v3"


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


def remote_host_and_repo(url: str) -> tuple[str, str] | None:
    if url.startswith("git@"):
        match = re.match(r"git@([^:]+):(.+?)(?:\.git)?$", url)
        if not match:
            return None
        return match.group(1), match.group(2)

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme in {"http", "https", "ssh"} and parsed.netloc and parsed.path:
        repo = parsed.path.strip("/")
        if repo.endswith(".git"):
            repo = repo[:-4]
        return parsed.hostname or parsed.netloc, repo

    return None


def current_branch() -> str:
    branch = run_git(["branch", "--show-current"])
    return branch or "HEAD"


def infer_repo(args: argparse.Namespace) -> str:
    if args.repo:
        return args.repo.strip()

    remotes = remote_urls()
    if not remotes:
        raise SystemExit("Cannot infer repo: no git remotes found.")

    github_host = urllib.parse.urlparse(args.github_url).hostname or "github.com"

    def as_repo(remote_name: str) -> tuple[str, str] | None:
        url = remotes.get(remote_name)
        parsed = remote_host_and_repo(url) if url else None
        if not parsed:
            return None
        host, repo = parsed
        if host != github_host:
            raise SystemExit(
                f"Remote {remote_name} host {host} does not match GitHub host {github_host}."
            )
        return remote_name, repo

    if args.remote:
        forced = as_repo(args.remote)
        if not forced:
            raise SystemExit(f"Remote {args.remote} is not a valid GitHub remote.")
        return forced[1]

    upstream = as_repo("upstream")
    if upstream:
        return upstream[1]

    branch_remote = run_git(["config", "--get", "branch." + current_branch() + ".remote"])
    if branch_remote:
        tracked = as_repo(branch_remote)
        if tracked:
            return tracked[1]

    github_repos: list[tuple[str, str]] = []
    for name, url in remotes.items():
        parsed = remote_host_and_repo(url)
        if parsed and parsed[0] == github_host:
            github_repos.append((name, parsed[1]))

    unique_repos = sorted(set(repo for _, repo in github_repos))
    if len(unique_repos) == 1:
        return unique_repos[0]

    details = ", ".join(f"{name}={repo}" for name, repo in github_repos)
    raise SystemExit(
        "Cannot infer a unique GitHub repo. Provide --repo or --remote. "
        f"Candidates: {details or 'none'}"
    )


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


def language_from_config(explicit: str | None) -> str:
    if explicit:
        return explicit.strip()
    config = Path("team-spec") / "config.yml"
    if not config.exists():
        return "en-US"
    for line in config.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*language\s*:\s*['\"]?([^'\"#]+)", line)
        if match:
            return match.group(1).strip() or "en-US"
    return "en-US"


def is_chinese_language(language: str) -> bool:
    return language.lower().startswith("zh")


def section_value(sections: dict[str, str], *names: str) -> str | None:
    normalized = {key.lower(): value for key, value in sections.items()}
    for name in names:
        value = normalized.get(name.lower())
        if value:
            return value
    return None


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


def section_text(text: str | None, fallback: str) -> str:
    if text and text.strip():
        return text.strip()
    return fallback


def metadata_lines(sections: dict[str, str], language: str) -> str:
    lines: list[str] = []
    parent = (section_value(sections, "Parent", "父需求", "来源") or "").strip()
    issue_type = (section_value(sections, "Type", "类型") or "").strip()
    parent_label = "父需求" if is_chinese_language(language) else "Parent"
    type_label = "类型" if is_chinese_language(language) else "Type"
    if parent:
        lines.append(f"- {parent_label}: {parent}")
    if issue_type:
        lines.append(f"- {type_label}: {issue_type}")
    fallback = "- 未记录父需求或类型。" if is_chinese_language(language) else "- No explicit parent or type."
    return "\n".join(lines) if lines else fallback


def issue_body_labels(language: str) -> dict[str, str]:
    if is_chinese_language(language):
        return {
            "summary_heading": "摘要",
            "scope_heading": "范围",
            "acceptance_criteria_heading": "验收标准",
            "dependencies_heading": "依赖",
            "implementation_notes_heading": "实现备注",
            "source_heading": "来源",
            "missing_summary": "本地 issue 草稿未提供摘要。",
            "missing_acceptance": "- [ ] 本地 issue 草稿未提供验收标准。",
            "missing_dependencies": "- 无依赖，可立即开始",
            "missing_notes": "- 无补充说明。",
        }
    return {
        "summary_heading": "Summary",
        "scope_heading": "Scope",
        "acceptance_criteria_heading": "Acceptance criteria",
        "dependencies_heading": "Dependencies",
        "implementation_notes_heading": "Implementation notes",
        "source_heading": "Source",
        "missing_summary": "No summary was provided in the local issue draft.",
        "missing_acceptance": "- [ ] Acceptance criteria were not provided in the local issue draft.",
        "missing_dependencies": "- None - can start immediately",
        "missing_notes": "- No additional notes.",
    }


def render_issue_body(key: str, sections: dict[str, str], language: str) -> str:
    template = Template(BODY_TEMPLATE_PATH.read_text(encoding="utf-8"))
    labels = issue_body_labels(language)
    rendered = template.safe_substitute(
        **labels,
        summary=section_text(
            section_value(sections, "What to build", "建设内容", "实现内容", "需求摘要"),
            labels["missing_summary"],
        ),
        scope=metadata_lines(sections, language),
        acceptance_criteria=section_text(
            section_value(sections, "Acceptance criteria", "验收标准"),
            labels["missing_acceptance"],
        ),
        dependencies=section_text(
            section_value(sections, "Blocked by", "依赖", "阻塞项"),
            labels["missing_dependencies"],
        ),
        implementation_notes=section_text(
            section_value(sections, "Notes", "备注", "实现备注"),
            labels["missing_notes"],
        ),
        local_issue_key=key,
    ).rstrip()
    return rendered + "\n"


def load_drafts(issue_dir: Path, language: str) -> list[IssueDraft]:
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
        title, title_source = resolve_title(path, text, sections)
        publish_status = parse_publish_status(sections)
        remote_number = None
        if publish_status.get("github number", "").isdigit():
            remote_number = int(publish_status["github number"])
        drafts.append(
            IssueDraft(
                path=path,
                key=path.name,
                title=title,
                title_source=title_source,
                body=render_issue_body(path.name, sections, language),
                blocked_by=parse_blockers(
                    section_value(sections, "Blocked by", "依赖", "阻塞项") or "",
                    known_keys,
                ),
                title_issues=validate_title(title, title_source, path),
                status=publish_status.get("status", "pending").lower() or "pending",
                remote_url=publish_status.get("github url") or None,
                remote_number=remote_number,
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


def topo_sort(drafts: list[IssueDraft]) -> list[IssueDraft]:
    by_key = {draft.key: draft for draft in drafts}
    temporary: set[str] = set()
    permanent: set[str] = set()
    ordered: list[IssueDraft] = []

    def visit(key: str, stack: list[str]) -> None:
        if key in permanent:
            return
        if key in temporary:
            cycle = " -> ".join([*stack, key])
            raise SystemExit(f"Cycle detected in Blocked by dependencies: {cycle}")
        temporary.add(key)
        for blocker in by_key[key].blocked_by:
            if blocker in by_key:
                visit(blocker, [*stack, key])
        temporary.remove(key)
        permanent.add(key)
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
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "team-ai-skills-publish-github-issues",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
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
        raise GitHubError(f"GitHub API {method} {url} failed: {exc.code} {body}") from exc
    except urllib.error.URLError as exc:
        raise GitHubError(f"GitHub API {method} {url} failed: {exc.reason}") from exc


def repo_api_base(github_url: str, repo: str) -> str:
    return f"{api_base(github_url)}/repos/{repo}"


def find_existing_issue(
    github_url: str,
    repo: str,
    token: str,
    draft: IssueDraft,
) -> dict[str, Any] | None:
    issues: list[dict[str, Any]] = []
    page = 1
    while True:
        query = urllib.parse.urlencode(
            {"state": "all", "per_page": "100", "page": str(page)}
        )
        url = f"{repo_api_base(github_url, repo)}/issues?{query}"
        batch = api_request("GET", url, token)
        issues.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    candidates = [
        issue
        for issue in issues
        if "pull_request" not in issue
        and f"Local-Issue-Key: {draft.key}" in (issue.get("body") or "")
    ]
    title_matches = [
        issue for issue in candidates if (issue.get("title") or "").strip() == draft.title
    ]
    if len(title_matches) == 1:
        return title_matches[0]
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        raise GitHubError(f"Multiple remote issues match Local-Issue-Key {draft.key}.")
    return None


def create_issue(
    github_url: str,
    repo: str,
    token: str,
    draft: IssueDraft,
    args: argparse.Namespace,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": draft.title,
        "body": draft.body,
    }
    if args.label:
        payload["labels"] = args.label
    if args.milestone is not None:
        payload["milestone"] = args.milestone
    if args.assignee:
        payload["assignees"] = args.assignee
    return api_request("POST", f"{repo_api_base(github_url, repo)}/issues", token, payload)


def write_status(draft: IssueDraft) -> None:
    text = draft.path.read_text(encoding="utf-8")
    body = [
        PUBLISH_SECTION,
        "",
        f"- Status: {draft.status}",
        f"- Updated At: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
    ]
    if draft.remote_number is not None:
        body.append(f"- GitHub Number: {draft.remote_number}")
    if draft.remote_url:
        body.append(f"- GitHub URL: {draft.remote_url}")
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
    args.language = language_from_config(args.language)
    issue_dir = issue_dir_from_args(args)
    repo = infer_repo(args)
    drafts = topo_sort(filter_drafts(load_drafts(issue_dir, args.language), args.issue))
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
            existing = find_existing_issue(args.github_url, repo, token, draft)
            if existing:
                draft.status = "skipped"
                draft.remote_number = existing.get("number")
                draft.remote_url = existing.get("html_url")
            else:
                created = create_issue(args.github_url, repo, token, draft, args)
                draft.status = "created"
                draft.remote_number = created.get("number")
                draft.remote_url = created.get("html_url")
            write_status(draft)
        except GitHubError as exc:
            draft.status = "failed"
            draft.error = str(exc)
            write_status(draft)

    counts: dict[str, int] = {}
    for draft in drafts:
        counts[draft.status] = counts.get(draft.status, 0) + 1

    return {
        "mode": "execute" if args.execute else "dry-run",
        "github_url": normalize_github_url(args.github_url),
        "language": args.language,
        "repo": repo,
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
                "remote_number": draft.remote_number,
                "remote_url": draft.remote_url,
                "error": draft.error,
            }
            for draft in drafts
        ],
    }


def print_text_summary(result: dict[str, Any]) -> None:
    print(f"Mode: {result['mode']}")
    print(f"GitHub: {result['github_url']}")
    print(f"Language: {result['language']}")
    print(f"Repo: {result['repo']}")
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

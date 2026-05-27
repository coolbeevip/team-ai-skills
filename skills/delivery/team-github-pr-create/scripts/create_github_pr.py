#!/usr/bin/env python3
"""Push an issue branch and create a linked GitHub Pull Request."""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Any


ISSUE_RE = re.compile(r"(?:^|[-_/])#?(\d+)(?:[-_/]|$)")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
BODY_TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "pr_body.md.tpl"


@dataclass
class ProjectRef:
    remote: str | None
    host: str
    path: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Push current branch and create a linked GitHub Pull Request."
    )
    parser.add_argument("--github-url", default="https://github.com")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--execute", action="store_true", help="Push and create PR.")
    parser.add_argument("--issue-number", help="GitHub issue number to link.")
    parser.add_argument("--source-branch", help="Source branch. Defaults to current branch.")
    parser.add_argument("--target-branch", help="Target branch. Defaults to remote default branch.")
    parser.add_argument("--source-remote", help="Remote to push source branch to.")
    parser.add_argument("--target-remote", help="Remote used as target project.")
    parser.add_argument("--source-repo", help="Source repository owner/repo.")
    parser.add_argument("--target-repo", help="Target repository owner/repo.")
    parser.add_argument("--title", help="Pull Request title.")
    parser.add_argument(
        "--issue-file",
        help="Local issue markdown file used to derive a meaningful PR title and body.",
    )
    parser.add_argument("--body-file", help="Read PR body from file.")
    parser.add_argument(
        "--language",
        help="Output language for rendered PR body. Defaults to team-spec/config.yml language, then en-US.",
    )
    parser.add_argument("--draft", action="store_true", help="Create a Draft PR.")
    parser.add_argument("--assignee", action="append", default=[], help="Assignee login.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
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
    except (OSError, subprocess.CalledProcessError) as exc:
        if check:
            detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
            raise SystemExit(f"git {' '.join(args)} failed: {detail}")
        return None
    return result.stdout.strip()


def current_branch() -> str:
    branch = run_git(["branch", "--show-current"])
    if not branch:
        raise SystemExit("Cannot determine current branch. Provide --source-branch.")
    return branch


def infer_issue_number(branch: str, explicit: str | None) -> str:
    if explicit:
        return explicit.lstrip("#")
    if branch.isdigit():
        return branch
    match = ISSUE_RE.search(branch)
    if match:
        return match.group(1)
    raise SystemExit("Cannot infer issue number from branch. Provide --issue-number.")


def remote_urls() -> dict[str, str]:
    output = run_git(["remote", "-v"], check=False)
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


def github_host(github_url: str) -> str:
    return urllib.parse.urlparse(github_url).hostname or "github.com"


def project_from_remote(remote: str, remotes: dict[str, str], host: str) -> ProjectRef | None:
    url = remotes.get(remote)
    parsed = remote_host_and_repo(url) if url else None
    if not parsed:
        return None
    remote_host, repo = parsed
    if remote_host != host:
        raise SystemExit(f"Remote {remote} host {remote_host} does not match GitHub host {host}.")
    return ProjectRef(remote=remote, host=remote_host, path=repo)


def branch_tracking_remote(branch: str) -> str | None:
    return run_git(["config", "--get", f"branch.{branch}.remote"], check=False)


def infer_target_repo(args: argparse.Namespace, branch: str) -> ProjectRef:
    host = github_host(args.github_url)
    if args.target_repo:
        return ProjectRef(remote=args.target_remote, host=host, path=args.target_repo)

    remotes = remote_urls()
    candidates: list[ProjectRef] = []

    if args.target_remote:
        target = project_from_remote(args.target_remote, remotes, host)
        if not target:
            raise SystemExit(f"Remote {args.target_remote} is not a valid GitHub remote.")
        return target

    upstream = project_from_remote("upstream", remotes, host)
    if upstream:
        return upstream

    tracked_remote = branch_tracking_remote(branch)
    if tracked_remote:
        tracked = project_from_remote(tracked_remote, remotes, host)
        if tracked:
            return tracked

    for remote in remotes:
        parsed = project_from_remote(remote, remotes, host)
        if parsed:
            candidates.append(parsed)

    unique = {candidate.path: candidate for candidate in candidates}
    if len(unique) == 1:
        return next(iter(unique.values()))

    detail = ", ".join(f"{item.remote}={item.path}" for item in candidates)
    raise SystemExit(
        "Cannot infer target repo. Provide --target-repo or --target-remote. "
        f"Candidates: {detail or 'none'}"
    )


def infer_source_repo(args: argparse.Namespace, branch: str, target: ProjectRef) -> ProjectRef:
    host = github_host(args.github_url)
    if args.source_repo:
        return ProjectRef(remote=args.source_remote, host=host, path=args.source_repo)

    remotes = remote_urls()

    for remote in [
        args.source_remote,
        branch_tracking_remote(branch),
        "origin",
    ]:
        if remote:
            source = project_from_remote(remote, remotes, host)
            if source:
                return source

    candidates = [
        parsed
        for remote in remotes
        for parsed in [project_from_remote(remote, remotes, host)]
        if parsed
    ]
    unique = {candidate.path: candidate for candidate in candidates}
    if len(unique) == 1:
        return next(iter(unique.values()))
    return target


def default_target_branch(target: ProjectRef) -> str:
    if target.remote:
        ref = run_git(["symbolic-ref", f"refs/remotes/{target.remote}/HEAD"], check=False)
        if ref:
            prefix = f"refs/remotes/{target.remote}/"
            if ref.startswith(prefix):
                return ref.removeprefix(prefix)
    return "main"


def target_branch_source(target: ProjectRef, explicit: str | None) -> str:
    if explicit:
        return "explicit"
    if target.remote:
        ref = run_git(["symbolic-ref", f"refs/remotes/{target.remote}/HEAD"], check=False)
        if ref:
            return f"inferred from {target.remote}/HEAD"
    return "fallback main"


def branch_summary(branch: str, issue_number: str) -> str:
    cleaned = branch
    cleaned = re.sub(rf"(^|[-_/])#?{re.escape(issue_number)}([-_/]|$)", " ", cleaned)
    cleaned = re.sub(r"[-_]+", " ", cleaned).strip()
    return cleaned[:80] if cleaned else "implementation"


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


def split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        section_title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[section_title] = text[start:end].strip()
    return sections


def issue_title_from_file(path: Path) -> tuple[str, str] | None:
    text = path.read_text(encoding="utf-8")
    first_heading = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if first_heading:
        return first_heading.group(1).strip(), str(path)
    sections = split_sections(text)
    if "Title" in sections and sections["Title"].strip():
        return sections["Title"].splitlines()[0].strip(), str(path)
    return None


def infer_issue_file(issue_number: str, explicit: str | None) -> Path | None:
    if explicit:
        path = Path(explicit)
        if not path.exists():
            raise SystemExit(f"Issue file does not exist: {path}")
        if path.is_dir():
            raise SystemExit(f"Issue file is a directory: {path}")
        return path

    active_root = Path("team-spec/active")
    legacy_issues_root = active_root / "issues"
    if not active_root.exists():
        return None
    candidates = []
    candidates.extend(active_root.glob(f"*/issues/{issue_number}-*.md"))
    if legacy_issues_root.exists():
        candidates.extend(legacy_issues_root.glob(f"*/{issue_number}-*.md"))
    candidates = sorted(set(candidates))
    candidates = [
        path
        for path in candidates
        if not path.name.endswith((".implementation.md", ".verification.md"))
    ]
    if len(candidates) == 1:
        return candidates[0]
    return None


def infer_issue_title(issue_number: str, explicit_file: str | None) -> tuple[str, str] | None:
    path = infer_issue_file(issue_number, explicit_file)
    if not path:
        return None
    resolved = issue_title_from_file(path)
    if not resolved:
        if explicit_file:
            raise SystemExit(
                f"Cannot derive title from {path}. Add a '# Title' heading or '## Title' section."
            )
        return None
    return resolved


def resolve_issue_file_and_title(
    issue_number: str,
    explicit_file: str | None,
) -> tuple[Path | None, tuple[str, str] | None]:
    issue_file = infer_issue_file(issue_number, explicit_file)
    if not issue_file:
        return None, None
    issue_title = issue_title_from_file(issue_file)
    if not issue_title and explicit_file:
        raise SystemExit(
            f"Cannot derive title from {issue_file}. Add a '# Title' heading or '## Title' section."
        )
    return issue_file, issue_title


def normalize_title_text(title: str) -> str:
    return re.sub(r"\s+", " ", title).strip()


def build_title(
    args: argparse.Namespace,
    issue_number: str,
    branch: str,
    issue_title: str | None,
) -> tuple[str, str]:
    if args.title:
        title = normalize_title_text(args.title)
        title_source = "explicit"
    elif issue_title:
        title = normalize_title_text(issue_title)
        title_source = "issue_file"
    else:
        summary = branch_summary(branch, issue_number)
        if summary == "implementation":
            raise SystemExit(
                "Cannot build a meaningful PR title from the branch name. "
                "Provide --title or --issue-file."
            )
        title = summary
        title_source = "branch"
    if args.draft and not title.lower().startswith(("draft:", "wip:")):
        title = "Draft: " + title
    return title, title_source


def body_section(sections: dict[str, str], fallback: str, *titles: str) -> str:
    value = (section_value(sections, *titles) or "").strip()
    return value if value else fallback


def section_value(sections: dict[str, str], *names: str) -> str | None:
    normalized = {key.lower(): value for key, value in sections.items()}
    for name in names:
        value = normalized.get(name.lower())
        if value:
            return value
    return None


def load_issue_sections(issue_file: Path | None) -> dict[str, str]:
    if not issue_file:
        return {}
    return split_sections(issue_file.read_text(encoding="utf-8"))


def pr_body_labels(language: str) -> dict[str, str]:
    if is_chinese_language(language):
        return {
            "summary_heading": "摘要",
            "changes_heading": "变更",
            "acceptance_criteria_heading": "验收标准",
            "verification_heading": "验证",
            "risks_heading": "风险",
            "reviewer_notes_heading": "审阅备注",
            "checklist_heading": "检查清单",
            "missing_summary": "从分支 `${branch}` 实现 issue #${issue_number}。",
            "missing_changes": "- 见本 PR 的提交记录。",
            "missing_verification": "- [ ] 请在发起审阅前补充验证命令和结果。",
            "missing_acceptance": "- [ ] 本地 issue 文件未记录验收标准覆盖情况。",
            "missing_risks": "- 未记录明确的回归风险。",
            "missing_reviewer_notes": "- 未记录需要审阅者特别关注的事项。",
            "checklist": "\n".join(
                [
                    "- [ ] PR 标题清楚描述变更本身，且不嵌入 issue 编号。",
                    "- [ ] 实现范围与关联 issue 一致。",
                    "- [ ] 已在上方列出相关测试或检查结果。",
                ]
            ),
        }
    return {
        "summary_heading": "Summary",
        "changes_heading": "Changes",
        "acceptance_criteria_heading": "Acceptance criteria",
        "verification_heading": "Verification",
        "risks_heading": "Risks",
        "reviewer_notes_heading": "Reviewer notes",
        "checklist_heading": "Checklist",
        "missing_summary": "Implements issue #${issue_number} from branch `${branch}`.",
        "missing_changes": "- See the commits in this pull request.",
        "missing_verification": "- [ ] Add the verification commands and results before review.",
        "missing_acceptance": "- [ ] Acceptance criteria coverage was not found in the local issue file.",
        "missing_risks": "- No specific regression risks recorded.",
        "missing_reviewer_notes": "- No reviewer notes recorded.",
        "checklist": "\n".join(
            [
                "- [ ] The PR title clearly describes the change without embedding the issue number.",
                "- [ ] The implementation scope matches the linked issue.",
                "- [ ] Relevant tests or checks are listed above.",
            ]
        ),
    }


def render_default_body(
    issue_number: str,
    branch: str,
    issue_file: Path | None,
    language: str,
) -> str:
    sections = load_issue_sections(issue_file)
    template = Template(BODY_TEMPLATE_PATH.read_text(encoding="utf-8"))
    labels = pr_body_labels(language)
    fallback_template_values = {"issue_number": issue_number, "branch": branch}
    return template.safe_substitute(
        **labels,
        issue_number=issue_number,
        branch=branch,
        summary=body_section(
            sections,
            Template(labels["missing_summary"]).safe_substitute(fallback_template_values),
            "What to build",
            "建设内容",
            "实现内容",
            "需求摘要",
        ),
        changes=body_section(
            sections,
            labels["missing_changes"],
            "Implementation Notes",
            "实现说明",
            "实现备注",
        ),
        verification=body_section(
            sections,
            labels["missing_verification"],
            "Commands Run",
            "验证命令",
            "已运行命令",
        ),
        acceptance_coverage=body_section(
            sections,
            labels["missing_acceptance"],
            "Acceptance Criteria Coverage",
            "验收标准覆盖",
            "验收覆盖",
        ),
        risks=body_section(
            sections,
            labels["missing_risks"],
            "Regression Risks",
            "回归风险",
            "风险",
        ),
        reviewer_notes=body_section(
            sections,
            labels["missing_reviewer_notes"],
            "Findings",
            "发现",
            "审阅备注",
        ),
    ).strip()


def build_body(
    args: argparse.Namespace,
    issue_number: str,
    branch: str,
    issue_file: Path | None,
    language: str,
) -> str:
    if args.body_file:
        with open(args.body_file, encoding="utf-8") as fh:
            body = fh.read().strip()
    else:
        body = render_default_body(issue_number, branch, issue_file, language)
    if f"#{issue_number}" not in body:
        body = f"Closes #{issue_number}\n\n" + body
    if not re.search(rf"\b(close[sd]?|fix(e[sd])?|resolve[sd]?)\s+#{re.escape(issue_number)}\b", body, re.I):
        body = f"Closes #{issue_number}\n\n" + body
    return body


def tracked_ignored_files() -> list[str]:
    output = run_git(["ls-files", "-ci", "--exclude-standard"], check=False)
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def normalize_github_url(url: str) -> str:
    return url.rstrip("/")


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


def api_request(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> Any:
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "team-ai-skills-create-github-pr",
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
        raise RuntimeError(f"GitHub API {method} {url} failed: {exc.code} {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API {method} {url} failed: {exc.reason}") from exc


def repo_api_base(github_url: str, repo: str) -> str:
    return f"{normalize_github_url(github_url)}/api/v3/repos/{repo}"


def get_repo_id(github_url: str, repo: str, token: str) -> int:
    data = api_request("GET", repo_api_base(github_url, repo), token)
    return int(data["id"])


def existing_pr(
    github_url: str,
    target_repo: str,
    token: str,
    source_repo: str,
    source_branch: str,
) -> dict[str, Any] | None:
    head = source_repo.split("/", 1)[0] + ":" + source_branch
    query = urllib.parse.urlencode({"state": "open", "head": head, "per_page": "20"})
    url = f"{repo_api_base(github_url, target_repo)}/pulls?{query}"
    items = api_request("GET", url, token)
    return items[0] if items else None


def create_pr(
    args: argparse.Namespace,
    token: str,
    source: ProjectRef,
    target: ProjectRef,
    source_branch: str,
    target_branch: str,
    title: str,
    body: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "head": source_branch if source.path == target.path else f"{source.path.split('/', 1)[0]}:{source_branch}",
        "base": target_branch,
        "title": title,
        "body": body,
        "draft": args.draft,
    }
    payload["maintainer_can_modify"] = True

    return api_request(
        "POST",
        f"{repo_api_base(args.github_url, target.path)}/pulls",
        token,
        payload,
    )


def dirty_worktree() -> bool:
    return bool(run_git(["status", "--porcelain"], check=False))


def push_branch(remote: str, branch: str) -> None:
    run_git(["push", "-u", remote, f"{branch}:{branch}"])


def upsert_issue_tracking_line(lines: list[str], key: str, value: str) -> list[str]:
    pattern = re.compile(rf"^(\s*(?:-\s*)?{re.escape(key)}\s*:\s*).*$", re.IGNORECASE)
    replacement = f"{key}: {value}"
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            lines[index] = f"{match.group(1)}{value}"
            return lines

    status_index = next(
        (
            index
            for index, line in enumerate(lines)
            if re.match(r"^\s*(?:-\s*)?Status\s*:", line, re.IGNORECASE)
        ),
        None,
    )
    insert_at = status_index + 1 if status_index is not None else len(lines)
    lines.insert(insert_at, replacement)
    return lines


def write_issue_pr_tracking(
    issue_file: Path | None,
    pr_url: str | None,
    source_branch: str,
) -> str | None:
    if not issue_file or not pr_url:
        return None

    text = issue_file.read_text(encoding="utf-8")
    ends_with_newline = text.endswith("\n")
    lines = text.splitlines()
    lines = upsert_issue_tracking_line(lines, "Status", "PR created")
    lines = upsert_issue_tracking_line(lines, "Pushed Branch", source_branch)
    lines = upsert_issue_tracking_line(lines, "PR", pr_url)
    updated = "\n".join(lines)
    if ends_with_newline:
        updated += "\n"
    issue_file.write_text(updated, encoding="utf-8")
    return str(issue_file)


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    args.language = language_from_config(args.language)
    source_branch = args.source_branch or current_branch()
    issue_number = infer_issue_number(source_branch, args.issue_number)
    target = infer_target_repo(args, source_branch)
    source = infer_source_repo(args, source_branch, target)
    target_branch = args.target_branch or default_target_branch(target)
    issue_file, issue_title = resolve_issue_file_and_title(issue_number, args.issue_file)
    title, title_source = build_title(
        args,
        issue_number,
        source_branch,
        issue_title[0] if issue_title else None,
    )
    body = build_body(args, issue_number, source_branch, issue_file, args.language)
    ignored_files = tracked_ignored_files()

    if not source.remote and not args.source_repo:
        raise SystemExit("Cannot infer source remote. Provide --source-remote or --source-repo.")

    return {
        "mode": "execute" if args.execute else "dry-run",
        "github_url": normalize_github_url(args.github_url),
        "language": args.language,
        "issue_number": issue_number,
        "source_branch": source_branch,
        "target_branch": target_branch,
        "source_remote": source.remote,
        "source_repo": source.path,
        "target_repo": target.path,
        "title": title,
        "title_source": title_source,
        "issue_title_source": issue_title[1] if issue_title else None,
        "issue_file": str(issue_file) if issue_file else None,
        "body": body,
        "target_branch_source": target_branch_source(target, args.target_branch),
        "tracked_ignored_files": ignored_files,
        "dirty_worktree": dirty_worktree(),
    }


def confirm_execution(plan: dict[str, Any]) -> None:
    needs_confirmation = plan["target_branch_source"] != "explicit"
    ignored_files = plan.get("tracked_ignored_files") or []

    if not needs_confirmation and not ignored_files:
        return

    print("Execution confirmation required.")
    if needs_confirmation:
        print(f"- Target branch was {plan['target_branch_source']}: {plan['target_branch']}")
    if ignored_files:
        print("- Tracked files matching ignore rules were found:")
        for path in ignored_files:
            print(f"  - {path}")
    if not sys.stdin.isatty():
        raise SystemExit(
            "Interactive confirmation required. Rerun in a TTY or pass an explicit --target-branch after reviewing ignored tracked files."
        )
    answer = input("Continue with push and creation? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        raise SystemExit("Aborted by user.")


def execute(args: argparse.Namespace, plan: dict[str, Any]) -> dict[str, Any]:
    token = os.environ.get(args.token_env)
    if not token:
        raise SystemExit(f"Missing token env var: {args.token_env}")
    if plan["dirty_worktree"]:
        raise SystemExit("Working tree has uncommitted changes. Commit or stash before creating PR.")
    if not plan["source_remote"]:
        raise SystemExit("Cannot push without a source remote.")

    confirm_execution(plan)
    push_branch(plan["source_remote"], plan["source_branch"])
    existing = existing_pr(
        args.github_url,
        plan["target_repo"],
        token,
        plan["source_repo"],
        plan["source_branch"],
    )
    if existing:
        plan["status"] = "skipped"
        plan["pr_url"] = existing.get("html_url")
        plan["pr_number"] = existing.get("number")
        plan["issue_file_updated"] = write_issue_pr_tracking(
            Path(plan["issue_file"]) if plan.get("issue_file") else None,
            plan.get("pr_url"),
            plan["source_branch"],
        )
        return plan

    source = ProjectRef(plan["source_remote"], github_host(args.github_url), plan["source_repo"])
    target = ProjectRef(args.target_remote, github_host(args.github_url), plan["target_repo"])
    created = create_pr(
        args,
        token,
        source,
        target,
        plan["source_branch"],
        plan["target_branch"],
        plan["title"],
        plan["body"],
    )
    plan["status"] = "created"
    plan["pr_url"] = created.get("html_url")
    plan["pr_number"] = created.get("number")
    plan["issue_file_updated"] = write_issue_pr_tracking(
        Path(plan["issue_file"]) if plan.get("issue_file") else None,
        plan.get("pr_url"),
        plan["source_branch"],
    )
    return plan


def print_text(plan: dict[str, Any]) -> None:
    print(f"Mode: {plan['mode']}")
    print(f"Language: {plan['language']}")
    print(f"Issue: #{plan['issue_number']}")
    print(f"Source: {plan['source_repo']}:{plan['source_branch']}")
    print(f"Target: {plan['target_repo']}:{plan['target_branch']}")
    print(f"Target branch source: {plan['target_branch_source']}")
    print(f"Source remote: {plan['source_remote']}")
    print(f"Dirty worktree: {plan['dirty_worktree']}")
    if plan.get("tracked_ignored_files"):
        print("Tracked files matching ignore rules:")
        for path in plan["tracked_ignored_files"]:
            print(f"- {path}")
    print(f"Title: {plan['title']}")
    print(f"Title source: {plan['title_source']}")
    if plan.get("issue_title_source"):
        print(f"Issue title source: {plan['issue_title_source']}")
    if plan.get("issue_file_updated"):
        print(f"Issue file updated: {plan['issue_file_updated']}")
    if plan.get("pr_url"):
        print(f"PR: {plan['pr_url']}")
    if plan.get("status"):
        print(f"Status: {plan['status']}")
    print("")
    print("Body preview:")
    print(plan["body"])


def main() -> int:
    args = parse_args()
    try:
        plan = build_plan(args)
        if args.execute:
            plan = execute(args, plan)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print_text(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

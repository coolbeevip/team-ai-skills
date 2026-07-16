#!/usr/bin/env python3
"""Push an issue branch and create a linked GitLab Merge Request."""

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
TEAM_SPEC_PREFIX = "team-spec/"
BODY_TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "mr_body.md.tpl"
TITLE_TAG_RE = re.compile(r"^(?:\[[^\]\n]+\])+\s+\S")
PAST_TENSE_TITLE_RE = re.compile(
    r"^(?:\[[^\]\n]+\]\s*)*(Added|Changed|Created|Fixed|Implemented|Removed|Updated)\b"
)


@dataclass
class ProjectRef:
    remote: str | None
    host: str
    path: str


class GitLabError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Push current branch and create a linked GitLab Merge Request."
    )
    parser.add_argument("--token-env", default="GITLAB_TOKEN")
    parser.add_argument("--execute", action="store_true", help="Push and create MR.")
    parser.add_argument("--issue-iid", help="GitLab issue IID to link.")
    parser.add_argument("--source-branch", help="Source branch. Defaults to current branch.")
    parser.add_argument(
        "--target-branch",
        help="Target branch. Defaults to team-spec/config.yml version_control.trunk_branch, then remote default branch.",
    )
    parser.add_argument("--source-remote", help="Remote to push source branch to.")
    parser.add_argument("--target-remote", help="Remote used as target project.")
    parser.add_argument("--source-project", help="Source project namespace/project.")
    parser.add_argument("--target-project", help="Target project namespace/project.")
    parser.add_argument("--title", help="Merge Request title.")
    parser.add_argument(
        "--issue-file",
        help="Local issue markdown file used to derive a meaningful MR title.",
    )
    parser.add_argument("--body-file", help="Read MR body from file.")
    parser.add_argument(
        "--language",
        help="Output language for rendered MR body. Defaults to team-spec/config.yml language, then en-US.",
    )
    parser.add_argument("--draft", action="store_true", help="Create a Draft MR.")
    parser.add_argument("--label", action="append", default=[], help="Label to add.")
    parser.add_argument("--assignee-id", action="append", type=int, default=[])
    parser.add_argument("--reviewer-id", action="append", type=int, default=[])
    parser.add_argument("--remove-source-branch", action="store_true")
    parser.add_argument(
        "--commit-message",
        help="Commit local changes before pushing. Requires --commit-all, --commit-path, or --commit-staged.",
    )
    parser.add_argument(
        "--commit-all",
        action="store_true",
        help="Stage all non-team-spec worktree changes before committing.",
    )
    parser.add_argument(
        "--commit-path",
        action="append",
        default=[],
        help="Stage a specific non-team-spec path before committing. Repeat for multiple paths.",
    )
    parser.add_argument(
        "--commit-staged",
        action="store_true",
        help="Commit already staged changes without staging additional paths.",
    )
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


def git_succeeds(args: list[str]) -> bool:
    result = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.returncode == 0


def current_branch() -> str:
    branch = run_git(["branch", "--show-current"])
    if not branch:
        raise SystemExit("Cannot determine current branch. Provide --source-branch.")
    return branch


def infer_issue_iid(branch: str, explicit: str | None) -> str:
    if explicit:
        return explicit.lstrip("#")
    if branch.isdigit():
        return branch
    match = ISSUE_RE.search(branch)
    if match:
        return match.group(1)
    raise SystemExit("Cannot infer issue IID from branch. Provide --issue-iid.")


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


def gitlab_host(gitlab_url: str) -> str:
    return urllib.parse.urlparse(gitlab_url).hostname or "gitlab.com"


def gitlab_url_from_env() -> str:
    url = os.environ.get("GITLAB_URL", "").strip()
    if not url:
        raise SystemExit("Missing GitLab base URL env var: GITLAB_URL")
    return normalize_gitlab_url(url)


def project_from_remote(remote: str, remotes: dict[str, str], host: str) -> ProjectRef | None:
    url = remotes.get(remote)
    parsed = remote_host_and_project(url) if url else None
    if not parsed:
        return None
    remote_host, project = parsed
    if remote_host != host:
        raise SystemExit(f"Remote {remote} host {remote_host} does not match GitLab host {host}.")
    return ProjectRef(remote=remote, host=remote_host, path=project)


def branch_tracking_remote(branch: str) -> str | None:
    return run_git(["config", "--get", f"branch.{branch}.remote"], check=False)


def infer_target_project(args: argparse.Namespace, branch: str) -> ProjectRef:
    host = gitlab_host(args.gitlab_url)
    if args.target_project:
        return ProjectRef(remote=args.target_remote, host=host, path=args.target_project)

    remotes = remote_urls()
    candidates: list[ProjectRef] = []

    if args.target_remote:
        target = project_from_remote(args.target_remote, remotes, host)
        if not target:
            raise SystemExit(f"Remote {args.target_remote} is not a valid GitLab remote.")
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
        "Cannot infer target project. Provide --target-project or --target-remote. "
        f"Candidates: {detail or 'none'}"
    )


def infer_source_project(args: argparse.Namespace, branch: str, target: ProjectRef) -> ProjectRef:
    host = gitlab_host(args.gitlab_url)
    if args.source_project:
        return ProjectRef(remote=args.source_remote, host=host, path=args.source_project)

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


def target_branch_source(target: ProjectRef, explicit: str | None, configured: str | None) -> str:
    if explicit:
        return "explicit"
    if configured:
        return "team-spec/config.yml version_control.trunk_branch"
    if target.remote:
        ref = run_git(["symbolic-ref", f"refs/remotes/{target.remote}/HEAD"], check=False)
        if ref:
            return f"inferred from {target.remote}/HEAD"
    return "fallback main"


def branch_summary(branch: str, issue_iid: str) -> str:
    cleaned = branch
    cleaned = re.sub(rf"(^|[-_/])#?{re.escape(issue_iid)}([-_/]|$)", " ", cleaned)
    cleaned = re.sub(r"[-_]+", " ", cleaned).strip()
    return cleaned[:80] if cleaned else "implementation"


def strip_yaml_scalar(value: str) -> str:
    value = value.split("#", 1)[0].strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1].strip()
    return value


def team_config_values() -> dict[str, str]:
    config = Path("team-spec") / "config.yml"
    if not config.exists():
        return {}
    values: dict[str, str] = {}
    section: str | None = None
    for line in config.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^(\s*)([A-Za-z0-9_-]+)\s*:\s*(.*?)\s*$", line)
        if not match:
            continue
        indent = len(match.group(1).replace("\t", "  "))
        key = match.group(2)
        value = strip_yaml_scalar(match.group(3))
        if indent == 0:
            if value:
                values[key] = value
                section = None
            else:
                section = key
            continue
        if section and value:
            values[f"{section}.{key}"] = value
    return values


def team_config_value(key: str) -> str | None:
    value = team_config_values().get(key)
    return value.strip() if value and value.strip() else None


def language_from_config(explicit: str | None) -> str:
    if explicit:
        return explicit.strip()
    return team_config_value("language") or "en-US"


def version_control_value(key: str) -> str | None:
    return team_config_value(f"version_control.{key}")


def ensure_supported_version_control() -> None:
    system = version_control_value("system")
    if system and system.lower() != "git":
        raise SystemExit(
            "team-spec/config.yml version_control.system is "
            f"{system!r}; create_gitlab_mr.py only supports git."
        )


def apply_version_control_defaults(args: argparse.Namespace) -> None:
    if not args.target_remote:
        args.target_remote = version_control_value("target_remote")
    if not args.source_remote:
        args.source_remote = version_control_value("source_remote")


def configured_trunk_branch() -> str | None:
    return version_control_value("trunk_branch")


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


def infer_issue_file(issue_iid: str, explicit: str | None) -> Path | None:
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
    candidates.extend(active_root.glob(f"*/issues/{issue_iid}-*.md"))
    if legacy_issues_root.exists():
        candidates.extend(legacy_issues_root.glob(f"*/{issue_iid}-*.md"))
    candidates = sorted(set(candidates))
    candidates = [
        path
        for path in candidates
        if not path.name.endswith((".implementation.md", ".verification.md"))
    ]
    if len(candidates) == 1:
        return candidates[0]
    return None


def infer_issue_title(issue_iid: str, explicit_file: str | None) -> tuple[str, str] | None:
    path = infer_issue_file(issue_iid, explicit_file)
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
    issue_iid: str,
    explicit_file: str | None,
) -> tuple[Path | None, tuple[str, str] | None]:
    issue_file = infer_issue_file(issue_iid, explicit_file)
    if not issue_file:
        return None, None
    issue_title = issue_title_from_file(issue_file)
    if not issue_title and explicit_file:
        raise SystemExit(
            f"Cannot derive title from {issue_file}. Add a '# Title' heading or '## Title' section."
        )
    return issue_file, issue_title


def normalize_title_text(title: str) -> str:
    normalized = re.sub(r"\s+", " ", title).strip()
    return re.sub(r"[.。]+\s*$", "", normalized)


def title_style_notes(title: str) -> list[str]:
    notes: list[str] = []
    if not TITLE_TAG_RE.match(title):
        notes.append(
            "Recommended title starts with one or more component tags, e.g. [BugFix] Fix export filter."
        )
    if PAST_TENSE_TITLE_RE.match(title):
        notes.append("Recommended title uses imperative mood, e.g. Fix ..., not Fixed ...")
    return notes


def build_title(
    args: argparse.Namespace,
    issue_iid: str,
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
        summary = branch_summary(branch, issue_iid)
        if summary == "implementation":
            raise SystemExit(
                "Cannot build a meaningful MR title from the branch name. "
                "Provide --title or --issue-file."
            )
        title = summary
        title_source = "branch"
    if args.draft and not title.lower().startswith(("draft:", "wip:")):
        title = "Draft: " + title
    return title, title_source


def section_value(sections: dict[str, str], *names: str) -> str | None:
    normalized = {key.lower(): value for key, value in sections.items()}
    for name in names:
        value = normalized.get(name.lower())
        if value:
            return value
    return None


def body_section(sections: dict[str, str], fallback: str, *titles: str) -> str:
    value = (section_value(sections, *titles) or "").strip()
    return value if value else fallback


def load_issue_sections(issue_file: Path | None) -> dict[str, str]:
    if not issue_file:
        return {}
    return split_sections(issue_file.read_text(encoding="utf-8"))


def mr_body_labels(language: str) -> dict[str, str]:
    if is_chinese_language(language):
        return {
            "missing_purpose": "从分支 `${branch}` 实现 issue #${issue_iid}。",
            "missing_change_log": "- 见本 MR 的提交记录。",
            "missing_testing": "- [ ] 请在发起审阅前补充验证命令、测试结果和 CI 覆盖情况。",
            "missing_compatibility": "- 未记录 public API、配置项、数据格式、依赖、兼容性、性能、部署、运维或安全影响。",
            "missing_reviewer_notes": "- 未记录需要 reviewer 特别关注的事项。",
            "documentation_checklist": "\n".join(
                [
                    "- [ ] 不需要文档更新",
                    "- [ ] 已更新文档 / JavaDocs / API docs / release notes",
                    "- [ ] 后续 PR 更新文档，并说明原因",
                ]
            ),
        }
    return {
        "missing_purpose": "Implements issue #${issue_iid} from branch `${branch}`.",
        "missing_change_log": "- See the commits in this merge request.",
        "missing_testing": "- [ ] Add verification commands, test results, and CI coverage before review.",
        "missing_compatibility": "- No public API, configuration, data format, dependency, compatibility, performance, deployment, operations, or security impact recorded.",
        "missing_reviewer_notes": "- No reviewer notes recorded.",
        "documentation_checklist": "\n".join(
            [
                "- [ ] No documentation update needed",
                "- [ ] Updated docs / JavaDocs / API docs / release notes",
                "- [ ] Documentation will be updated in a follow-up PR, with rationale",
            ]
        ),
    }


def render_default_body(
    issue_iid: str,
    branch: str,
    issue_file: Path | None,
    language: str,
) -> str:
    sections = load_issue_sections(issue_file)
    template = Template(BODY_TEMPLATE_PATH.read_text(encoding="utf-8"))
    labels = mr_body_labels(language)
    fallback_template_values = {"issue_iid": issue_iid, "branch": branch}
    return template.safe_substitute(
        **labels,
        issue_iid=issue_iid,
        branch=branch,
        purpose=body_section(
            sections,
            Template(labels["missing_purpose"]).safe_substitute(fallback_template_values),
            "What to build",
            "建设内容",
            "实现内容",
            "需求摘要",
        ),
        change_log=body_section(
            sections,
            labels["missing_change_log"],
            "Implementation Notes",
            "实现说明",
            "实现备注",
        ),
        testing=body_section(
            sections,
            labels["missing_testing"],
            "Commands Run",
            "验证命令",
            "已运行命令",
            "Acceptance Criteria Coverage",
            "验收标准覆盖",
            "验收覆盖",
        ),
        documentation=labels["documentation_checklist"],
        compatibility=body_section(
            sections,
            labels["missing_compatibility"],
            "Compatibility / impact",
            "Compatibility",
            "Impact",
            "Regression Risks",
            "兼容性影响",
            "影响",
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
    issue_iid: str,
    branch: str,
    issue_file: Path | None,
    language: str,
) -> str:
    if args.body_file:
        body = open(args.body_file, encoding="utf-8").read().strip()
    else:
        body = render_default_body(issue_iid, branch, issue_file, language)
    if f"#{issue_iid}" not in body:
        body = f"Fixes #{issue_iid}\n\n" + body
    if not re.search(rf"\b(close[sd]?|fix(e[sd])?|resolve[sd]?)\s+#{re.escape(issue_iid)}\b", body, re.I):
        body = f"Fixes #{issue_iid}\n\n" + body
    return body


def tracked_ignored_files() -> list[str]:
    output = run_git(["ls-files", "-ci", "--exclude-standard"], check=False)
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def normalize_gitlab_url(url: str) -> str:
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


def get_project_id(gitlab_url: str, project: str, token: str) -> int:
    data = api_request("GET", project_api_base(gitlab_url, project), token)
    return int(data["id"])


def existing_mr(
    gitlab_url: str,
    target_project: str,
    token: str,
    source_branch: str,
    source_project_id: int | None = None,
) -> dict[str, Any] | None:
    query = urllib.parse.urlencode(
        {"state": "opened", "source_branch": source_branch, "per_page": "20"}
    )
    url = f"{project_api_base(gitlab_url, target_project)}/merge_requests?{query}"
    items = api_request("GET", url, token)
    if source_project_id is None:
        return items[0] if items else None
    for item in items:
        if item.get("source_project_id") == source_project_id:
            return item
    return None


def create_mr(
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
        "source_branch": source_branch,
        "target_branch": target_branch,
        "title": title,
        "description": body,
        "remove_source_branch": args.remove_source_branch,
    }
    if args.label:
        payload["labels"] = ",".join(args.label)
    if args.assignee_id:
        payload["assignee_ids"] = args.assignee_id
    if args.reviewer_id:
        payload["reviewer_ids"] = args.reviewer_id
    if source.path != target.path:
        payload["target_project_id"] = get_project_id(args.gitlab_url, target.path, token)

    return api_request(
        "POST",
        f"{project_api_base(args.gitlab_url, source.path)}/merge_requests",
        token,
        payload,
    )


def dirty_worktree() -> bool:
    return bool(run_git(["status", "--porcelain"], check=False))


def worktree_status() -> list[str]:
    output = run_git(["status", "--porcelain"], check=False)
    if not output:
        return []
    return [line for line in output.splitlines() if line]


def status_path(line: str) -> str:
    path = line[3:]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path


def is_team_spec_path(path: str) -> bool:
    normalized = path.strip().lstrip("./")
    return normalized == "team-spec" or normalized.startswith(TEAM_SPEC_PREFIX)


def non_team_spec_status(status: list[str]) -> list[str]:
    return [line for line in status if not is_team_spec_path(status_path(line))]


def staged_paths() -> list[str]:
    output = run_git(["diff", "--cached", "--name-only"], check=False)
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def has_staged_changes() -> bool:
    return not git_succeeds(["diff", "--cached", "--quiet"])


def validate_commit_options(args: argparse.Namespace) -> None:
    staging_modes = sum(
        [
            bool(args.commit_all),
            bool(args.commit_path),
            bool(args.commit_staged),
        ]
    )
    if staging_modes > 1:
        raise SystemExit("Use only one of --commit-all, --commit-path, or --commit-staged.")
    if args.commit_message and staging_modes == 0:
        raise SystemExit("--commit-message requires --commit-all, --commit-path, or --commit-staged.")
    if staging_modes and not args.commit_message:
        raise SystemExit("--commit-all, --commit-path, and --commit-staged require --commit-message.")
    blocked_paths = [path for path in args.commit_path if is_team_spec_path(path)]
    if blocked_paths:
        raise SystemExit(
            "Refusing to git add paths under team-spec/: " + ", ".join(blocked_paths)
        )


def commit_requested(args: argparse.Namespace) -> bool:
    return bool(args.commit_message)


def commit_changes(args: argparse.Namespace) -> str:
    if args.commit_all:
        run_git(["add", "-A", "--", ".", ":(exclude)team-spec", ":(exclude)team-spec/**"])
    elif args.commit_path:
        run_git(["add", "--", *args.commit_path])

    blocked_staged = [path for path in staged_paths() if is_team_spec_path(path)]
    if blocked_staged:
        raise SystemExit(
            "Refusing to commit staged paths under team-spec/. Unstage them first: "
            + ", ".join(blocked_staged)
        )
    if not has_staged_changes():
        raise SystemExit("No staged non-team-spec changes to commit.")

    run_git(["commit", "-m", args.commit_message])
    commit_sha = run_git(["rev-parse", "--short", "HEAD"])
    if not commit_sha:
        raise SystemExit("Cannot determine created commit SHA.")
    return commit_sha


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


def write_issue_mr_tracking(
    issue_file: Path | None,
    mr_url: str | None,
    source_branch: str,
) -> str | None:
    if not issue_file or not mr_url:
        return None

    text = issue_file.read_text(encoding="utf-8")
    ends_with_newline = text.endswith("\n")
    lines = text.splitlines()
    lines = upsert_issue_tracking_line(lines, "Status", "mr-created")
    lines = upsert_issue_tracking_line(lines, "Pushed Branch", source_branch)
    lines = upsert_issue_tracking_line(lines, "MR", mr_url)
    updated = "\n".join(lines)
    if ends_with_newline:
        updated += "\n"
    issue_file.write_text(updated, encoding="utf-8")
    return str(issue_file)


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    validate_commit_options(args)
    args.language = language_from_config(args.language)
    ensure_supported_version_control()
    apply_version_control_defaults(args)
    args.gitlab_url = gitlab_url_from_env()
    source_branch = args.source_branch or current_branch()
    issue_iid = infer_issue_iid(source_branch, args.issue_iid)
    target = infer_target_project(args, source_branch)
    source = infer_source_project(args, source_branch, target)
    configured_branch = configured_trunk_branch()
    target_branch = args.target_branch or configured_branch or default_target_branch(target)
    issue_file, issue_title = resolve_issue_file_and_title(issue_iid, args.issue_file)
    title, title_source = build_title(
        args,
        issue_iid,
        source_branch,
        issue_title[0] if issue_title else None,
    )
    body = build_body(args, issue_iid, source_branch, issue_file, args.language)
    ignored_files = tracked_ignored_files()
    status = worktree_status()

    if not source.remote and not args.source_project:
        raise SystemExit("Cannot infer source remote. Provide --source-remote or --source-project.")

    return {
        "mode": "execute" if args.execute else "dry-run",
        "gitlab_url": normalize_gitlab_url(args.gitlab_url),
        "language": args.language,
        "issue_iid": issue_iid,
        "source_branch": source_branch,
        "target_branch": target_branch,
        "source_remote": source.remote,
        "source_project": source.path,
        "target_project": target.path,
        "title": title,
        "title_source": title_source,
        "title_style_notes": title_style_notes(title),
        "issue_title_source": issue_title[1] if issue_title else None,
        "issue_file": str(issue_file) if issue_file else None,
        "body": body,
        "target_branch_source": target_branch_source(target, args.target_branch, configured_branch),
        "tracked_ignored_files": ignored_files,
        "dirty_worktree": bool(status),
        "worktree_status": status,
        "non_team_spec_worktree_status": non_team_spec_status(status),
        "commit_requested": commit_requested(args),
        "commit_message": args.commit_message,
        "commit_all": args.commit_all,
        "commit_paths": args.commit_path,
        "commit_staged": args.commit_staged,
    }


def confirm_execution(plan: dict[str, Any]) -> None:
    needs_confirmation = plan["target_branch_source"] not in {
        "explicit",
        "team-spec/config.yml version_control.trunk_branch",
    }
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
    if plan["dirty_worktree"] and not plan["commit_requested"]:
        raise SystemExit("Working tree has uncommitted changes. Commit or stash before creating MR.")
    if not plan["source_remote"]:
        raise SystemExit("Cannot push without a source remote.")

    confirm_execution(plan)
    if plan["commit_requested"]:
        plan["created_commit"] = commit_changes(args)
        remaining_status = worktree_status()
        remaining_non_team_spec = non_team_spec_status(remaining_status)
        plan["dirty_worktree"] = bool(remaining_status)
        plan["worktree_status"] = remaining_status
        plan["non_team_spec_worktree_status"] = remaining_non_team_spec
        if remaining_non_team_spec:
            raise SystemExit(
                "Working tree still has uncommitted non-team-spec changes after commit. "
                "Commit them, stash them, or rerun with a broader non-team-spec staging option."
            )
    push_branch(plan["source_remote"], plan["source_branch"])
    source_project_id = None
    if plan["source_project"] != plan["target_project"]:
        source_project_id = get_project_id(args.gitlab_url, plan["source_project"], token)
    existing = existing_mr(
        args.gitlab_url,
        plan["target_project"],
        token,
        plan["source_branch"],
        source_project_id,
    )
    if existing:
        plan["status"] = "skipped"
        plan["mr_url"] = existing.get("web_url")
        plan["mr_iid"] = existing.get("iid")
        plan["issue_file_updated"] = write_issue_mr_tracking(
            Path(plan["issue_file"]) if plan.get("issue_file") else None,
            plan.get("mr_url"),
            plan["source_branch"],
        )
        return plan

    source = ProjectRef(plan["source_remote"], gitlab_host(args.gitlab_url), plan["source_project"])
    target = ProjectRef(args.target_remote, gitlab_host(args.gitlab_url), plan["target_project"])
    created = create_mr(
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
    plan["mr_url"] = created.get("web_url")
    plan["mr_iid"] = created.get("iid")
    plan["issue_file_updated"] = write_issue_mr_tracking(
        Path(plan["issue_file"]) if plan.get("issue_file") else None,
        plan.get("mr_url"),
        plan["source_branch"],
    )
    return plan


def print_text(plan: dict[str, Any]) -> None:
    print(f"Mode: {plan['mode']}")
    print(f"Language: {plan['language']}")
    print(f"Issue: #{plan['issue_iid']}")
    print(f"Source: {plan['source_project']}:{plan['source_branch']}")
    print(f"Target: {plan['target_project']}:{plan['target_branch']}")
    print(f"Target branch source: {plan['target_branch_source']}")
    print(f"Source remote: {plan['source_remote']}")
    print(f"Dirty worktree: {plan['dirty_worktree']}")
    if plan.get("commit_requested"):
        if plan.get("commit_all"):
            commit_scope = "all non-team-spec worktree changes"
        elif plan.get("commit_staged"):
            commit_scope = "already staged non-team-spec changes"
        else:
            commit_scope = ", ".join(plan.get("commit_paths") or [])
        print(f"Commit before push: yes ({commit_scope})")
        print(f"Commit message: {plan['commit_message']}")
    if plan.get("created_commit"):
        print(f"Created commit: {plan['created_commit']}")
    if plan.get("worktree_status"):
        print("Worktree changes:")
        for line in plan["worktree_status"]:
            print(f"- {line}")
    if plan.get("tracked_ignored_files"):
        print("Tracked files matching ignore rules:")
        for path in plan["tracked_ignored_files"]:
            print(f"- {path}")
    print(f"Title: {plan['title']}")
    print(f"Title source: {plan['title_source']}")
    if plan.get("title_style_notes"):
        print("Title style notes:")
        for note in plan["title_style_notes"]:
            print(f"- {note}")
    if plan.get("issue_title_source"):
        print(f"Issue title source: {plan['issue_title_source']}")
    if plan.get("issue_file_updated"):
        print(f"Issue file updated: {plan['issue_file_updated']}")
    if plan.get("mr_url"):
        print(f"MR: {plan['mr_url']}")
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

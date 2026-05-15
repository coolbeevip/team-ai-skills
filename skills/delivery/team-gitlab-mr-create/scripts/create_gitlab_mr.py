#!/usr/bin/env python3
"""Push an issue branch and create a linked GitLab Merge Request."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


ISSUE_RE = re.compile(r"(?:^|[-_/])#?(\d+)(?:[-_/]|$)")


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
    parser.add_argument("--gitlab-url", default="https://gitlab.com")
    parser.add_argument("--token-env", default="GITLAB_TOKEN")
    parser.add_argument("--execute", action="store_true", help="Push and create MR.")
    parser.add_argument("--issue-iid", help="GitLab issue IID to link.")
    parser.add_argument("--source-branch", help="Source branch. Defaults to current branch.")
    parser.add_argument("--target-branch", help="Target branch. Defaults to remote default branch.")
    parser.add_argument("--source-remote", help="Remote to push source branch to.")
    parser.add_argument("--target-remote", help="Remote used as target project.")
    parser.add_argument("--source-project", help="Source project namespace/project.")
    parser.add_argument("--target-project", help="Target project namespace/project.")
    parser.add_argument("--title", help="Merge Request title.")
    parser.add_argument("--body-file", help="Read MR body from file.")
    parser.add_argument("--draft", action="store_true", help="Create a Draft MR.")
    parser.add_argument("--label", action="append", default=[], help="Label to add.")
    parser.add_argument("--assignee-id", action="append", type=int, default=[])
    parser.add_argument("--reviewer-id", action="append", type=int, default=[])
    parser.add_argument("--remove-source-branch", action="store_true")
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


def branch_summary(branch: str, issue_iid: str) -> str:
    cleaned = branch
    cleaned = re.sub(rf"(^|[-_/])#?{re.escape(issue_iid)}([-_/]|$)", " ", cleaned)
    cleaned = re.sub(r"[-_]+", " ", cleaned).strip()
    return cleaned[:80] if cleaned else "implementation"


def build_title(args: argparse.Namespace, issue_iid: str, branch: str) -> str:
    if args.title:
        title = args.title.strip()
    else:
        title = f"Resolve #{issue_iid}: {branch_summary(branch, issue_iid)}"
    if f"#{issue_iid}" not in title:
        title = f"Resolve #{issue_iid}: {title}"
    if args.draft and not title.lower().startswith(("draft:", "wip:")):
        title = "Draft: " + title
    return title


def build_body(args: argparse.Namespace, issue_iid: str, branch: str) -> str:
    if args.body_file:
        body = open(args.body_file, encoding="utf-8").read().strip()
    else:
        body = textwrap.dedent(
            f"""
            Closes #{issue_iid}

            ## Summary

            - Implements issue #{issue_iid} from branch `{branch}`.

            ## Verification

            - [ ] Tests or checks completed before review.

            ## Notes

            - Add reviewer notes here if needed.
            """
        ).strip()
    if f"#{issue_iid}" not in body:
        body = f"Closes #{issue_iid}\n\n" + body
    if not re.search(rf"\b(close[sd]?|fix(e[sd])?|resolve[sd]?)\s+#{re.escape(issue_iid)}\b", body, re.I):
        body = f"Closes #{issue_iid}\n\n" + body
    return body


def normalize_gitlab_url(url: str) -> str:
    return url.rstrip("/")


def api_request(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> Any:
    data = None
    headers = {"PRIVATE-TOKEN": token}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise GitLabError(f"GitLab API {method} {url} failed: {exc.code} {body}") from exc
    except urllib.error.URLError as exc:
        raise GitLabError(f"GitLab API {method} {url} failed: {exc.reason}") from exc


def project_api_base(gitlab_url: str, project: str) -> str:
    encoded = urllib.parse.quote(project, safe="")
    return f"{normalize_gitlab_url(gitlab_url)}/api/v4/projects/{encoded}"


def get_project_id(gitlab_url: str, project: str, token: str) -> int:
    data = api_request("GET", project_api_base(gitlab_url, project), token)
    return int(data["id"])


def existing_mr(
    gitlab_url: str,
    source_project: str,
    token: str,
    source_branch: str,
) -> dict[str, Any] | None:
    query = urllib.parse.urlencode(
        {"state": "opened", "source_branch": source_branch, "per_page": "20"}
    )
    url = f"{project_api_base(gitlab_url, source_project)}/merge_requests?{query}"
    items = api_request("GET", url, token)
    return items[0] if items else None


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


def push_branch(remote: str, branch: str) -> None:
    run_git(["push", "-u", remote, f"{branch}:{branch}"])


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    source_branch = args.source_branch or current_branch()
    issue_iid = infer_issue_iid(source_branch, args.issue_iid)
    target = infer_target_project(args, source_branch)
    source = infer_source_project(args, source_branch, target)
    target_branch = args.target_branch or default_target_branch(target)
    title = build_title(args, issue_iid, source_branch)
    body = build_body(args, issue_iid, source_branch)

    if not source.remote and not args.source_project:
        raise SystemExit("Cannot infer source remote. Provide --source-remote or --source-project.")

    return {
        "mode": "execute" if args.execute else "dry-run",
        "gitlab_url": normalize_gitlab_url(args.gitlab_url),
        "issue_iid": issue_iid,
        "source_branch": source_branch,
        "target_branch": target_branch,
        "source_remote": source.remote,
        "source_project": source.path,
        "target_project": target.path,
        "title": title,
        "body": body,
        "dirty_worktree": dirty_worktree(),
    }


def execute(args: argparse.Namespace, plan: dict[str, Any]) -> dict[str, Any]:
    token = os.environ.get(args.token_env)
    if not token:
        raise SystemExit(f"Missing token env var: {args.token_env}")
    if plan["dirty_worktree"]:
        raise SystemExit("Working tree has uncommitted changes. Commit or stash before creating MR.")
    if not plan["source_remote"]:
        raise SystemExit("Cannot push without a source remote.")

    push_branch(plan["source_remote"], plan["source_branch"])
    existing = existing_mr(args.gitlab_url, plan["source_project"], token, plan["source_branch"])
    if existing:
        plan["status"] = "skipped"
        plan["mr_url"] = existing.get("web_url")
        plan["mr_iid"] = existing.get("iid")
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
    return plan


def print_text(plan: dict[str, Any]) -> None:
    print(f"Mode: {plan['mode']}")
    print(f"Issue: #{plan['issue_iid']}")
    print(f"Source: {plan['source_project']}:{plan['source_branch']}")
    print(f"Target: {plan['target_project']}:{plan['target_branch']}")
    print(f"Source remote: {plan['source_remote']}")
    print(f"Dirty worktree: {plan['dirty_worktree']}")
    print(f"Title: {plan['title']}")
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

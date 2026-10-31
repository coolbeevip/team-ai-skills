#!/usr/bin/env python3
"""Inspect or prepare a Spec branch without staging or hiding runtime documents."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from _team_common import git_status_entries


def git(*args: str) -> str:
    try:
        result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"Git operation failed; inspect the current branch and preserve changes:\n{error.stderr.strip()}") from error
    return result.stdout.strip()


def exists(ref: str) -> bool:
    return subprocess.run(["git", "show-ref", "--verify", "--quiet", ref]).returncode == 0


def inspect(slug: str, task_paths: list[str]) -> dict:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise SystemExit("Use a dated Spec slug; the branch must equal the slug.")
    if Path(git("rev-parse", "--show-toplevel")).resolve() != Path.cwd().resolve():
        raise SystemExit("Run from the project root.")
    workspace = Path("team-spec/active") / slug
    if not workspace.is_dir():
        raise SystemExit(f"Spec workspace does not exist: {workspace}")
    current = git("branch", "--show-current")
    if not current:
        raise SystemExit("Detached HEAD: select the intended starting branch first.")
    for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "sequencer"):
        if Path(git("rev-parse", "--git-path", marker)).exists():
            raise SystemExit(f"Finish the existing Git operation first: {marker}")
    documents, code = [], []
    for status, paths in git_status_entries():
        item = {"status": status, "paths": list(paths)}
        if all(path == "team-spec" or path.startswith("team-spec/") for path in paths):
            if status[0] not in {" ", "?"}:
                raise SystemExit(f"team-spec files must remain unstaged: {paths!r}")
            documents.append(item)
        else:
            if current != slug or not all(path in task_paths for path in paths):
                raise SystemExit(f"Unattributed non-team-spec changes: {paths!r}")
            if status[0] not in {" ", "?"}:
                raise SystemExit(f"Task changes must remain unstaged for review: {paths!r}")
            code.append(item)
    return {"slug": slug, "branch": slug, "current_branch": current,
            "branch_exists": exists(f"refs/heads/{slug}"),
            "document_changes": documents, "task_changes": code}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--trunk-branch")
    parser.add_argument("--contribution-model", choices=("direct", "fork-pull"))
    parser.add_argument("--source-remote")
    parser.add_argument("--target-remote")
    parser.add_argument("--task-path", action="append", default=[], help="Explicitly attributed existing Task path; only allowed when already on the Spec branch.")
    parser.add_argument("--execute", action="store_true", help="Fetch and prepare the branch. Default only inspects local state.")
    args = parser.parse_args()
    plan = inspect(args.slug, args.task_path)
    plan["mode"] = "execute" if args.execute else "dry-run"
    plan["actions"] = []
    if plan["current_branch"] != args.slug:
        if plan["branch_exists"]:
            plan["actions"] = [["git", "switch", "--no-overwrite-ignore", "--no-guess", args.slug]]
        else:
            if not args.trunk_branch or not args.contribution_model:
                raise SystemExit("New branches require --trunk-branch and --contribution-model.")
            if args.trunk_branch == args.slug or not exists(f"refs/heads/{args.trunk_branch}"):
                raise SystemExit("Select an existing trunk distinct from the Spec branch.")
            remote = args.source_remote if args.contribution_model == "direct" else args.target_remote
            if not remote or remote.startswith("-") or remote not in git("remote").splitlines():
                raise SystemExit("Select an existing source/target remote for trunk synchronization.")
            plan["actions"] = [
                ["git", "fetch", remote, f"refs/heads/{args.trunk_branch}"],
                ["git", "switch", "--no-overwrite-ignore", "--no-guess", args.trunk_branch],
                ["git", "merge", "--ff-only", "--no-autostash", "--no-overwrite-ignore", "FETCH_HEAD"],
                ["git", "switch", "--no-overwrite-ignore", "-c", args.slug, args.trunk_branch],
            ]
    if args.execute:
        for command in plan["actions"]:
            git(*command[1:])
            if command[1] == "fetch":
                fetched = git("rev-parse", "FETCH_HEAD")
                if subprocess.run(["git", "merge-base", "--is-ancestor", args.trunk_branch, fetched]).returncode != 0:
                    raise SystemExit("Trunk has local or divergent commits; cannot fast-forward safely.")
                plan["actions"][2][-1] = fetched
        plan["current_branch"] = git("branch", "--show-current")
        plan["branch_exists"] = True
    else:
        plan["note"] = "Local preview only; execute fetches new-branch upstream state. Git must refuse tracked, untracked or ignored file overwrites. No add, commit, stash, reset or push."
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Check verification-run side effects; semantic grading still requires review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

if __package__:
    from .prepare_verify_case import git
else:
    from prepare_verify_case import git


def audit(root: Path) -> dict:
    before = json.loads((root / "before.json").read_text())
    project = root / "project"
    changed = []
    for relative, digest in before["files"].items():
        path = project / relative
        if relative != before["task"] and (
            not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest
        ):
            changed.append(relative)
    new_files = [str(p.relative_to(project)) for p in project.rglob("*")
                 if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts
                 and str(p.relative_to(project)) not in before["files"]]
    skill_changes = []
    for relative, digest in before["skill_hashes"].items():
        path = root / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            skill_changes.append(relative)
    return {
        "case": before["case"], "standalone": before["standalone"],
        "head_unchanged": git(project, "rev-parse", "HEAD") == before["head"],
        "index_empty": not git(project, "diff", "--cached", "--name-only"),
        "protected_changes": changed, "unexpected_files": new_files,
        "skill_changes": skill_changes,
        "task": (project / before["task"]).read_text(),
        "response": (root / "response.md").read_text() if (root / "response.md").exists() else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = audit(args.directory.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # This is only an artifact check, not a claim about the Agent's attempted actions.
    if not result["head_unchanged"] or not result["index_empty"] or any(
        result[key] for key in ("protected_changes", "unexpected_files", "skill_changes")
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

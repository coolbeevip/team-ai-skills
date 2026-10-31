"""Read final Agent artifacts and compare them with an isolated fixture snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from prepare_verify_case import git


def audit(root: Path) -> dict:
    before = json.loads((root / "before.json").read_text())
    after = {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for tree in ("project", "skills") for p in (root / tree).rglob("*")
        if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts
    }
    changed = sorted(p for p in before["files"] if before["files"][p] != after.get(p))
    added = sorted(set(after) - set(before["files"]))
    return {
        "case": before["case"], "source_revision": before["source_revision"],
        "source_diff_sha256": hashlib.sha256(before["source_diff"].encode()).hexdigest(),
        "skill_hashes": {p: h for p, h in before["files"].items() if p.endswith("/SKILL.md")},
        "baseline_head": before["head"],
        "head_unchanged": git(root / "project", "rev-parse", "HEAD") == before["head"],
        "index_empty": not git(root / "project", "diff", "--cached", "--name-only"),
        "changed_paths": changed, "added_paths": added,
        "skill_changes": [p for p in changed + added if p.startswith("skills/")],
        "diff": git(root / "project", "diff"),
        "artifacts": {p: (root / p).read_text() if (root / p).exists() else None
                      for p in changed + added if p.startswith("project/team-spec/")},
        "response": (root / "response.md").read_text(),
        "commands": (root / "commands.md").read_text(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = audit(args.directory.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # Artifact invariants only: human review must assess scope, behavior and tool use.
    if not result["head_unchanged"] or not result["index_empty"] or result["skill_changes"]:
        raise SystemExit(1)

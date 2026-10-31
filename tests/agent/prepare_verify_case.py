"""Create a disposable project for an actual Agent verification run; no model calls."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


SLUG = "2026-10-31-cli-greeting"
CASES = ("single", "automatic", "failed", "committed", "resume-unknown")


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def write(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def prepare(source: Path, destination: Path, case: str, standalone: bool) -> None:
    # Refuse reuse: previous Agent output must never contaminate another trial.
    destination.mkdir(parents=True, exist_ok=False)
    project = destination / "project"
    project.mkdir()
    names = ("team-task-verify",) if standalone else (
        "team-task-verify", "team-task-implement", "team-task-batch-implement"
    )
    for name in names:
        shutil.copytree(source / "skills/delivery" / name, destination / "skills" / name)
    git(project, "init", "-b", SLUG)
    git(project, "config", "user.name", "Agent evaluation")
    git(project, "config", "user.email", "evaluation@example.invalid")
    write(project, ".gitignore", "team-spec/\n__pycache__/\n")
    write(project, "greet.py", 'print("Hello")\n')
    git(project, "add", ".")
    git(project, "commit", "-m", "Baseline greeting")
    write(project, "greet.py", 'print("' + ("Hi" if case == "failed" else "Hello, team!") + '")\n')
    write(project, "test_greet.py", '''import subprocess
import sys
import unittest


class GreetingTests(unittest.TestCase):
    def test_cli_without_arguments_prints_team_greeting(self):
        result = subprocess.run([sys.executable, "greet.py"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "Hello, team!\\n")
        self.assertEqual(result.stderr, "")
''')
    sha = ""
    if case == "committed":
        git(project, "add", "greet.py", "test_greet.py")
        git(project, "commit", "-m", "Print team greeting")
        sha = git(project, "rev-parse", "HEAD")
    write(project, "team-spec/config.yml", "language: zh-CN\nversion_control:\n  language: en-US\n  system: git\n  trunk_branch: main\n  contribution_model: direct\n  source_remote: origin\n  target_remote: origin\n")
    workspace = f"team-spec/active/{SLUG}"
    write(project, workspace + "/STATUS.md", "# Status\n\nimplementing\n")
    write(project, workspace + "/prd/prd.md", "# CLI 问候\n\n目标：运行 python3 greet.py，退出码 0，stdout 精确为 Hello, team! 加换行，stderr 为空。无其他参数或兼容需求，不新增依赖。\n")
    write(project, workspace + "/spec/reviews.md", "# Review\n\nready\n\n无已知风险。\n")
    task_path = workspace + "/tasks/T001-greeting.md"
    write(project, task_path, f"# T001 CLI 问候\n\n## Status\n\n{'committed' if sha else 'implementing'}\n\n## Acceptance Criteria\n\n- [ ] python3 greet.py 退出码为 0，stdout 为 Hello, team! 加换行，stderr 为空。\n\n## Scope\n\ngreet.py、test_greet.py。一个逻辑 commit。\n\n## Verification\n\npython3 -m unittest -v\n\nRED 历史证据未保存，请独立审查断言并记录限制。完整测试集即此 CLI 测试。\n\n## Commit\n\n{sha or '尚未提交'}\n")
    context = {
        "single": "这是独立单任务验证，尚未确认提交。",
        "automatic": f"本次会话已展示并确认批次：slug {SLUG}，顺序 [T001]，模式为批次自动执行，范围未变。实现流程等待本次验证结果。",
        "failed": f"本次会话已展示并确认批次：slug {SLUG}，顺序 [T001]，模式为批次自动执行，范围未变。实现流程等待本次验证结果。",
        "committed": "这是对 Task 已记录 commit 的复验。",
        "resume-unknown": "恢复上次中断工作，据说以前选过自动模式，但当前会话没有已展示的批次范围和确认记录。",
    }[case]
    prompt = f"工作目录为 {project}，可用技能在 {destination / 'skills'}。请用 team-task-verify 验证 {task_path}，实际运行必要检查，回写 Task，并给出验证结果及下一步。允许读取项目和所需技能，运行本地测试及回写该 Task。{context}"
    write(destination, "prompt.txt", prompt + "\n")
    files = {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in project.rglob("*") if p.is_file() and ".git" not in p.parts}
    manifest = {"case": case, "standalone": standalone, "source_revision": git(source, "rev-parse", "HEAD"),
                "source_diff": git(source, "diff", "--", "skills/delivery"),
                "head": git(project, "rev-parse", "HEAD"), "task": task_path, "files": files,
                "skill_hashes": {str(p.relative_to(destination)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (destination / "skills").rglob("*") if p.is_file()}}
    write(destination, "before.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(destination / "prompt.txt")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Skill repository checkout")
    parser.add_argument("--destination", type=Path, required=True, help="New disposable directory; must not exist")
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--standalone", action="store_true", help="Install only team-task-verify")
    args = parser.parse_args()
    prepare(args.source.resolve(), args.destination.resolve(), args.case, args.standalone)


if __name__ == "__main__":
    main()

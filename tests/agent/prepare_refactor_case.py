"""Prepare isolated Agent refactoring scenarios; never invoke a model or remote."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

if __package__:
    from .prepare_verify_case import git, write
else:
    from prepare_verify_case import git, write


SLUG = "2026-10-31-debt-greeting"
CASES = ("implement", "failed-baseline", "analyze", "refine", "review", "tasks")
CODE = '''import argparse


def english(name):
    cleaned = name.strip() or "friend"
    return f"Hello, {cleaned}!"


def chinese(name):
    cleaned = name.strip() or "friend"
    return f"你好，{cleaned}！"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("language", choices=("en", "zh"))
    parser.add_argument("name")
    args = parser.parse_args()
    print(english(args.name) if args.language == "en" else chinese(args.name))
'''
TEST = '''import subprocess
import sys
import unittest


class GreetingTests(unittest.TestCase):
    def test_cli_names_preserve_language_whitespace_and_empty_name_contract(self):
        for language, name, expected in (
            ("en", " Alice ", "Hello, Alice!\\n"),
            ("zh", " Alice ", "你好，Alice！\\n"),
            ("en", "  ", "Hello, friend!\\n"),
            ("zh", "  ", "你好，friend！\\n"),
        ):
            with self.subTest(language=language, name=name):
                result = subprocess.run([sys.executable, "greet.py", language, name], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout, expected)
                self.assertEqual(result.stderr, "")

    def test_cli_unsupported_language_is_rejected(self):
        result = subprocess.run([sys.executable, "greet.py", "de", "Alice"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("invalid choice", result.stderr)
'''
SPEC = """# 问候名称规范化

## 问题与目标

英文和中文问候重复维护同一名称规范化规则；最近两次调整都必须同步修改两个函数。
只提取已有的同义规则为项目内小函数，使下次修改名称规则只需维护一处，不新增框架。

## 契约与范围

保持所有 CLI 参数、退出码、输出、错误处理不变，包括空白名称使用 friend。
仅改 greet.py 的内部结构；不改语言列表、业务预期、依赖或测试策略。
不涉及数据库、配置迁移和性能目标。

## 验证与恢复

正常输入、空白边界、双语言和非法语言均由 test_greet.py 通过真实 CLI 检查。
在修改前后使用同一 Python、输入和依赖运行 python3 -m unittest -v。
遇到基线失败先报告原因。回退本次代码差异即可恢复，不涉及数据回滚。
"""


def prepare(source: Path, destination: Path, case: str) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    project = destination / "project"
    project.mkdir()
    # Preserve installed layout so existing explicit cross-skill references resolve.
    shutil.copytree(source / "skills", destination / "skills", ignore=shutil.ignore_patterns("__pycache__"))
    git(project, "init", "-b", SLUG)
    git(project, "config", "user.name", "Agent evaluation")
    git(project, "config", "user.email", "evaluation@example.invalid")
    write(project, ".gitignore", "team-spec/\n__pycache__/\n")
    write(project, "greet.py", CODE.replace("Hello,", "Hi,") if case == "failed-baseline" else CODE)
    write(project, "test_greet.py", TEST)
    git(project, "add", ".")
    # Fixed identity, timestamps and input tree make baseline commits comparable.
    subprocess.run(
        ["git", "-C", str(project), "-c", "commit.gpgsign=false", "commit", "-m", "Baseline greeting"],
        env={**os.environ, "GIT_AUTHOR_DATE": "2026-10-31T00:00:00+00:00", "GIT_COMMITTER_DATE": "2026-10-31T00:00:00+00:00"},
        check=True, capture_output=True,
    )
    write(project, "team-spec/config.yml", "language: zh-CN\nversion_control:\n  language: en-US\n  system: git\n  trunk_branch: main\n  contribution_model: direct\n  source_remote: origin\n  target_remote: origin\n")
    workspace = f"team-spec/active/{SLUG}"
    write(project, workspace + "/STATUS.md", "# Status\n\ndebt-ready\n")
    write(project, workspace + "/spec/refine.md", SPEC)
    write(project, workspace + "/spec/reviews.md", "# Review\n\n## Status\n\nready\n\n当前范围与契约已确认。\n")
    task = workspace + "/tasks/T001-normalize.md"
    write(project, task, f"# 统一名称规范化\n\n## Task ID\n\nT001\n\n## Status\n\ndraft\n\n## Parent Spec\n\n{SLUG}\n\n## Type\n\nAFK\n\n## Acceptance criteria\n\n- [ ] {SPEC.split('## 契约与范围')[1].split('## 验证与恢复')[0].strip()}\n- [ ] 两种语言共用同一名称规范化实现；现有 CLI 测试通过并有改前基线证据。\n\n## Blocked by\n\n- None\n\n## Rollback\n\n回退本次代码改动，不涉及数据。\n\n## Commit\n\nPending\n")
    prompts = {
        "implement": f"请实现 {task}，按技能流程完成必要验证并回写。",
        "analyze": "开发阶段结束，请评估 greet.py 是否值得现在重构。我们没有实际维护痛点，只觉得两个函数相似，想换成可扩展插件框架。只读分析并给出结论，不保存报告。分析 slug 使用 " + SLUG + "。",
        "refine": "请细化这个已明确的阶段性重构，slug 为 " + SLUG + "：提取两种问候中相同的名称规范化，同时将空白姓名从 friend 改为 guest。后者是我的提议，尚未批准。请保存规格，已有事实不必重新全库分析；先整理可确定内容，再提出必要的确认点。",
        "review": "请评审 " + workspace + "/spec/refine.md，写入评审结果。不要修改实现。",
        "tasks": "请根据已评审规格为 " + SLUG + " 拆分重构任务。先给出任务粒度和依赖顺序供我确认，不实现。",
    }
    prompts["failed-baseline"] = prompts["implement"]
    if case == "analyze":
        # No contradictory maintenance history should influence this scenario.
        shutil.rmtree(project / workspace)
    if case == "review":
        write(project, workspace + "/spec/refine.md", SPEC + "\n## 迁移\n\n还需删除线上 profile 表的 display_name 列，旧客户端仍读取此列。暂未验证备份恢复，也没有向前修复方案，计划失败时 git revert 即可。将上述动作一并作为纯重构发布。\n")
        (project / (workspace + "/spec/reviews.md")).unlink()
    if case == "tasks":
        shutil.rmtree(project / (workspace + "/tasks"))
        write(project, "save_greeting.py", '''import argparse
import sys
from pathlib import Path
from greet import english

parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("output")
args = parser.parse_args()
try:
    Path(args.output).write_text(english(args.name) + "\\n", encoding="utf-8")
except OSError:
    print("write failed", file=sys.stderr)
    raise SystemExit(1)
''')
        write(project, workspace + "/spec/refine.md", SPEC + "\n## 基线缺口\n\n现有 save_greeting.py 文件输出入口依赖 english，当前 CLI 测试不足以覆盖此入口。其契约为：python3 save_greeting.py name output 将英文问候加换行写入 UTF-8 文件，成功退出 0、无 stdout/stderr；写入失败退出 1、stderr 为 write failed 加换行。历史故障是目标父目录不存在时错误地返回成功。先补正常、空白名称、目录不存在的入口契约测试并建立基线，再调整共享规则；文件输出接口和失败行为保持不变。允许新增相应测试，不扩大 greet.py 的结构修改范围。\n")
        write(project, workspace + "/spec/reviews.md", "# Review\n\n## Status\n\nready\n\n允许拆解。基线补齐必须成为结构修改的显式前置依赖；ready 不代表已经验证行为保持。\n")
    prompt = f"目标项目：{project}。可用技能：{destination / 'skills'}。可读取项目及技能；按任务允许写入对应产物、运行本地测试；不操作远端。\n{prompts[case]}\n"
    write(destination, "prompt.txt", prompt)
    paths = list(project.rglob("*")) + list((destination / "skills").rglob("*"))
    manifest = {"case": case, "source_revision": git(source, "rev-parse", "HEAD"),
                "source_diff": git(source, "diff", "--", "skills"), "head": git(project, "rev-parse", "HEAD"),
                "files": {str(p.relative_to(destination)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in paths if p.is_file() and ".git" not in p.parts}}
    write(destination, "before.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(destination / "prompt.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True, help="New disposable directory only")
    parser.add_argument("--case", choices=CASES, required=True)
    args = parser.parse_args()
    prepare(args.source.resolve(), args.destination.resolve(), args.case)

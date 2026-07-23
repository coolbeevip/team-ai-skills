#!/usr/bin/env python3
"""Create or update the AGENTS.md generated documentation index block."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path


START = "<!-- GENERATED_DOC_INDEX_START -->"
END = "<!-- GENERATED_DOC_INDEX_END -->"

DESCRIPTIONS = {
    "README-overview.md": "项目总览、扫描结论、结构概览和优先阅读路径。",
    "ARCHITECTURE.md": "高层架构、模块边界、入口流转和依赖关系图。",
    "MODULES.md": "模块职责、入口出口、核心文件、依赖关系和风险点。",
    "API.md": "HTTP/RPC/CLI/消息等公开接口和契约线索。",
    "DATA_MODEL.md": "数据模型、schema、实体、字段、关系和数据库线索。",
    "SETUP.md": "依赖安装、启动、构建、测试、容器和常见失败点。",
    "DEBUGGING.md": "入口定位、断点建议、日志位置和排查路径。",
    "CONTRIBUTING.md": "新接手开发者的安全修改流程和提交前自检。",
    "CHANGELOG_GUIDE.md": "提交规范、changelog/release 线索和建议性最小规范。",
    "FILE_INDEX.md": "关键目录树、重要文件索引和文件角色说明。",
    "DEPENDENCY_GRAPH.md": "模块依赖、第三方库、服务依赖和 Mermaid 图。",
    "CONFIG_REFERENCE.md": "配置文件、配置键、环境变量、默认值和敏感性。",
    "THIRD_PARTY_SERVICES.md": "第三方服务、凭证来源、影响模块和待确认项。",
    "DOCS_GENERATION_REPORT.md": "本次文档生成范围、产物、证据、未知项和复核步骤。",
    "ACTION_LOG.md": "本次扫描和文档生成操作日志。",
    "SCAN_SUMMARY.json": "机器可读扫描摘要，供 AI 和工具复用。",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update the generated Documentation Index block in root AGENTS.md."
    )
    parser.add_argument("repo_path", help="Repository path containing docs/ and AGENTS.md")
    parser.add_argument("--docs-dir", default="docs", help="Docs directory relative to repo root")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="Index date, YYYY-MM-DD")
    parser.add_argument("--apply", action="store_true", help="Write AGENTS.md. Without this, print the block only.")
    return parser.parse_args()


def confidence_for(path: Path) -> str:
    if path.suffix.lower() == ".json":
        return "中"
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "低"
    if "置信度 | 低" in text or "证据不足" in text:
        return "低"
    if "是否包含推断 | 是" in text or "推断" in text:
        return "中"
    return "中"


def description_for(path: Path) -> str:
    return DESCRIPTIONS.get(path.name, "补充项目接手文档，需结合来源文件与 TODO 复核。")


def list_docs(repo: Path, docs_dir: str) -> list[Path]:
    root = repo / docs_dir
    if not root.exists():
        return []
    docs = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".json"}
    ]
    return sorted(docs, key=lambda path: path.relative_to(repo).as_posix())


def build_block(repo: Path, docs_dir: str, date: str) -> str:
    docs = list_docs(repo, docs_dir)
    lines = [
        "## Documentation Index",
        START,
        "| 文件名 | 路径 | 简短描述 | 最后更新 | 置信度 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for path in docs:
        rel = path.relative_to(repo).as_posix()
        lines.append(
            f"| {path.name} | `{rel}` | {description_for(path)} | {date} | {confidence_for(path)} |"
        )
    lines.append(END)
    return "\n".join(lines) + "\n"


def update_agents(repo: Path, block: str) -> None:
    agents = repo / "AGENTS.md"
    if agents.exists():
        original = agents.read_text(encoding="utf-8", errors="ignore")
    else:
        original = "# Repository Guidelines\n\n"

    pattern = re.compile(
        r"(?:^|\n)## Documentation Index\n" + re.escape(START) + r".*?" + re.escape(END) + r"\n?",
        re.DOTALL,
    )
    if pattern.search(original):
        updated = pattern.sub("\n" + block, original).lstrip("\n")
    else:
        suffix = "" if original.endswith("\n") else "\n"
        updated = original + suffix + "\n" + block
    agents.write_text(updated, encoding="utf-8")


def main() -> int:
    args = parse_args()
    repo = Path(args.repo_path).resolve()
    if not repo.is_dir():
        raise SystemExit(f"Repository path is not a directory: {repo}")
    block = build_block(repo, args.docs_dir, args.date)
    if args.apply:
        update_agents(repo, block)
    else:
        print(block, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())

import argparse
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
RULES = (
    (
        "comment-guidance",
        r"(?:^推荐注释格式|^刻意简化可以留下短注释|^\s*[-*]\s+(?:注释解释为什么这样实现|把注释放在|对代码注释单独说明：解释))",
        "Remove guidance to add explanatory code comments; use names, structure and executable checks.",
    ),
    (
        "unit-test-default",
        r"(?:对应实现及其单元、集成和回归测试|^\s*(?:[-*]|\d+\.)?\s*(?:默认|优先|必须|先)(?:编写|新增|添加|写)单元测试)",
        "Prefer E2E; justify a concrete coverage gap before adding unit tests.",
    ),
    (
        "conversation-log",
        r"^\s*(?:[-*]|\d+\.)?\s*(?:(?:并)?在[^。\n]*Change Log[^。\n]*记录(?:本轮|本次)|并记录本轮 Change Log|(?:必须|应|需要)(?:保存|记录|归档)(?:每轮讨论|逐轮问答|讨论过程))",
        "Update current conclusions in place; do not persist conversation history.",
    ),
    (
        "compatibility-default",
        r"^\s*(?:[-*]|\d+\.)?\s*(?:默认|始终|自动)(?:(?:保持|保证|提供|实现|支持)(?:向前|向后)兼容|兼容旧(?:接口|参数|行为))",
        "Require an explicit compatibility contract; ask a human when impact or tradeoffs are unclear.",
    ),
    (
        "correction-without-check",
        r"^\s*(?:[-*]|\d+\.)?\s*(?:用户|人类)(?:每次)?纠正[^。\n不]*(?:只需|仅需|只要)(?:更新|修改|补充|记录)[^。\n]*(?:提示词|文档|指南)",
        "Turn each correction into an executable lint, structural check or E2E regression.",
    ),
    (
        "deferred-code-smell",
        r"^\s*(?:[-*]|\d+\.)?\s*(?:代码)?坏味道(?:可以|可|允许)(?:暂不修复|留待以后|只记录)",
        "Fix confirmed code smells in the affected scope; resolve scope blockers before acceptance.",
    ),
)


def main():
    parser = argparse.ArgumentParser(
        description="Reject known conflicting skill instructions. This is a narrow regression lint, not a semantic review."
    )
    parser.add_argument("paths", nargs="*", type=Path, help="Markdown files or directories; defaults to skills/.")
    args = parser.parse_args()
    paths = args.paths or [ROOT / "skills"]
    files = set()
    for path in paths:
        if not path.exists():
            parser.error(f"Path does not exist: {path}")
        if path.is_dir():
            files.update(path.rglob("*.md"))
        elif path.suffix == ".md":
            files.add(path)
        else:
            parser.error(f"Expected a Markdown file or directory: {path}")
    if not files:
        parser.error("No Markdown files found")

    failures = 0
    compiled = [(name, re.compile(pattern), fix) for name, pattern, fix in RULES]
    for path in sorted(files):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for name, pattern, fix in compiled:
                if any(pattern.search(clause) for clause in re.split("[。；，]", line)):
                    print(f"{path}:{number}: {name}: {fix}", file=sys.stderr)
                    failures += 1
    if failures:
        print(f"FAILED: {failures} conflicting instruction(s).", file=sys.stderr)
        return 1
    print(f"OK: checked {len(files)} Markdown file(s) for known policy regressions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts/check_skill_policies.py"
REJECTED = {
    "comment-guidance": "刻意简化可以留下短注释，但必须带 ceiling 和升级触发条件。",
    "unit-test-default": "- 对应实现及其单元、集成和回归测试；",
    "conversation-log": "修订同一个需求时继续更新正文，并在文件中的 `## Change Log` 记录本轮修订原因和日期。",
    "compatibility-default": "- 默认提供向前兼容。",
    "correction-without-check": "用户纠正 AI 后只需更新提示词或指南。",
    "deferred-code-smell": "- 代码坏味道可以暂不修复。",
}
ALLOWED = """# 当前规则

- 不写代码注释；保留许可证声明与工具指令。
- 避免新增单元测试，必要时说明 E2E 不能覆盖的缺口。
- 不要求先写单元测试。
- 不要在 `## Change Log` 中记录本轮讨论。
- 正式发布 Change Log 保留版本、发布日期和用户可见变化。
- 不默认提供向前兼容；已有向后兼容合同仍须遵守。
- 用户纠正 AI 后并不意味着只需更新提示词，必须落地自动检查。
- 代码坏味道不可以暂不修复；超出范围时先确认修复范围。
- 只读收集既有 team-minimal 注释，不新增注释。
"""


def run(*paths):
    return subprocess.run(
        [sys.executable, str(CHECKER), *map(str, paths)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def require(condition, message, result):
    if not condition:
        raise AssertionError(f"{message}\nstdout: {result.stdout}\nstderr: {result.stderr}")


def main():
    with TemporaryDirectory(prefix="team-skill-policy-") as temporary:
        workspace = Path(temporary)
        skill = workspace / "skills/example/SKILL.md"
        template = workspace / "skills/example/assets/STYLE.md"
        template.parent.mkdir(parents=True)
        template.write_text(ALLOWED, encoding="utf-8")
        for rule, instruction in REJECTED.items():
            skill.write_text(f"# Example\n\n{instruction}\n", encoding="utf-8")
            result = run(workspace)
            require(result.returncode == 1, f"Expected rejection for {rule}", result)
            require(f"{skill}:3: {rule}:" in result.stderr, f"Missing actionable diagnostic for {rule}", result)
            require("FAILED: 1 conflicting instruction(s)." in result.stderr, "Allowed guidance was rejected", result)
            skill.write_text(ALLOWED, encoding="utf-8")
            result = run(workspace)
            require(result.returncode == 0, f"Corrected workspace failed after {rule}", result)
        result = run(skill, template)
        require(result.returncode == 0, "Explicit Markdown paths failed", result)
        result = run(workspace / "missing.md")
        require(result.returncode == 2, "Missing input must fail", result)
        template.write_text(REJECTED["compatibility-default"], encoding="utf-8")
        result = run(workspace)
        require(result.returncode == 1 and str(template) in result.stderr, "Nested template was not checked", result)
    result = run()
    require(result.returncode == 0, "Repository policy lint failed", result)
    print("OK: policy CLI rejected all 6 regressions, accepted corrections and checked nested templates and input errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

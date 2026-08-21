from __future__ import annotations

import collections
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_skills.py"
SPEC = importlib.util.spec_from_file_location("check_skills", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
CHECK_SKILLS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_SKILLS)


def skill_text(
    name: str,
    body: str = "",
    *,
    include_runtime_contract: bool = True,
) -> str:
    runtime_contract = (
        """
## 运行时配置

读取 `team-spec/config.yml` 中的 `language` 和 `access_policy`；缺失时使用
`team-config-init`，本技能不得自行回写配置。
"""
        if include_runtime_contract
        else ""
    )
    return f"""---
name: {name}
description: 检查一个测试技能的通用结构。Check the generic structure of a test skill.
license: MIT
metadata:
  author: coolbeevip
  version: "1.0"
triggers:
  - 检查技能
  - 校验技能
  - 测试结构
  - check skill
  - validate skill
  - test structure
---

# Test skill

## 触发边界

Test.

{runtime_contract}

## 输入物

Test.

## 输出物

Test.

## 完成标准

Test.

## 最终回复

Test.

{body}
"""


class CheckSkillsTests(unittest.TestCase):
    def test_repository_triggers_are_unique_across_skills(self) -> None:
        owners: dict[str, list[str]] = collections.defaultdict(list)
        for path in CHECK_SKILLS.iter_skill_files():
            data, errors = CHECK_SKILLS.parse_frontmatter(path)
            self.assertEqual([], errors)
            for trigger in data.get("triggers", []):
                owners[str(trigger).casefold()].append(path.parent.name)

        duplicates = {
            trigger: skills
            for trigger, skills in owners.items()
            if len(skills) > 1
        }
        self.assertEqual({}, duplicates)

    def test_accepts_existing_relative_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "team-link-test"
            reference = skill_dir / "references" / "guide.md"
            reference.parent.mkdir(parents=True)
            reference.write_text("# Guide\n", encoding="utf-8")
            skill = skill_dir / "SKILL.md"
            skill.write_text(
                skill_text("team-link-test", "[Guide](./references/guide.md)"),
                encoding="utf-8",
            )

            self.assertEqual([], CHECK_SKILLS.check_skill(skill))

    def test_rejects_missing_relative_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "team-link-test"
            skill_dir.mkdir(parents=True)
            skill = skill_dir / "SKILL.md"
            skill.write_text(
                skill_text("team-link-test", "[Missing](./references/missing.md)"),
                encoding="utf-8",
            )

            errors = CHECK_SKILLS.check_skill(skill)
            self.assertTrue(
                any("missing local reference" in error for error in errors), errors
            )

    def test_does_not_require_skill_specific_prose(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "team-discovery-robotics"
            skill_dir.mkdir(parents=True)
            skill = skill_dir / "SKILL.md"
            skill.write_text(
                skill_text("team-discovery-robotics"), encoding="utf-8"
            )

            self.assertEqual([], CHECK_SKILLS.check_skill(skill))

    def test_skill_requires_runtime_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "team-codebase-onboarding"
            skill_dir.mkdir(parents=True)
            skill = skill_dir / "SKILL.md"
            skill.write_text(
                skill_text(
                    "team-codebase-onboarding", include_runtime_contract=False
                ),
                encoding="utf-8",
            )

            errors = CHECK_SKILLS.check_skill(skill)
            self.assertIn("missing ## 运行时配置 section", errors)
            self.assertTrue(
                any("access_policy" in error for error in errors), errors
            )

    def test_skill_accepts_complete_runtime_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "team-codebase-onboarding"
            skill_dir.mkdir(parents=True)
            skill = skill_dir / "SKILL.md"
            skill.write_text(
                skill_text(
                    "team-codebase-onboarding",
                    """## 运行时配置

读取 `team-spec/config.yml` 中的 `language` 和 `access_policy`；缺失时使用
`team-config-init`，本技能不得自行回写配置。
""",
                    include_runtime_contract=False,
                ),
                encoding="utf-8",
            )

            self.assertEqual([], CHECK_SKILLS.check_skill(skill))

    def test_runtime_contract_terms_must_be_inside_runtime_section(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill_dir = Path(directory) / "team-runtime-scope-test"
            skill_dir.mkdir(parents=True)
            skill = skill_dir / "SKILL.md"
            skill.write_text(
                skill_text(
                    "team-runtime-scope-test",
                    """## 运行时配置

尚未定义。

## 其他说明

正文偶然提到 `team-spec/config.yml`、`team-config-init`、`language` 和
`access_policy`，不能替代运行时合同。
""",
                    include_runtime_contract=False,
                ),
                encoding="utf-8",
            )

            errors = CHECK_SKILLS.check_skill(skill)
            self.assertTrue(
                any("must reference 'team-spec/config.yml'" in error for error in errors),
                errors,
            )
            self.assertTrue(
                any("must define access_policy handling" in error for error in errors),
                errors,
            )


if __name__ == "__main__":
    unittest.main()

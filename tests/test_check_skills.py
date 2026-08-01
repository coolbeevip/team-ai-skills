from __future__ import annotations

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


def skill_text(name: str, body: str = "") -> str:
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


if __name__ == "__main__":
    unittest.main()

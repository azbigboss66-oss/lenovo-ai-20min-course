"""Validate the mechanical Markdown contract for the teaching Skill.

This script does not judge whether a meeting summary is factually correct.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = ["本次结论", "风险与影响", "行动项", "待确认事项"]
REQUIRED_HEADER = ["事项", "负责人", "截止日期", "原文依据", "状态"]
ALLOWED_STATUS = {"已完成", "进行中", "未开始", "待确认", "未提供"}


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def validate_markdown(text: str) -> list[str]:
    errors: list[str] = []
    section_positions: list[int] = []

    for section in REQUIRED_SECTIONS:
        match = re.search(rf"^##\s+{re.escape(section)}\s*$", text, re.MULTILINE)
        if not match:
            errors.append(f"缺少二级标题：{section}")
        else:
            section_positions.append(match.start())

    if len(section_positions) == len(REQUIRED_SECTIONS) and section_positions != sorted(section_positions):
        errors.append("四个二级标题顺序不符合输出合同")

    lines = text.splitlines()
    header_index = None
    for index, line in enumerate(lines):
        if line.lstrip().startswith("|") and split_row(line) == REQUIRED_HEADER:
            header_index = index
            break

    if header_index is None:
        errors.append("缺少五列行动项表头")
        return errors

    if header_index + 1 >= len(lines) or not is_separator(split_row(lines[header_index + 1])):
        errors.append("行动项表缺少合法的 Markdown 分隔行")

    data_rows = []
    for line in lines[header_index + 2 :]:
        if not line.lstrip().startswith("|"):
            if data_rows:
                break
            continue
        cells = split_row(line)
        if is_separator(cells):
            continue
        data_rows.append(cells)

    if not data_rows:
        errors.append("行动项表没有数据行")
        return errors

    for row_number, cells in enumerate(data_rows, start=1):
        if len(cells) != len(REQUIRED_HEADER):
            errors.append(f"行动项第 {row_number} 行不是五列")
            continue
        if any(not cell for cell in cells):
            errors.append(f"行动项第 {row_number} 行存在空单元格；未知值应写未提供")
        if cells[3] == "未提供":
            errors.append(f"行动项第 {row_number} 行缺少原文依据")
        if cells[4] not in ALLOWED_STATUS:
            errors.append(f"行动项第 {row_number} 行状态不在允许值中：{cells[4]}")

    return errors


def run_self_test() -> int:
    valid = """## 本次结论
- 演示材料需要汇总。
## 风险与影响
- 两项测试尚未返回。
## 行动项
| 事项 | 负责人 | 截止日期 | 原文依据 | 状态 |
|---|---|---|---|---|
| 汇总演示材料 | 李敏 | 本周四前 | 李敏负责汇总 | 未提供 |
| 确认培训日期 | 未提供 | 未提供 | 具体日期尚未确认 | 待确认 |
## 待确认事项
- 培训日期和负责人。
"""
    invalid = """## 本次结论
- 示例。
## 风险与影响
- 示例。
## 行动项
| 事项 | 负责人 | 截止日期 | 原文依据 | 状态 |
|---|---|---|---|---|
| 确认培训日期 | | | 未提供 | 大概进行中 |
## 待确认事项
- 示例。
"""

    valid_errors = validate_markdown(valid)
    invalid_errors = validate_markdown(invalid)
    if valid_errors:
        print("SELF-TEST FAIL: 合格样例被拒绝", file=sys.stderr)
        for error in valid_errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if len(invalid_errors) < 3:
        print("SELF-TEST FAIL: 缺字段样例未触发预期检查", file=sys.stderr)
        for error in invalid_errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"SELF-TEST PASS: 合格样例 0 项错误；缺字段样例捕获 {len(invalid_errors)} 项错误")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查行动项 Markdown 的机械输出合同")
    parser.add_argument("file", nargs="?", type=Path, help="待检查的 Markdown 文件")
    parser.add_argument("--self-test", action="store_true", help="运行内置正常与缺字段样例")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.file is None:
        parser.error("请提供 Markdown 文件，或使用 --self-test")
    if not args.file.is_file():
        print(f"ERROR: 文件不存在：{args.file}", file=sys.stderr)
        return 2

    errors = validate_markdown(args.file.read_text(encoding="utf-8"))
    if errors:
        print(f"FAIL: {len(errors)} 项机械合同错误")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: 行动项 Markdown 满足机械输出合同；业务真实性仍需人工确认")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

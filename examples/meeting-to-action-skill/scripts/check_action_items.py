"""Validate the deterministic Markdown contract for the teaching Skill.

With ``--source``, this script also checks that evidence anchors and explicit
owner/date/status values occur literally in the supplied notes. It still does
not judge whether the summary is complete or business-correct.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = ["本次结论", "风险与影响", "行动项", "待确认事项"]
REQUIRED_HEADER = ["事项", "负责人", "截止日期", "原文依据", "状态"]
ALLOWED_STATUS = {"已完成", "进行中", "未开始", "待确认", "未提供"}
UNKNOWN_VALUES = {"未提供", "待确认"}


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(cells: list[str]) -> bool:
    return len(cells) == len(REQUIRED_HEADER) and all(
        re.fullmatch(r":?-{3,}:?", cell) for cell in cells
    )


def normalize_literal(text: str) -> str:
    text = text.strip().strip("`\"'“”‘’")
    return re.sub(r"\s+", "", text)


def parse_action_rows(text: str) -> list[list[str]]:
    lines = text.splitlines()
    header_index = None
    for index, line in enumerate(lines):
        if line.lstrip().startswith("|") and split_row(line) == REQUIRED_HEADER:
            header_index = index
            break
    if header_index is None:
        return []

    rows: list[list[str]] = []
    for line in lines[header_index + 2 :]:
        if not line.lstrip().startswith("|"):
            if rows:
                break
            continue
        cells = split_row(line)
        if is_separator(cells):
            continue
        rows.append(cells)
    return rows


def validate_markdown(text: str, source_text: str | None = None) -> list[str]:
    errors: list[str] = []
    section_positions: list[int] = []

    for section in REQUIRED_SECTIONS:
        match = re.search(rf"^##\s+{re.escape(section)}\s*$", text, re.MULTILINE)
        if not match:
            errors.append(f"缺少二级标题：{section}")
        else:
            section_positions.append(match.start())

    if len(section_positions) == len(REQUIRED_SECTIONS) and section_positions != sorted(
        section_positions
    ):
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

    if header_index + 1 >= len(lines) or not is_separator(
        split_row(lines[header_index + 1])
    ):
        errors.append("行动项表缺少合法的五列 Markdown 分隔行")

    data_rows = parse_action_rows(text)
    if not data_rows:
        errors.append("行动项表没有数据行")
        return errors

    normalized_source = normalize_literal(source_text or "")
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

        if source_text is None:
            continue
        evidence = normalize_literal(cells[3])
        if evidence and evidence not in normalized_source:
            errors.append(f"行动项第 {row_number} 行的原文依据无法在输入中逐字定位")
        for field_index, field_name in [(1, "负责人"), (2, "截止日期")]:
            value = cells[field_index]
            if value not in UNKNOWN_VALUES and normalize_literal(value) not in normalized_source:
                errors.append(
                    f"行动项第 {row_number} 行{field_name}未在输入中逐字出现：{value}"
                )
        status = cells[4]
        if status not in UNKNOWN_VALUES and normalize_literal(status) not in normalized_source:
            errors.append(f"行动项第 {row_number} 行状态未在输入中明确出现：{status}")

    return errors


def run_self_test() -> int:
    source = """授权状态：已批准用于当前教学演示。
试点演示材料需要在本周四前完成，李敏负责汇总。
"""
    valid = """## 本次结论
- 演示材料需要汇总。
## 风险与影响
- 未提供。
## 行动项
| 事项 | 负责人 | 截止日期 | 原文依据 | 状态 |
|---|---|---|---|---|
| 汇总演示材料 | 李敏 | 本周四前 | 试点演示材料需要在本周四前完成，李敏负责汇总 | 未提供 |
## 待确认事项
- 执行状态。
"""
    invalid = """## 本次结论
- 示例。
## 风险与影响
- 示例。
## 行动项
| 事项 | 负责人 | 截止日期 | 原文依据 | 状态 |
|---|---|---|---|---|
| 汇总演示材料 | | 周五上午会议前 | 不存在的原文 | 大概进行中 |
## 待确认事项
- 示例。
"""
    unsupported = """## 本次结论
- 示例。
## 风险与影响
- 示例。
## 行动项
| 事项 | 负责人 | 截止日期 | 原文依据 | 状态 |
|---|---|---|---|---|
| 汇总演示材料 | 李敏 | 本周四前 | 试点演示材料需要在本周四前完成，李敏负责汇总 | 进行中 |
## 待确认事项
- 示例。
"""

    valid_errors = validate_markdown(valid, source)
    invalid_errors = validate_markdown(invalid, source)
    unsupported_errors = validate_markdown(unsupported, source)
    if valid_errors:
        print("SELF-TEST FAIL: 合格样例被拒绝", file=sys.stderr)
        for error in valid_errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if len(invalid_errors) < 4:
        print("SELF-TEST FAIL: 缺字段样例未触发预期检查", file=sys.stderr)
        for error in invalid_errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if not any("状态未在输入中明确出现" in error for error in unsupported_errors):
        print("SELF-TEST FAIL: 未拦截由模型推断的状态", file=sys.stderr)
        return 1
    print(
        "SELF-TEST PASS: 合格样例 0 项错误；"
        f"缺字段样例捕获 {len(invalid_errors)} 项错误；未明示状态已被拦截"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查行动项 Markdown 的确定性合同")
    parser.add_argument("file", nargs="?", type=Path, help="待检查的 Markdown 文件")
    parser.add_argument("--source", type=Path, help="原始会议记录；提供后执行逐字依据检查")
    parser.add_argument("--self-test", action="store_true", help="运行正常、缺字段和推断状态样例")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.file is None:
        parser.error("请提供 Markdown 文件，或使用 --self-test")
    if not args.file.is_file():
        print(f"ERROR: 文件不存在：{args.file}", file=sys.stderr)
        return 2
    if args.source is not None and not args.source.is_file():
        print(f"ERROR: 原始会议记录不存在：{args.source}", file=sys.stderr)
        return 2

    source_text = args.source.read_text(encoding="utf-8") if args.source else None
    errors = validate_markdown(args.file.read_text(encoding="utf-8"), source_text)
    if errors:
        print(f"FAIL: {len(errors)} 项合同错误")
        for error in errors:
            print(f"- {error}")
        return 1
    scope = "结构与逐字依据" if source_text is not None else "机械结构"
    print(f"PASS: 行动项 Markdown 满足{scope}合同；业务完整性仍需人工确认")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

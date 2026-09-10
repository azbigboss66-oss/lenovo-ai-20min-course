"""Evaluate reference or local-model outputs against the teaching fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = SKILL_ROOT / "evals/cases.json"


def load_checker():
    path = Path(__file__).with_name("check_action_items.py")
    spec = importlib.util.spec_from_file_location("check_action_items", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载合同检查器")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(
    case: dict[str, object], candidate: Path, checker, *, reference_mode: bool
) -> list[str]:
    errors: list[str] = []
    text = candidate.read_text(encoding="utf-8")
    source = (SKILL_ROOT / str(case["input"])).read_text(encoding="utf-8")

    if case["kind"] == "stop":
        expected = str(case["expected_stop"])
        stop_matches = expected in text if reference_mode else text.strip() == expected
        if not stop_matches:
            errors.append("未返回精确授权停止通知")
        if "## 本次结论" in text or "[未提供真实值]" in text:
            errors.append("停止输出包含结构化处理结果或复述了正文占位符")
        return errors

    errors.extend(checker.validate_markdown(text, source))
    rows = checker.parse_action_rows(text)
    expected_rows = int(case["expected_action_rows"])
    if len(rows) != expected_rows:
        errors.append(f"行动项行数应为 {expected_rows}，实际为 {len(rows)}")
    actual_cells = [[row[0], row[1], row[2], row[4]] for row in rows if len(row) == 5]
    expected_cells = case.get("expected_action_cells", [])
    if actual_cells != expected_cells:
        errors.append(
            "行动项关键单元格不匹配："
            f"expected={expected_cells}, actual={actual_cells}"
        )
    for term in case.get("required_terms", []):
        if str(term) not in text:
            errors.append(f"缺少必需信息：{term}")
    for term in case.get("forbidden_terms", []):
        if str(term) in text:
            errors.append(f"出现禁止猜测或裁决：{term}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="评测会议行动项 Skill 的四个教学案例")
    parser.add_argument(
        "--candidate-dir",
        type=Path,
        help="模型输出目录；省略时评测人工参考答案",
    )
    parser.add_argument(
        "--suffix",
        default="skill",
        help="模型输出文件后缀，默认 skill，例如 01-normal-skill.md",
    )
    parser.add_argument("--report", type=Path, help="可选：写入纯文本结果")
    args = parser.parse_args()

    cases = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checker = load_checker()
    lines: list[str] = []
    passed = 0
    for case in cases:
        if args.candidate_dir:
            candidate = args.candidate_dir / f"{case['id']}-{args.suffix}.md"
        else:
            candidate = SKILL_ROOT / str(case["reference"])
        if not candidate.is_file():
            errors = [f"缺少候选文件：{candidate}"]
        else:
            errors = evaluate(
                case, candidate, checker, reference_mode=args.candidate_dir is None
            )
        if errors:
            lines.append(f"FAIL {case['id']}: {'；'.join(errors)}")
        else:
            passed += 1
            lines.append(f"PASS {case['id']}")

    lines.append(f"SUMMARY: {passed}/{len(cases)} cases passed")
    lines.append("LIMIT: 小样本教学断言不证明业务完整性、生产准确率或内部合规。")
    output = "\n".join(lines) + "\n"
    print(output, end="")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Estimate speaker-script duration without claiming a real rehearsal."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DEFAULT_SCRIPT = Path("course/01-speaker-script.md")


def spoken_text(markdown: str) -> str:
    lines: list[str] = []
    in_fence = False
    for raw in markdown.splitlines():
        line = raw.strip()
        if line == "## 讲稿来源":
            break
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if line.startswith("#") or line.startswith(">"):
            continue
        if re.fullmatch(r"\[[^\]]+\]", line):
            continue
        if not line:
            continue
        lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"\[(?:\d+)(?:[-–]\d+)?\]", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"[`*_>|]", "", text)
    return text


def count_units(text: str) -> tuple[int, int, float]:
    cjk = len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))
    english_words = len(re.findall(r"\b[A-Za-z][A-Za-z0-9-]*\b", text))
    equivalent_units = cjk + english_words * 1.6
    return cjk, english_words, equivalent_units


def build_report(script_path: Path) -> str:
    markdown = script_path.read_text(encoding="utf-8")
    text = spoken_text(markdown)
    cjk, english_words, units = count_units(text)
    planned_pause_minutes = 1.4

    estimates = {
        "偏慢语速（210 等效字符/分钟）": units / 210 + planned_pause_minutes,
        "参考语速（230 等效字符/分钟）": units / 230 + planned_pause_minutes,
        "偏快语速（250 等效字符/分钟）": units / 250 + planned_pause_minutes,
    }

    lines = [
        "课程讲稿自动估时",
        f"文件: {script_path.as_posix()}",
        f"可讲文本中文字符: {cjk}",
        f"可讲文本英文词: {english_words}",
        f"等效字符: {units:.1f}",
        f"计划停顿/互动/切页预算: {planned_pause_minutes:.1f} 分钟",
    ]
    lines.extend(f"{label}: {minutes:.1f} 分钟" for label, minutes in estimates.items())
    lines.extend(
        [
            "结论: 自动估时只用于发现明显超时或内容不足，不能替代真实彩排。",
            "验收: 讲师需以实际语速完整彩排，目标为 18–20 分钟，并按讲师指南删减。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="估算中文课程讲稿时长")
    parser.add_argument("--script", type=Path, default=DEFAULT_SCRIPT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.script.is_file():
        parser.error(f"讲稿不存在：{args.script}")
    report = build_report(args.script)
    print(report, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

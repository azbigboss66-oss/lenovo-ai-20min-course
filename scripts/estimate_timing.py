"""Estimate lesson duration without claiming a real rehearsal."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "course-data.json"
DEFAULT_SCRIPT = ROOT / "course/01-speaker-script.md"


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


def build_report(script_path: Path, pause_minutes: float, target_minutes: int | None = None) -> tuple[str, float]:
    markdown = script_path.read_text(encoding="utf-8")
    text = spoken_text(markdown)
    cjk, english_words, units = count_units(text)
    estimates = {
        "偏慢语速（210 等效字符/分钟）": units / 210 + pause_minutes,
        "参考语速（230 等效字符/分钟）": units / 230 + pause_minutes,
        "偏快语速（250 等效字符/分钟）": units / 250 + pause_minutes,
    }
    reference = estimates["参考语速（230 等效字符/分钟）"]
    status = "PASS" if 15 <= reference <= 30 else "WARN"
    lines = [
        "课程讲稿自动估时",
        f"文件: {script_path.relative_to(ROOT).as_posix()}",
        f"可讲文本中文字符: {cjk}",
        f"可讲文本英文词: {english_words}",
        f"等效字符: {units:.1f}",
        f"计划停顿/演示/互动预算: {pause_minutes:.1f} 分钟",
    ]
    if target_minutes is not None:
        lines.append(f"教案计划时长: {target_minutes} 分钟")
    lines.extend(f"{label}: {minutes:.1f} 分钟" for label, minutes in estimates.items())
    lines.extend(
        [
            f"自动范围检查: {status}（参考估时需处于 15–30 分钟）",
            "结论: 自动估时只用于发现明显超时或内容不足，不能替代真实彩排。",
            "人工验收: 讲师需以实际语速完整彩排，并按讲师运行手册调整。",
        ]
    )
    return "\n".join(lines) + "\n", reference


def run_all(output_dir: Path) -> int:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    failures = 0
    summary = ["七节课程自动估时汇总", ""]
    for lesson in data["lessons"]:
        script = ROOT / "lessons" / f"{lesson['id']}-{lesson['slug']}" / "speaker-script.md"
        report, reference = build_report(script, float(lesson["pauseMinutes"]), int(lesson["duration"]))
        (output_dir / f"lesson-{lesson['id']}.txt").write_text(report, encoding="utf-8")
        status = "PASS" if 15 <= reference <= 30 else "WARN"
        failures += status != "PASS"
        summary.append(f"{lesson['id']} | 计划 {lesson['duration']} 分钟 | 参考估时 {reference:.1f} 分钟 | {status}")
    summary.extend(["", "限制: 自动字符估时不等于真人彩排或教学效果测量。"])
    (output_dir / "summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="估算中文课程讲稿时长")
    parser.add_argument("--all", action="store_true", help="估算 course-data.json 中全部七课")
    parser.add_argument("--script", type=Path, default=DEFAULT_SCRIPT)
    parser.add_argument("--pause-minutes", type=float, default=1.4)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "quality/timing")
    args = parser.parse_args()
    if args.all:
        return run_all(args.output_dir)
    script = args.script if args.script.is_absolute() else ROOT / args.script
    if not script.is_file():
        parser.error(f"讲稿不存在：{script}")
    report, _ = build_report(script, args.pause_minutes)
    print(report, end="")
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

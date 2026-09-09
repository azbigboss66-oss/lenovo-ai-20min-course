"""Run deterministic structural checks for the course repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md",
    "course/00-course-outline.md",
    "course/01-speaker-script.md",
    "course/02-slide-outline.md",
    "course/03-instructor-guide.md",
    "course/04-quick-reference.md",
    "examples/prompt-before-after.md",
    "examples/lenovo-workplace-cases.md",
    "examples/meeting-to-action-skill/SKILL.md",
    "examples/meeting-to-action-skill/references/output-contract.md",
    "examples/meeting-to-action-skill/scripts/check_action_items.py",
    "research/research-synthesis.md",
    "research/sources.md",
    "quality/content-checklist.md",
    "quality/self-check-report.md",
    "quality/timing-check.txt",
]


def markdown_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts and "docs" not in path.parts
    ]


def check_local_links(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).split("#", 1)[0]
        if not target or re.match(r"https?://", target):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"断开的本地链接：{path.relative_to(ROOT)} -> {target}")
    return errors


def run_checks() -> list[str]:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"缺少文件：{relative}")

    files = markdown_files()
    combined = "\n".join(path.read_text(encoding="utf-8") for path in files)

    banned_tokens = [r"cite", r"turn\d+(?:search|view|fetch)\d+", r"\bTODO\b", r"\bTBD\b"]
    for pattern in banned_tokens:
        if re.search(pattern, combined, re.IGNORECASE):
            errors.append(f"发现内部引用标记或未完成占位符：{pattern}")

    for relative in ["examples/prompt-before-after.md", "examples/lenovo-workplace-cases.md"]:
        path = ROOT / relative
        if path.is_file() and "教学模拟" not in path.read_text(encoding="utf-8"):
            errors.append(f"案例未标记为教学模拟：{relative}")

    prompt_path = ROOT / "examples/prompt-before-after.md"
    if prompt_path.is_file():
        prompt_text = prompt_path.read_text(encoding="utf-8")
        for field in ["任务目标", "必要上下文", "约束条件", "输出形式", "验收与停止条件"]:
            if f"# {field}" not in prompt_text:
                errors.append(f"完整 Prompt 缺少字段：{field}")

    slide_path = ROOT / "course/02-slide-outline.md"
    if slide_path.is_file():
        slide_count = len(re.findall(r"^## 第 \d+ 页", slide_path.read_text(encoding="utf-8"), re.MULTILINE))
        if slide_count != 11:
            errors.append(f"PPT 页纲应为 11 页，实际为 {slide_count} 页")

    sources_path = ROOT / "research/sources.md"
    if sources_path.is_file():
        source_rows = len(re.findall(r"^\|\s*\d+\s*\|", sources_path.read_text(encoding="utf-8"), re.MULTILINE))
        if source_rows < 20:
            errors.append(f"来源台账少于 20 项，实际为 {source_rows} 项")

    for path in files:
        text = path.read_text(encoding="utf-8")
        is_skill = path.name == "SKILL.md" and text.startswith("---\n")
        if not text.strip().startswith("#") and not is_skill:
            errors.append(f"Markdown 缺少顶层标题：{path.relative_to(ROOT)}")
        errors.extend(check_local_links(path, text))

    return errors


def main() -> int:
    errors = run_checks()
    if errors:
        print(f"FAIL: {len(errors)} 项仓库结构错误")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {len(REQUIRED_FILES)} 个必需文件齐全")
    print("PASS: 教学模拟标记、Prompt 五字段、11 页 PPT 页纲、来源数量和本地链接满足合同")
    print("PASS: 未发现内部引用标记或未完成占位符")
    print("LIMIT: 本检查不证明事实准确、教学效果、真实时长或联想内部合规性")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

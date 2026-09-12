"""Deterministic structural checks for the seven-lesson curriculum and site."""

from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from estimate_timing import build_report


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "course-data.json"
EXPECTED_LOGO_SHA256 = "f7abd014eb99a62db7837e8a0fdc4469306ff360d23ac3af83b6823d6d63b4e8"


class PageAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.h1 = 0
        self.buttons = 0
        self.details = 0
        self.links: list[str] = []
        self.scripts: list[str] = []
        self.styles: list[str] = []
        self.images: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if tag == "button":
            self.buttons += 1
        if tag == "details":
            self.details += 1
        if tag == "a" and values.get("href"):
            self.links.append(str(values["href"]))
        if tag == "script" and values.get("src"):
            self.scripts.append(str(values["src"]))
        if tag == "link" and values.get("href"):
            self.styles.append(str(values["href"]))
        if tag == "img":
            self.images.append((str(values.get("src", "")), str(values.get("alt", ""))))


def local_target(page: Path, target: str) -> Path | None:
    clean = target.split("#", 1)[0]
    if not clean or re.match(r"(?:https?:|mailto:)", clean):
        return None
    return (page.parent / clean).resolve()


def minute_value(minutes: str, seconds: str) -> float:
    return int(minutes) + int(seconds) / 60


def run_checks() -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"课程元数据不可读取：{exc}"]

    lessons = data.get("lessons", [])
    if len(lessons) != 7:
        errors.append(f"课程必须为 7 节，实际为 {len(lessons)} 节")

    ids = [lesson.get("id") for lesson in lessons]
    if ids != [f"{number:02d}" for number in range(1, 8)]:
        errors.append(f"课程编号应为 01–07，实际为 {ids}")

    seen_titles: set[str] = set()
    all_markdown: list[str] = []
    for lesson in lessons:
        lesson_id = str(lesson.get("id", ""))
        title = str(lesson.get("title", ""))
        duration = lesson.get("duration")
        if title in seen_titles:
            errors.append(f"课程标题重复：{title}")
        seen_titles.add(title)
        if not isinstance(duration, int) or not 15 <= duration <= 30:
            errors.append(f"{lesson_id} 计划时长不在 15–30 分钟：{duration}")
        folder = ROOT / "lessons" / f"{lesson_id}-{lesson.get('slug', '')}"
        parts: dict[str, str] = {}
        for name in ["outline.md", "speaker-script.md", "exercise.md", "reference-answer.md"]:
            path = folder / name
            if not path.is_file():
                errors.append(f"{lesson_id} 缺少文件：{path.relative_to(ROOT)}")
                continue
            text = path.read_text(encoding="utf-8")
            parts[name] = text
            all_markdown.append(text)
            if not text.startswith("# "):
                errors.append(f"{path.relative_to(ROOT)} 缺少一级标题")
            if re.search(r"\b(?:TODO|TBD)\b|cite|turn\d+(?:search|view|fetch)\d+", text, re.IGNORECASE):
                errors.append(f"{path.relative_to(ROOT)} 含内部引用或未完成占位符")
        outline = parts.get("outline.md", "")
        exercise = parts.get("exercise.md", "")
        answer = parts.get("reference-answer.md", "")
        script = parts.get("speaker-script.md", "")
        if "教学模拟" not in outline or "教学模拟" not in exercise or "教学模拟" not in answer:
            errors.append(f"{lesson_id} 的提纲/练习/答案未全部标记教学模拟")
        if "## 来源" not in outline or "## 讲稿来源" not in script:
            errors.append(f"{lesson_id} 缺少来源段")
        if "评分标准" not in answer:
            errors.append(f"{lesson_id} 参考答案缺少评分标准")
        minute_sections = re.findall(
            r"^##\s+(\d+):(\d+)–(\d+):(\d+)｜", script, re.MULTILINE
        )
        if len(minute_sections) < 5:
            errors.append(f"{lesson_id} 讲稿分钟段少于 5 段")
        elif isinstance(duration, int):
            spans = [
                (minute_value(start_m, start_s), minute_value(end_m, end_s))
                for start_m, start_s, end_m, end_s in minute_sections
            ]
            if spans[0][0] != 0:
                errors.append(f"{lesson_id} 讲稿时间线没有从 0:00 开始")
            for previous, current in zip(spans, spans[1:]):
                if previous[1] != current[0]:
                    errors.append(
                        f"{lesson_id} 讲稿时间线不连续：{previous[1]:g} -> {current[0]:g} 分钟"
                    )
            if spans[-1][1] != duration:
                errors.append(
                    f"{lesson_id} 讲稿结束时间 {spans[-1][1]:g} 与计划 {duration} 分钟不一致"
                )
        if script and isinstance(duration, int):
            _, estimate = build_report(folder / "speaker-script.md", float(lesson.get("pauseMinutes", 0)), duration)
            if not 15 <= estimate <= 30:
                errors.append(f"{lesson_id} 参考自动估时 {estimate:.1f} 分钟，不在 15–30 分钟")

    combined = "\n".join(all_markdown)
    for term in ["Prompt", "RAG", "Skill", "Agent", "微调", "预训练", "可交付", "可证明", "可追责", "可追踪"]:
        if term not in combined:
            errors.append(f"课程链缺少关键概念：{term}")

    logo = ROOT / "site/assets/brand/lenovo-logo-red-horizontal.webp"
    if not logo.is_file():
        errors.append("缺少 Lenovo 官方 Logo 文件")
    else:
        payload = logo.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != EXPECTED_LOGO_SHA256:
            errors.append(f"Lenovo Logo 哈希与来源台账不一致：{digest}")
        if not payload.startswith(b"RIFF"):
            errors.append("Lenovo Logo 文件不是预期 WebP 容器")

    pages = [ROOT / "site/index.html"] + [ROOT / f"site/lessons/{number:02d}.html" for number in range(1, 8)]
    for page in pages:
        if not page.is_file():
            errors.append(f"缺少生成页面：{page.relative_to(ROOT)}")
            continue
        text = page.read_text(encoding="utf-8")
        audit = PageAudit()
        audit.feed(text)
        if audit.h1 != 1:
            errors.append(f"HTML 应只有 1 个 h1：{page.relative_to(ROOT)}，实际为 {audit.h1}")
        if not any(src.endswith("lenovo-logo-red-horizontal.webp") and alt == "Lenovo" for src, alt in audit.images):
            errors.append(f"HTML 缺少带替代文本的官方 Logo：{page.relative_to(ROOT)}")
        for target in audit.links + audit.scripts + audit.styles + [src for src, _ in audit.images]:
            resolved = local_target(page, target)
            if resolved is not None and not resolved.exists():
                errors.append(f"HTML 本地链接断开：{page.relative_to(ROOT)} -> {target}")
        if page.name != "index.html" and (audit.buttons < 3 or audit.details < 1):
            errors.append(f"课程页缺少复制/讲师/进度或答案交互：{page.relative_to(ROOT)}")

    sources = (ROOT / "research/sources.md").read_text(encoding="utf-8")
    source_ids = [
        int(value) for value in re.findall(r"^\|\s*(\d+)\s*\|", sources, re.MULTILINE)
    ]
    source_count = len(source_ids)
    if source_count < 42:
        errors.append(f"来源台账少于 42 项，实际为 {source_count}")
    if source_ids != list(range(1, source_count + 1)):
        errors.append("来源台账编号不连续或顺序错误")
    used_source_ids = {int(value) for value in re.findall(r"\[(\d+)\]", combined)}
    unknown_source_ids = sorted(used_source_ids - set(source_ids))
    if unknown_source_ids:
        errors.append(f"课程引用了台账中不存在的编号：{unknown_source_ids}")
    for benchmark in ["Google AI Essentials", "Generative AI for Beginners", "OpenAI Academy", "IBM SkillsBuild", "AI literacy", "Lenovo Brand World"]:
        if benchmark not in sources:
            errors.append(f"来源台账缺少对标：{benchmark}")

    return errors


def main() -> int:
    errors = run_checks()
    if errors:
        print(f"FAIL: {len(errors)} 项 V2 课程错误")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: 7 节课程及 28 份提纲/讲稿/练习/答案文件齐全")
    print("PASS: 七课计划与参考估时均位于 15–30 分钟")
    print("PASS: 8 个 HTML 页面、官方 Logo、本地链接和课程交互满足结构合同")
    print("PASS: 教学模拟、来源、评分和核心术语边界齐全")
    print("LIMIT: 自动检查不证明真人授课时长、教学效果、内部审批或生产能力")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Build the offline static course site from Markdown sources."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = json.loads((ROOT / "course-data.json").read_text(encoding="utf-8"))


def inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+|[^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        escaped,
    )
    return escaped


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def markdown_to_html(markdown: str, heading_offset: int = 0) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    list_type: str | None = None
    in_code = False
    code_lines: list[str] = []
    i = 0

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if line.startswith("```"):
            flush_paragraph()
            close_list()
            if in_code:
                out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(raw)
            i += 1
            continue
        if not line:
            flush_paragraph()
            close_list()
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            flush_paragraph()
            close_list()
            headers = [cell.strip() for cell in line.strip("|").split("|")]
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([cell.strip() for cell in lines[i].strip().strip("|").split("|")])
                i += 1
            head = "".join(f"<th>{inline(cell)}</th>" for cell in headers)
            body = "".join(
                "<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>"
                for row in rows
            )
            out.append(f"<div class=\"table-wrap\"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>")
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            close_list()
            level = min(6, len(heading.group(1)) + heading_offset)
            title = heading.group(2)
            anchor = re.sub(r"[^a-zA-Z0-9\u3400-\u9fff]+", "-", title).strip("-")
            out.append(f'<h{level} id="{html.escape(anchor)}">{inline(title)}</h{level}>')
            i += 1
            continue
        if line.startswith(">"):
            flush_paragraph()
            close_list()
            out.append(f"<blockquote>{inline(line.lstrip('> ').strip())}</blockquote>")
            i += 1
            continue
        unordered = re.match(r"^[-*]\s+(.+)$", line)
        ordered = re.match(r"^\d+[.)]\s+(.+)$", line)
        if unordered or ordered:
            flush_paragraph()
            wanted = "ul" if unordered else "ol"
            if list_type != wanted:
                close_list()
                list_type = wanted
                out.append(f"<{wanted}>")
            item = (unordered or ordered).group(1)
            out.append(f"<li>{inline(item)}</li>")
            i += 1
            continue
        paragraph.append(line)
        i += 1

    flush_paragraph()
    close_list()
    if in_code:
        out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    return "\n".join(out)


def lesson_dir(lesson: dict) -> Path:
    return ROOT / "lessons" / f"{lesson['id']}-{lesson['slug']}"


def read_part(lesson: dict, name: str) -> str:
    return (lesson_dir(lesson) / name).read_text(encoding="utf-8")


def timeline(script: str) -> str:
    items = []
    for start, _end, title in re.findall(r"^##\s+(\d+:\d+)–(\d+:\d+)｜(.+)$", script, re.MULTILINE):
        items.append(f'<li><time>{start}</time><span>{html.escape(title)}</span></li>')
    return "<ol class=\"timeline\">" + "".join(items) + "</ol>"


def nav(current: str | None = None, prefix: str = "") -> str:
    links = []
    for lesson in DATA["lessons"]:
        active = ' aria-current="page" class="active"' if lesson["id"] == current else ""
        links.append(
            f'<a href="{prefix}lessons/{lesson["id"]}.html"{active}>'
            f'<span>{lesson["id"]}</span>{html.escape(lesson["shortTitle"])}</a>'
        )
    return "".join(links)


def document(title: str, body: str, asset_prefix: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="联想场景特化的 AI 工作方法系列课，全部案例为教学模拟。">
  <title>{html.escape(title)}｜AI 工作新方法</title>
  <link rel="stylesheet" href="{asset_prefix}assets/styles.css">
</head>
<body>
  <a class="skip-link" href="#main">跳到正文</a>
  {body}
  <script src="{asset_prefix}assets/app.js" defer></script>
</body>
</html>
"""


def header(prefix: str) -> str:
    return f"""<header class="topbar">
  <a class="course-brand" href="{prefix}index.html">AI 工作新方法</a>
  <nav aria-label="全局导航">
    <a href="{prefix}index.html#positions">课程立场</a>
    <a href="{prefix}index.html#course-map">课程总览</a>
    <a href="{prefix}index.html#instructor">讲师指南</a>
  </nav>
  <img class="lenovo-logo" src="{prefix}assets/brand/lenovo-logo-red-horizontal.webp" width="120" height="40" alt="Lenovo">
</header>"""


def footer() -> str:
    return """<footer class="site-footer">
  <strong>AI 工作新方法</strong>
  <p>内部教学候选材料。全部案例为教学模拟；使用前需按当前联想内部工具、数据、品牌与审批要求复核。</p>
  <p>LENOVO is a trademark of Lenovo. All other trademarks are the property of their respective owners. © 2026</p>
</footer>"""


def build_home() -> None:
    lesson_rows = []
    for lesson in DATA["lessons"]:
        lesson_rows.append(f"""<a class="course-row" href="lessons/{lesson['id']}.html">
  <span class="course-no">{lesson['id']}</span>
  <span><strong>{html.escape(lesson['shortTitle'])}</strong><small>{html.escape(lesson['summary'])}</small></span>
  <span class="course-meta">{lesson['duration']} 分钟<br>{html.escape(lesson['deliverable'])}</span>
  <svg aria-hidden="true" viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"/></svg>
</a>""")
    position_cards = "".join(
        f"<article><b>{index:02d}</b><p>{html.escape(position)}</p></article>"
        for index, position in enumerate(DATA["positions"], start=1)
    )
    body = header("") + f"""
<main id="main">
  <section class="hero">
    <div>
      <h1>{html.escape(DATA['programTitle'])}</h1>
      <p class="hero-subtitle">{html.escape(DATA['programSubtitle'])}</p>
      <p class="hero-copy">{html.escape(DATA['programThesis'])}</p>
      <div class="hero-actions"><a class="button primary" href="lessons/01.html">开始第一课</a><a class="button secondary" href="#course-map">查看课程地图</a></div>
    </div>
    <div class="workflow" aria-label="AI 工作流程">
      <h2>从问题到价值的 AI 工作流程</h2>
      <ol><li><b>01</b><span>定义问题<br>明确目标</span></li><li><b>02</b><span>获得信息<br>给出上下文</span></li><li><b>03</b><span>生成方案<br>受控执行</span></li><li><b>04</b><span>验证结果<br>持续改进</span></li><li><b>05</b><span>沉淀能力<br>创造价值</span></li></ol>
    </div>
  </section>
  <section class="positions" id="positions"><div class="section-heading"><h2>五个讲师判断</h2><p>资料负责校准事实，取舍才体现专业。以下观点贯穿七课，也欢迎学员用工作反例挑战。</p></div><div class="position-grid">{position_cards}</div><p class="position-note">完整论证与台上表达见仓库 <code>curriculum/course-thesis.md</code>。详细讲稿是论证支架，不是必须逐字照念的台词。</p></section>
  <section class="course-map" id="course-map"><div class="section-heading"><h2>七课进阶：从会用到会设计</h2><p>总计划约 180 分钟，每课完成一个可观察产出。</p></div>{''.join(lesson_rows)}</section>
  <section class="method" id="method"><h2>不是听完，而是每节带走一份成果</h2><div class="method-flow"><span>问题切入</span><span>核心模型</span><span>对比示范</span><span>动手练习</span><span>评分迁移</span></div><p>{html.escape(DATA['scope'])}</p></section>
  <section class="principles"><h2>四个原则，让 AI 真正服务于工作</h2><div><article><strong>可交付</strong><p>结果能进入工作，而不是停在漂亮文字。</p></article><article><strong>可证明</strong><p>关键事实有来源，结论可核验。</p></article><article><strong>可追责</strong><p>授权、复核和业务责任明确。</p></article><article><strong>可追踪</strong><p>输入、版本、调用和修改可回溯。</p></article></div></section>
  <section class="instructor" id="instructor"><h2>讲师怎样使用这套教材</h2><p>普通模式展示精简课件与练习；每个单课页打开“讲师模式”后显示逐分钟详细讲稿。正式授课前必须真人彩排。完整讲师运行手册保存在仓库的 <code>curriculum/instructor-runbook.md</code>。</p></section>
</main>{footer()}"""
    (SITE / "index.html").write_text(document("课程总览", body, ""), encoding="utf-8")


def build_lesson(lesson: dict, index: int) -> None:
    outline = read_part(lesson, "outline.md")
    exercise = read_part(lesson, "exercise.md")
    answer = read_part(lesson, "reference-answer.md")
    script = read_part(lesson, "speaker-script.md")
    previous_link = "../index.html" if index == 0 else f"{DATA['lessons'][index - 1]['id']}.html"
    next_link = "../index.html" if index == len(DATA["lessons"]) - 1 else f"{DATA['lessons'][index + 1]['id']}.html"
    body = header("../") + f"""
<div class="lesson-shell" data-lesson="{lesson['id']}">
  <aside class="lesson-rail" aria-label="课程目录"><div class="rail-title">联想内部 AI 课程<small>从认知到实践</small></div><nav>{nav(lesson['id'], '../')}</nav><div class="progress-block"><span>学习进度</span><progress value="{index + 1}" max="{len(DATA['lessons'])}">{index + 1}/{len(DATA['lessons'])}</progress><small>{index + 1} / {len(DATA['lessons'])}</small></div></aside>
  <main id="main" class="lesson-main">
    <div class="lesson-toolbar"><span>{lesson['duration']} 分钟 · 含练习</span><div><button type="button" class="toolbar-button" data-action="copy-page">复制本课提纲</button><button type="button" class="toolbar-button" data-action="toggle-instructor" aria-pressed="false">讲师模式</button></div></div>
    <article class="lesson-content" id="lesson-outline">{markdown_to_html(outline)}</article>
    <section class="exercise-panel"><div class="section-label">动手练习</div>{markdown_to_html(exercise, heading_offset=1)}<details><summary>显示参考答案</summary><div class="answer-content">{markdown_to_html(answer, heading_offset=1)}</div></details></section>
    <section class="speaker-panel" aria-label="详细讲稿"><div class="section-label">讲师专用</div>{markdown_to_html(script, heading_offset=1)}</section>
    <div class="lesson-actions"><button type="button" class="button secondary" data-action="complete">标记本课完成</button><nav aria-label="课间导航"><a class="button secondary" href="{previous_link}">上一课</a><a class="button primary" href="{next_link}">下一课</a></nav></div>
  </main>
  <aside class="lesson-timeline"><h2>教学时间线</h2>{timeline(script)}</aside>
</div>{footer()}"""
    (SITE / "lessons" / f"{lesson['id']}.html").write_text(
        document(lesson["title"], body, "../"), encoding="utf-8"
    )


def main() -> int:
    (SITE / "lessons").mkdir(parents=True, exist_ok=True)
    build_home()
    for index, lesson in enumerate(DATA["lessons"]):
        build_lesson(lesson, index)
    print(f"BUILT: 1 个总览页 + {len(DATA['lessons'])} 个课程页 -> {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

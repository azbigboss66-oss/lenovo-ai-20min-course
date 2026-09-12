"""Run deterministic structural checks for the course repository."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from check_curriculum import run_checks as run_curriculum_checks


ROOT = Path(__file__).resolve().parents[1]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


REQUIRED_FILES = [
    "README.md",
    "curriculum/course-thesis.md",
    "curriculum/program-map.md",
    "curriculum/instructor-runbook.md",
    "curriculum/glossary.md",
    "examples/prompt-before-after.md",
    "examples/lenovo-workplace-cases.md",
    "examples/meeting-to-action-skill/SKILL.md",
    "examples/meeting-to-action-skill/references/output-contract.md",
    "examples/meeting-to-action-skill/scripts/check_action_items.py",
    "examples/meeting-to-action-skill/scripts/evaluate_cases.py",
    "examples/meeting-to-action-skill/scripts/run_ollama_demo.py",
    "examples/meeting-to-action-skill/evals/cases.json",
    "examples/meeting-to-action-skill/evals/evaluation-rubric.md",
    "examples/meeting-to-action-skill/evals/evaluation-results.md",
    "examples/meeting-to-action-skill/examples/01-normal-input.md",
    "examples/meeting-to-action-skill/examples/01-normal-reference.md",
    "examples/meeting-to-action-skill/examples/02-missing-fields-input.md",
    "examples/meeting-to-action-skill/examples/02-missing-fields-reference.md",
    "examples/meeting-to-action-skill/examples/03-conflict-input.md",
    "examples/meeting-to-action-skill/examples/03-conflict-reference.md",
    "examples/meeting-to-action-skill/examples/04-authorization-uncertain-input.md",
    "examples/meeting-to-action-skill/examples/04-authorization-uncertain-reference.md",
    "quality/skill-reference-eval.txt",
    "quality/skill-local-model-eval.txt",
    "quality/baseline-local-model-eval.txt",
    "research/research-synthesis.md",
    "research/sources.md",
    "quality/content-checklist.md",
    "quality/self-check-report.md",
]

FORBIDDEN_RETIRED_FILES = [
    "course/00-course-outline.md",
    "course/01-speaker-script.md",
    "course/02-slide-outline.md",
    "course/03-instructor-guide.md",
    "course/04-quick-reference.md",
    "docs/superpowers/plans/2026-09-09-lenovo-ai-20min-course.md",
    "docs/superpowers/specs/2026-09-09-lenovo-ai-20min-course-design.md",
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

    for relative in FORBIDDEN_RETIRED_FILES:
        if (ROOT / relative).exists():
            errors.append(f"已退役的原单课材料仍然存在：{relative}")

    v2_evidence_files = [
        "course-data.json",
        "curriculum/program-map.md",
        "curriculum/instructor-runbook.md",
        "curriculum/glossary.md",
        "site/assets/brand/README.md",
        "quality/site-qa.md",
        "quality/fidelity-ledger.md",
        "quality/screenshots/home-desktop.png",
        "quality/screenshots/home-mobile.png",
        "quality/screenshots/home-positions-mobile.png",
        "quality/screenshots/lesson-04-desktop.png",
        "quality/screenshots/lesson-04-mobile.png",
        "docs/design/course-home-concept.png",
        "docs/design/lesson-page-concept.png",
    ]
    for relative in v2_evidence_files:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"缺少 V2 证据文件：{relative}")
        elif path.suffix.lower() == ".png" and not path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
            errors.append(f"视觉证据不是有效 PNG 文件：{relative}")

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

    skill_root = ROOT / "examples/meeting-to-action-skill"
    case_manifest = skill_root / "evals/cases.json"
    if case_manifest.is_file():
        try:
            cases = json.loads(case_manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Skill 评测清单不是合法 JSON：{exc}")
            cases = []
        if len(cases) != 4:
            errors.append(f"Skill 教学评测应有 4 个案例，实际为 {len(cases)} 个")
        for case in cases:
            for key in ["input", "reference", "kind"]:
                if key not in case:
                    errors.append(f"Skill 评测案例缺少字段：{case.get('id', 'unknown')} -> {key}")

    run_root = skill_root / "evals/runs/2026-09-10-qwen38-q3km"
    traces = list(run_root.glob("*.trace.json")) if run_root.is_dir() else []
    if len(traces) != 8:
        errors.append(f"本地对照应保留 8 个追踪文件，实际为 {len(traces)} 个")
    for trace_path in traces:
        try:
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"追踪文件不是合法 JSON：{trace_path.relative_to(ROOT)} -> {exc}")
            continue
        if trace.get("teaching_scope") != "local_classroom_simulation_not_production":
            errors.append(f"追踪文件缺少教学证据边界：{trace_path.relative_to(ROOT)}")
        if not trace.get("output_sha256"):
            errors.append(f"追踪文件缺少输出哈希：{trace_path.relative_to(ROOT)}")
            continue
        output_path = trace_path.with_name(trace_path.name.replace(".trace.json", ".md"))
        if not output_path.is_file():
            errors.append(f"追踪文件缺少对应模型输出：{output_path.relative_to(ROOT)}")
        elif sha256_text(output_path.read_text(encoding="utf-8").rstrip("\n")) != trace["output_sha256"]:
            errors.append(f"模型输出哈希与追踪不一致：{output_path.relative_to(ROOT)}")

        input_path = ROOT / str(trace.get("input_file", ""))
        if not input_path.is_file():
            errors.append(f"追踪文件缺少对应输入：{trace_path.relative_to(ROOT)}")
        elif sha256_text(input_path.read_text(encoding="utf-8")) != trace.get("input_sha256"):
            errors.append(f"输入哈希与追踪不一致：{trace_path.relative_to(ROOT)}")

        if trace.get("mode") == "skill" and not trace.get("stopped_before_model"):
            current_skill_hash = sha256_text((skill_root / "SKILL.md").read_text(encoding="utf-8"))
            current_contract_hash = sha256_text(
                (skill_root / "references/output-contract.md").read_text(encoding="utf-8")
            )
            if trace.get("skill_sha256") != current_skill_hash:
                errors.append(f"Skill 哈希已过期：{trace_path.relative_to(ROOT)}")
            if trace.get("contract_sha256") != current_contract_hash:
                errors.append(f"输出合同哈希已过期：{trace_path.relative_to(ROOT)}")

    expected_eval_summaries = {
        "quality/skill-reference-eval.txt": "SUMMARY: 4/4 cases passed",
        "quality/skill-local-model-eval.txt": "SUMMARY: 4/4 cases passed",
        "quality/baseline-local-model-eval.txt": "SUMMARY: 1/4 cases passed",
    }
    for relative, expected in expected_eval_summaries.items():
        path = ROOT / relative
        if path.is_file() and expected not in path.read_text(encoding="utf-8"):
            errors.append(f"评测摘要与预期不一致：{relative} -> {expected}")

    sources_path = ROOT / "research/sources.md"
    if sources_path.is_file():
        source_rows = len(re.findall(r"^\|\s*\d+\s*\|", sources_path.read_text(encoding="utf-8"), re.MULTILINE))
        if source_rows < 20:
            errors.append(f"来源台账少于 20 项，实际为 {source_rows} 项")

    for path in files:
        text = path.read_text(encoding="utf-8")
        is_skill = path.name == "SKILL.md" and text.startswith("---\n")
        is_raw_model_output = "evals" in path.parts and "runs" in path.parts
        if not text.strip().startswith("#") and not is_skill and not is_raw_model_output:
            errors.append(f"Markdown 缺少顶层标题：{path.relative_to(ROOT)}")
        errors.extend(check_local_links(path, text))

    errors.extend(run_curriculum_checks())

    return errors


def main() -> int:
    errors = run_checks()
    if errors:
        print(f"FAIL: {len(errors)} 项仓库结构错误")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: 七课唯一教材的 {len(REQUIRED_FILES)} 个仓库支持文件齐全，原单课材料无残留")
    print("PASS: 教学模拟标记、Prompt 五字段、来源数量和本地链接满足合同")
    print("PASS: 4 个配对案例与 8 个本地对照追踪文件满足证据结构和哈希一致性")
    print("PASS: 未发现内部引用标记或未完成占位符")
    print("LIMIT: 本检查不证明事实准确、教学效果、真实时长或联想内部合规性")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Run the teaching Skill against a local Ollama model and save an audit trace.

This runner is intentionally local and read-only with respect to business systems.
It never sends notes to the model when the authorization gate is not approved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
STOP_NOTICE = "未处理：当前材料的使用授权尚未确认。请提供获准的教学模拟或脱敏版本后再继续。"
APPROVED_MARKER = "授权状态：已批准用于当前教学演示。"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def strip_private_reasoning(text: str) -> str:
    """Remove optional model reasoning blocks from the classroom artifact."""
    return re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL).strip()


def build_prompt(mode: str, notes: str) -> tuple[str, dict[str, str]]:
    if mode == "baseline":
        prompt = (
            "请把下面会议记录整理成一页周报和行动项。直接给出结果，不要解释过程。\n\n"
            f"<meeting_notes>\n{notes}\n</meeting_notes>"
        )
        return prompt, {}

    skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    contract_text = (SKILL_ROOT / "references/output-contract.md").read_text(
        encoding="utf-8"
    )
    prompt = f"""你正在执行一个课堂候选 Skill。严格遵守以下 Skill 和输出合同。
只处理 meeting_notes 中的事实，不使用常识补充，不把建议自动变成行动项。
输出必须直接从“## 本次结论”开始，不要代码围栏，不要解释推理过程。

<skill>
{skill_text}
</skill>

<output_contract>
{contract_text}
</output_contract>

<meeting_notes>
{notes}
</meeting_notes>
"""
    return prompt, {
        "skill_sha256": sha256_text(skill_text),
        "contract_sha256": sha256_text(contract_text),
    }


def run_model(model: str, prompt: str, endpoint: str) -> dict[str, object]:
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "seed": 42, "num_ctx": 8192},
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise SystemExit(f"ERROR: 无法调用本地 Ollama：{exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="运行本地 Ollama 教学对照并保存追踪信息")
    parser.add_argument("--input", required=True, type=Path, help="会议记录 Markdown")
    parser.add_argument("--output", required=True, type=Path, help="模型输出 Markdown")
    parser.add_argument("--trace", required=True, type=Path, help="追踪 JSON")
    parser.add_argument("--mode", choices=["baseline", "skill"], required=True)
    parser.add_argument("--model", default="qwen38-q3km:latest")
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434/api/generate")
    args = parser.parse_args()

    notes = args.input.read_text(encoding="utf-8")
    started = time.perf_counter()
    trace: dict[str, object] = {
        "schema_version": "1.0",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "teaching_scope": "local_classroom_simulation_not_production",
        "model": args.model,
        "mode": args.mode,
        "input_file": args.input.as_posix(),
        "input_sha256": sha256_text(notes),
        "temperature": 0,
        "seed": 42,
    }

    if APPROVED_MARKER not in notes:
        result_text = STOP_NOTICE
        trace.update(
            {
                "stopped_before_model": True,
                "stop_reason": "authorization_not_approved",
                "elapsed_ms": round((time.perf_counter() - started) * 1000),
            }
        )
    else:
        prompt, component_hashes = build_prompt(args.mode, notes)
        response = run_model(args.model, prompt, args.endpoint)
        result_text = strip_private_reasoning(str(response.get("response", "")))
        trace.update(component_hashes)
        trace.update(
            {
                "prompt_sha256": sha256_text(prompt),
                "stopped_before_model": False,
                "done": response.get("done"),
                "done_reason": response.get("done_reason"),
                "total_duration_ns": response.get("total_duration"),
                "load_duration_ns": response.get("load_duration"),
                "prompt_eval_count": response.get("prompt_eval_count"),
                "eval_count": response.get("eval_count"),
                "elapsed_ms": round((time.perf_counter() - started) * 1000),
            }
        )

    trace["output_sha256"] = sha256_text(result_text)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.trace.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result_text.rstrip() + "\n", encoding="utf-8")
    args.trace.write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: 已保存 {args.mode} 输出与追踪；stopped_before_model={trace['stopped_before_model']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

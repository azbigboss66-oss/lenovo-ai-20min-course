---
name: meeting-to-action-skill
description: Use when approved meeting notes must become traceable action items and missing owners, dates, or statuses must stay explicit.
---

# Meeting to Action

## Outcome

Turn meeting notes into a concise summary, risks, action items, and confirmation questions. Every action must retain a source anchor. Unknown facts remain `未提供`.

This repository contains a teaching example. Its presence does not grant access to Lenovo data, systems, or tools.

Teaching package version: `0.2.0-classroom-candidate`. This version is designed for a reproducible classroom demonstration, not production deployment.

## Input Gate

Require non-empty meeting notes. The person providing them must confirm that the material is approved for the current AI environment or provide a redacted version. If authorization is uncertain, stop before interpreting or repeating the meeting content. Return only the stop notice defined in [the output contract](references/output-contract.md).

## Workflow

1. Read [the output contract](references/output-contract.md).
2. Identify explicit decisions, risks, requests, commitments, owners, dates, and status statements.
3. Keep facts separate from proposals and unresolved questions. Do not turn a useful follow-up idea into an action item unless the notes contain an explicit request or commitment.
4. Create the four contracted sections. For each action row, copy one short, continuous source sentence as its anchor; do not join separate sentences into a new quotation. Do not invent names, dates, states, customer identities, actions, or causal conclusions.
5. Use `未提供` for a missing owner, date, or status. If an action sentence explicitly contains a time expression, use it as `截止日期` even when another later milestone is missing: for example, `王宁今天更新样机清单；最终提交时间未写` means the update action date is `今天`, while the final submission time remains a confirmation question. Copy the complete expression, including qualifiers such as `前`、`后`、`左右`; do not shorten `本周四前` to `本周四`. Preserve relative dates exactly as written unless the notes provide a reference date and the user requests conversion.
6. Put conflicting or execution-blocking gaps in `待确认事项`. When the notes say that a proposed change has no final conclusion, set every disputed action field and its status to `待确认`; list every competing value in `待确认事项` without choosing one.
7. If a Markdown output file is available, run `python scripts/check_action_items.py <file> --source <meeting-notes-file>`. Repair structural or literal-evidence failures; semantic truth still requires a human reviewer.
8. For classroom evaluation, use the four paired cases under `examples/` and the rubric under `evals/`. Do not infer general accuracy from these small teaching fixtures.

## Stop Conditions

- Notes are empty or unreadable.
- The requested output requires facts outside the supplied or explicitly authorized sources.
- The material appears to contain data not approved for the current environment.
- Conflicts prevent a responsible summary. Return the conflicts and request a human decision.

For uncertain authorization, return exactly: `未处理：当前材料的使用授权尚未确认。请提供获准的教学模拟或脱敏版本后再继续。`

## Completion

Return the result plus a one-line review notice: `请由会议参与者确认事实、责任人、日期和对外表述后再使用。`

Do not claim that validation proves business accuracy or production readiness.

## Demonstration Evidence

- `examples/01-normal-*`: ordinary source-grounded extraction.
- `examples/02-missing-fields-*`: unknown owner, date, and status remain explicit.
- `examples/03-conflict-*`: conflicting responsibility and dates are not silently resolved.
- `examples/04-authorization-uncertain-*`: processing stops before content use.
- `evals/evaluation-results.md`: records the tested model, hashes, assertions, and known limits.

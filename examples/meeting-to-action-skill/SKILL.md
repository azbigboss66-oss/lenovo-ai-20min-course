---
name: meeting-to-action-skill
description: Use when approved meeting notes must become traceable action items and missing owners, dates, or statuses must stay explicit.
---

# Meeting to Action

## Outcome

Turn meeting notes into a concise summary, risks, action items, and confirmation questions. Every action must retain a source anchor. Unknown facts remain `未提供`.

This repository contains a teaching example. Its presence does not grant access to Lenovo data, systems, or tools.

## Input Gate

Require non-empty meeting notes. The person providing them must confirm that the material is approved for the current AI environment or provide a redacted version. If authorization is uncertain, stop before processing.

## Workflow

1. Read [the output contract](references/output-contract.md).
2. Identify explicit decisions, risks, requests, commitments, owners, dates, and status statements.
3. Keep facts separate from proposals and unresolved questions.
4. Create the four contracted sections. Copy short source anchors; do not invent names, dates, states, customer identities, or causal conclusions.
5. Use `未提供` for a missing owner, date, or status. Preserve relative dates exactly as written unless the notes provide a reference date and the user requests conversion.
6. Put conflicting or execution-blocking gaps in `待确认事项`.
7. If a Markdown output file is available, run `python scripts/check_action_items.py <file>` and repair mechanical contract failures. Semantic truth still requires a human reviewer.

## Stop Conditions

- Notes are empty or unreadable.
- The requested output requires facts outside the supplied or explicitly authorized sources.
- The material appears to contain data not approved for the current environment.
- Conflicts prevent a responsible summary. Return the conflicts and request a human decision.

## Completion

Return the result plus a one-line review notice: `请由会议参与者确认事实、责任人、日期和对外表述后再使用。`

Do not claim that validation proves business accuracy or production readiness.

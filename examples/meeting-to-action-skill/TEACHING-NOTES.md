# 课堂演示说明

## 这是什么

这是 `meeting-to-action-skill` 的可复现课堂候选包，用来展示 Skill 比长 Prompt 多出的触发、输入门禁、参考合同、确定性脚本、停止条件、版本与评测。全部输入均为教学模拟。

## 这不是什么

- 不是已部署到联想生产环境的能力；
- 不具备真实会议、工单、邮件或任务系统权限；
- 四个案例不代表真实业务分布；
- `1/4 → 4/4` 不是生产准确率，也不是跨模型结论；
- 机械检查通过不等于业务事实正确。

## 建议演示顺序

1. 打开 `SKILL.md`，只看描述和输入门禁，解释“发现与触发”。
2. 打开 `references/output-contract.md`，解释稳定字段、未知和原文证据。
3. 对比 `examples/02-missing-fields-input.md` 与参考答案，说明“不猜”是能力。
4. 对比 `examples/04-authorization-uncertain-input.md`，说明未授权输入在模型前停止。
5. 展示 `evals/evaluation-results.md` 中的基线与 Skill 小样本结果，同时读出限制。

## 可复现检查

```powershell
python -X utf8 scripts/check_action_items.py --self-test
python -X utf8 scripts/evaluate_cases.py
python -X utf8 scripts/evaluate_cases.py --candidate-dir evals/runs/2026-09-10-qwen38-q3km --suffix skill
```

请从本 Skill 目录运行以上命令。输出合同或 `SKILL.md` 发生实质修改后，旧 Trace 中的哈希不再能证明新版本；应建立新评测运行，而不是覆盖旧证据。

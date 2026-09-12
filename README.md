# AI 工作新方法｜联想场景化七课课程链

一套面向工作经验丰富、但刚接触生成式 AI 的联想同事的中文课程仓库。课程由 7 节 15–30 分钟短课组成，以“判断 → 委托 → 求证 → 固化 → 编排 → 评测 → 落地”逐步建立 AI 工作能力。

> 使用边界：仓库中的项目、人物、客户、产品、会议和流程均为教学模拟，不代表联想真实项目、内部制度或已部署能力。正式授课和业务使用必须遵循当时有效的联想工具、数据、保密、品牌和审批要求。

## 最快使用方式

1. 打开 [`site/index.html`](site/index.html)，进入可离线使用的 HTML 教材；
2. 讲师先读 [`curriculum/course-thesis.md`](curriculum/course-thesis.md)、[`curriculum/program-map.md`](curriculum/program-map.md) 和 [`curriculum/instructor-runbook.md`](curriculum/instructor-runbook.md)；
3. 每课目录中的 `outline.md` 用于屏幕内容，`speaker-script.md` 是逐分钟讲稿，`exercise.md` 与 `reference-answer.md` 配套使用；
4. HTML 课页点击“讲师模式”可显示完整讲稿，参考答案默认折叠。

## 七课课程地图

| 课次 | 课程 | 计划时长 | 联想工作模拟 | 学员产出 |
|---|---|---:|---|---|
| 01 | AI 从零开始：先判断，再使用 | 20 分钟 | 跨部门会议记录整理 | AI 适用性判断卡 |
| 02 | Prompt：把要求写成工作合同 | 25 分钟 | 模糊周报请求改写 | 五字段 Prompt 合同 |
| 03 | 证据、数据与 RAG | 25 分钟 | 产品资料与版本核验 | 答案证据表 |
| 04 | Skill：把一次好结果变成工作能力 | 27 分钟 | 会议记录转行动项 | Skill 候选包 |
| 05 | 工具、工作流与 Agent | 25 分钟 | 工单与日志只读调查 | 权限与人工审批图 |
| 06 | 评测与模型升级路线 | 28 分钟 | 冻结案例对照评测 | 技术选择矩阵 |
| 07 | 联想场景综合实战 | 30 分钟 | 从会议输入到受控试点 | 经审计工作流与 30 天行动 |

计划课时合计约 180 分钟，适合按周或集中学习。自动估时按讲稿正文、固定停顿和练习预算计算，七课参考值为 15.4–17.9 分钟，是核心讲授的最低可讲范围；计划课时还预留现场演示、学员汇报和扩展讨论。两者都不能替代讲师真实彩排。

## 课程自己的判断

这不是一份外部课程内容的拼接，也不是 AI 工具功能清单。课程用公开一手资料校准事实，但在教学上坚持五个可讨论、可反驳的判断：

1. 先判断工作，再认识模型；
2. Prompt 是最小工作合同；
3. 企业真正稀缺的是求证；
4. 每增加一分自主，都要增加一分控制；
5. 没有失败证据，不讨论模型升级。

完整论证、台上表达和讲师个人化方法见 [`curriculum/course-thesis.md`](curriculum/course-thesis.md)。详细讲稿提供的是论证支架；讲师应保留逻辑与证据，用自己自然的语言完成最终表达。

## 内容与案例怎样配套

每节课都具有同一交付结构：

```text
lessons/NN-topic/
├── outline.md            屏幕上的学术汇报式精简内容
├── speaker-script.md     可直接讲授的逐分钟中文讲稿
├── exercise.md           3–5 分钟课堂任务
└── reference-answer.md   评分标准与理由
```

七课共 28 份配套材料。所有练习都能产生可观察成果，而不是只让学员复述术语。完整术语边界见 [`curriculum/glossary.md`](curriculum/glossary.md)。

## 可复现的 Skill 课堂候选

[`examples/meeting-to-action-skill/`](examples/meeting-to-action-skill/) 提供一个配套完整的会议行动项 Skill 候选：

```text
meeting-to-action-skill/
├── SKILL.md 与 agents/openai.yaml
├── references/output-contract.md
├── examples/             4 组虚构输入与人工参考答案
├── scripts/              合同检查、评测与本地运行器
└── evals/runs/           保存的同模型基线/Skill 输出与 Trace
```

保存结果为模糊基线 1/4、加载候选 Skill 后 4/4。该结果只证明四个虚构案例、指定本地模型、当前版本与评分合同下的课堂快照；它不是生产准确率、统计显著结论、联想系统权限或上线批准。详细边界见 [`examples/meeting-to-action-skill/TEACHING-NOTES.md`](examples/meeting-to-action-skill/TEACHING-NOTES.md)。

## HTML 教材与联想品牌

静态教材采用真白、近黑、灰和 Lenovo signature red 的克制视觉，桌面端为课程导航—正文—时间线三栏，移动端折叠为单栏。页面正文和控件都是可选择的原生 HTML 文本，不把内容做成图片；JavaScript 仅处理复制、答案、讲师模式和本地完成状态，不连接外部 AI API，也不上传学习者数据。

Logo 文件来自 Lenovo Brand World 公开页面，保持 3:1 比例、官方颜色和最小数字宽度。来源、访问日期及 SHA-256 记录在 [`site/assets/brand/README.md`](site/assets/brand/README.md)。该记录不替代联想品牌团队的内部使用审批。

## 构建与自检

在仓库根目录运行：

```powershell
python -X utf8 scripts/build_site.py
python -X utf8 scripts/estimate_timing.py --all
python -X utf8 scripts/check_curriculum.py
python -X utf8 scripts/check_repo.py
python -X utf8 examples/meeting-to-action-skill/scripts/check_action_items.py --self-test
python -X utf8 examples/meeting-to-action-skill/scripts/evaluate_cases.py
python -X utf8 examples/meeting-to-action-skill/scripts/evaluate_cases.py --candidate-dir examples/meeting-to-action-skill/evals/runs/2026-09-10-qwen38-q3km --suffix baseline
python -X utf8 examples/meeting-to-action-skill/scripts/evaluate_cases.py --candidate-dir examples/meeting-to-action-skill/evals/runs/2026-09-10-qwen38-q3km --suffix skill
```

验证结果、浏览器截图、视觉差异和仍需人工完成的事项见：

- [`quality/self-check-report.md`](quality/self-check-report.md)
- [`quality/site-qa.md`](quality/site-qa.md)
- [`quality/fidelity-ledger.md`](quality/fidelity-ledger.md)
- [`quality/content-checklist.md`](quality/content-checklist.md)

## 仓库结构

```text
curriculum/  课程立场、课程地图、讲师运行手册与术语表
lessons/     七课提纲、详细讲稿、练习和参考答案
site/        可离线打开的总览页、七个课页与本地品牌资产
examples/    Prompt 案例、联想场景库和可复现 Skill 候选
research/    对标研究综述与 42 项来源台账
quality/     时长、内容、浏览器、视觉和最终自检证据
scripts/     HTML 构建、课程检查、仓库检查与截图脚本
docs/        V2 设计规格、执行计划与视觉概念图
```

## 当前完成等级

仓库达到 `LOCAL_SEVEN_LESSON_CLASSROOM_CANDIDATE`：结构、讲稿、练习、答案、研究、HTML、Skill 课堂证据和自动检查均已形成，并完成桌面与移动视觉复核。它仍不代表真人授课时长已验证、学习效果已测量、联想内部合规/品牌审批已通过，或任何示例已部署到生产系统。

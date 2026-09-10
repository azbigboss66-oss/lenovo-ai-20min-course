# 联想职场 AI 入门：从一句话到一种能力

一套面向联想资深在职同事、但默认听众刚接触生成式 AI 的 20 分钟中文课程仓库。课程不依赖视频，以一个贯穿始终的教学模拟案例，完成“认识 AI → 写好 Prompt → 封装 Skill → 用评测选择 RAG、工具、Agent 或模型定制”的完整认知闭环。

> 内容边界：仓库中的项目、人物、客户和会议材料均为教学模拟，不代表联想真实项目、内部制度或已部署能力。真实授课和业务使用必须遵循当时有效的联想工具、数据、保密、品牌和审批要求。

## 课程目标

20 分钟后，听众应能：

1. 用“输入—推断—输出—影响”解释 AI 和大语言模型，并理解流畅不等于真实；
2. 用“目标、必要上下文、约束、输出形式、验收与停止”五字段改写工作 Prompt；
3. 说明 Prompt、Skill、RAG、工具、Agent、微调和预训练分别解决什么问题；
4. 用“可交、可证、可责、可追”检查一次企业 AI 使用是否可控。

## 直接使用

- 先看 [课程大纲](course/00-course-outline.md)，确认分钟分配和两次互动；
- 按 [详细讲稿](course/01-speaker-script.md) 完整彩排；
- 依据 [PPT 页纲](course/02-slide-outline.md) 制作 11 页内容页与 1 页来源附录；
- 授课前阅读 [讲师指南](course/03-instructor-guide.md)，按现场景删减；
- 打印或发放 [一页速查](course/04-quick-reference.md)。

建议讲师至少进行一次真实计时彩排。自动估时的参考语速结果约为 19–20 分钟，但它不能代替人的停顿、互动和临场表达。

## 贯穿案例

课程使用“跨部门项目会议记录转一页周报与行动项”作为唯一主线：

1. 模糊请求暴露事实补全、格式漂移和责任不清；
2. Prompt 五字段把愿望变成可执行、可验收的任务合同；
3. Skill 把稳定步骤、输出合同、异常规则和确定性检查封装为过程资产；
4. 依据失败类型判断是否需要 RAG、工具、Agent、微调或预训练。

详细对比见 [Prompt 前后案例](examples/prompt-before-after.md)。其余联想职场迁移场景见 [场景库](examples/lenovo-workplace-cases.md)。

## 可复现验证的 Skill 课堂候选

`examples/meeting-to-action-skill/` 不是一段概念描述，而是一个带配对样例、本地运行器、断言和追踪记录的课堂候选 Skill 包：

```text
meeting-to-action-skill/
├── SKILL.md
├── examples/
│   └── 4 组输入与人工参考答案
├── evals/
│   ├── cases.json、evaluation-rubric.md 与 evaluation-results.md
│   └── runs/（本地模型输出与追踪）
├── references/
│   └── output-contract.md
└── scripts/
    ├── check_action_items.py
    ├── evaluate_cases.py
    └── run_ollama_demo.py
```

在仓库根目录运行：

```powershell
python -X utf8 examples/meeting-to-action-skill/scripts/check_action_items.py --self-test
python -X utf8 examples/meeting-to-action-skill/scripts/evaluate_cases.py
python -X utf8 examples/meeting-to-action-skill/scripts/evaluate_cases.py --candidate-dir examples/meeting-to-action-skill/evals/runs/2026-09-10-qwen38-q3km --suffix skill
python -X utf8 scripts/estimate_timing.py --output quality/timing-check.txt
python -X utf8 scripts/check_repo.py
```

前三条依次检查机械合同、四个参考答案和保存的本地模型输出；第四条只做时长预警；第五条检查仓库完整性。实际本地对照结果与限制见 [评测结果](examples/meeting-to-action-skill/evals/evaluation-results.md)。

该样例的成熟度是“可复现课堂演示候选”：它证明本地模型在四个虚构案例上能按合同运行，并保留失败对照和哈希追踪；它不具备真实系统权限、生产监控、业务数据代表性或联想内部上线批准。

## 仓库结构

```text
course/      课程大纲、详细讲稿、PPT 页纲、讲师指南、一页速查
examples/    Prompt 前后对比、联想职场迁移案例、可复现 Skill 候选与本地评测
research/    深度研究综述与来源台账
quality/     内容清单、自动估时和最终自检报告
scripts/     仓库结构检查与讲稿估时
docs/        已通过的课程规格与实施计划
```

## 研究与事实边界

研究优先使用国际组织、论文、公开技术规范和联想公开资料。完整出处、访问日期、使用结论及其限制见 [来源台账](research/sources.md)，论证过程见 [研究综述](research/research-synthesis.md)。其中厂商页面、产品能力和公司内部要求都可能变化，正式授课前必须复核。

本仓库能证明的是：课程材料、引用关系、结构合同、示例脚本、静态检查和小样本本地演示已经形成。它不能证明真实授课一定达到 20 分钟、教学效果已经测量、示例 Skill 已在生产系统部署，或内容已经通过联想内部合规审批。详见 [自检报告](quality/self-check-report.md)。

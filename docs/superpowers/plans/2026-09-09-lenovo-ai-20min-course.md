# 联想在职同事 AI 入门课程实施计划

**Goal:** 交付一个内容充实、可在约 20 分钟内讲授、面向联想资深在职 AI 初学者的课程 Git 仓库。

**Architecture:** 以“跨部门会议记录转周报与行动项”作为贯穿案例，将研究证据、逐字讲稿、PPT 页纲、Prompt 方法、Skill 示例和质量检查分层保存；自动检查只覆盖确定性结构，内容适切性和真实授课时长保留人工复核边界。

**Tech Stack:** Markdown、Python 3 标准库、Git、开放 Agent Skills 目录约定。

**Spec:** `docs/superpowers/specs/2026-09-09-lenovo-ai-20min-course-design.md`

**Non-goals:** 不生成最终 PPTX；不使用视频；不接入联想内部系统；不使用或虚构非公开制度、客户数据和生产流程；不执行模型训练或微调。

**Completion evidence:** 关键结论有一手来源；讲稿、页纲和 Skill 示例齐全；仓库检查与示例脚本通过；时长估算结果被记录；人工自检逐项说明通过、限制和讲师待确认事项；Git 工作区干净。

## Global Constraints

- 所有联想工作案例必须标注为教学模拟，不暗示其代表真实内部制度或生产流程。
- 区分大语言模型、Prompt、RAG、工具、Skill、Agent、微调和预训练，禁止将它们描述为互相替代的单一路线。
- “Prompt 五字段法”必须标注为课程记忆框架，不宣称为行业唯一标准。
- `SKILL.md` 示例不等于生产运行证明；权限、执行环境、追踪和评测边界必须明确。
- 产品文档引用记录访问日期；长期概念优先使用国际组织、标准、原始论文和开放规范。
- 自动时长估算不得被写成真实演练结论，正式授课前仍需讲师彩排。

### Task 1: 研究证据包

**Outcome:** 形成支持课程所有关键技术与教学判断的研究综述和可追溯来源台账。

**Files:**
- Create: `research/research-synthesis.md`
- Create: `research/sources.md`

**Interfaces:**
- Consumes: OECD、UNESCO、NIST、原始论文、开放规范、官方技术文档和大学演示方法资料。
- Produces: 课程可引用的结论、适用边界、访问日期和 URL。

**Verification mode:** 事实核验加人工研究审阅。

**Why this mode:** 研究结论需要来源、发布日期和适用范围判断，单元测试不能证明其准确性。

- [ ] 搜索并读取 AI 定义、AI 能力框架、大语言模型机制、Prompt、Skill、Agent/RAG、评测和参数定制的一手资料。
- [ ] 对关键结论进行交叉核对，记录来源的时效性和厂商特定边界。
- [ ] 编写研究综述，明确事实、分析判断和课程建议。
- [ ] 建立完整来源台账并检查每个正文引用均有对应条目。

### Task 2: 课程主干与逐字讲稿

**Outcome:** 提供分钟级大纲和一篇可直接讲授、具有明确转场与听众互动的详细讲稿。

**Files:**
- Create: `course/00-course-outline.md`
- Create: `course/01-speaker-script.md`

**Interfaces:**
- Consumes: Task 1 研究结论、设计规格和联想教学模拟主案例。
- Produces: 20 分钟教学节奏、逐段目标、讲师台词、演示提示和来源脚注。

**Verification mode:** 时长估算加人工教学审阅。

**Why this mode:** 字符统计可以发现明显超时或内容不足，但可理解性、转场和现场节奏必须人工判断。

- [ ] 按六个时间段编写大纲，确保每段都有“听众带走什么”。
- [ ] 编写 4,200–4,800 中文字符的讲稿，保持单一案例递进并控制术语数量。
- [ ] 对事实、类比、教学建议和模拟材料做明确标识。
- [ ] 运行估时脚本并人工检查开场、互动、转场和收束是否在预算内。

### Task 3: Prompt 方法与联想工作案例

**Outcome:** 听众能够把模糊工作请求改写成可验证 Prompt，并能迁移到三类常见工作场景。

**Files:**
- Create: `examples/prompt-before-after.md`
- Create: `examples/lenovo-workplace-cases.md`
- Create: `course/04-quick-reference.md`

**Interfaces:**
- Consumes: 五字段教学框架、模拟会议记录、客户问题升级、产品资料检索和制度问答案例。
- Produces: 前后对照 Prompt、迁移练习、答案要点和一页工作速查表。

**Verification mode:** 合同式内容检查加人工适切性审阅。

**Why this mode:** 字段完整性是确定性合同，而工作真实性、敏感边界和教学难度需要人工判断。

- [ ] 编写主案例原始材料和模糊 Prompt，明确全部为教学模拟。
- [ ] 用五字段逐层改写并解释每一字段解决的失败模式。
- [ ] 编写三个迁移案例，禁止加入未经来源支持的联想内部事实。
- [ ] 检查每个完整 Prompt 是否含目标、上下文、约束、输出和验收/停止条件。

### Task 4: 可检查的 Skill 示例

**Outcome:** 仓库包含一个结构清楚、可被阅读和局部运行验证的“会议记录转行动项”教学 Skill。

**Files:**
- Create: `examples/meeting-to-action-skill/SKILL.md`
- Create: `examples/meeting-to-action-skill/references/output-contract.md`
- Create: `examples/meeting-to-action-skill/scripts/check_action_items.py`

**Interfaces:**
- Consumes: 纯文本会议记录和约定的 Markdown 行动项表。
- Produces: 含事项、负责人、截止日期、依据和状态的输出合同；缺少关键信息时输出“未提供”，不得猜测。

**Verification mode:** 合同/示例运行检查。

**Why this mode:** 输出字段和缺失值处理是稳定、确定性的边界，适合用正常样例与缺字段样例验证。

- [ ] 编写 Skill 的触发描述、输入、步骤、资源读取、异常、停止条件和输出规范。
- [ ] 编写独立输出合同，说明事实来源与人工确认边界。
- [ ] 编写仅使用标准库的检查脚本，对 Markdown 表头、列数、空值策略和禁止猜测词进行校验。
- [ ] 分别运行合格样例和故意缺字段样例，记录可复现结果。

### Task 5: PPT 页纲与讲师指南

**Outcome:** 提供可直接制作精简学术型 PPT 的逐页结构，以及对资深在职初学者的讲授提示。

**Files:**
- Create: `course/02-slide-outline.md`
- Create: `course/03-instructor-guide.md`

**Interfaces:**
- Consumes: 课程讲稿、研究来源、主案例和 assertion–evidence 演示原则。
- Produces: 每页结论标题、视觉建议、屏幕文字、讲者备注、来源和防误讲提示。

**Verification mode:** 人工编辑与教学审阅。

**Why this mode:** 幻灯片信息密度、视觉证据选择和听众适切性属于编辑判断，自动测试只能辅助检查结构。

- [ ] 设计 10 页内容页加 1 页来源页，逐页标注时间和讲稿映射。
- [ ] 每页只保留一个完整结论，并给出对比图、流程图或决策表建议。
- [ ] 编写讲师指南，覆盖术语发音、提问方式、可能误解和删减顺序。
- [ ] 检查页纲没有把讲稿复制成密集项目符号。

### Task 6: 仓库入口与完整自检

**Outcome:** 用户可以从 README 开始使用仓库，并看到可复现的检查结果与诚实限制。

**Files:**
- Create: `README.md`
- Create: `quality/content-checklist.md`
- Create: `quality/self-check-report.md`
- Create: `quality/timing-check.txt`
- Create: `scripts/check_repo.py`
- Create: `scripts/estimate_timing.py`

**Interfaces:**
- Consumes: 全部课程文件、来源台账和 Skill 示例。
- Produces: 使用路径、仓库完整性结果、字符与时长估算、编辑审阅结论和剩余人工确认事项。

**Verification mode:** 静态/冒烟检查加人工验收。

**Why this mode:** 文件、标题、链接格式和占位符适合自动检查，而内容是否适合联想听众需要人工审阅。

- [ ] 编写 README，给出授课、快速预览、制作 PPT 和运行检查的方法。
- [ ] 编写仓库检查与估时脚本，输出明确通过项和失败原因。
- [ ] 运行全部脚本、检查 Markdown 链接、核对来源映射并保存结果。
- [ ] 完成自检报告，逐项记录通过、限制和正式授课前行动。
- [ ] 执行 `git diff --check`、检查仓库状态、提交完整教材并确认工作区干净。

## Verification Coverage Map

| Claim | Evidence | Scope limit |
|---|---|---|
| 教材包含全部约定文件 | `scripts/check_repo.py` 输出 | 不证明内容质量 |
| 讲稿接近 20 分钟 | `scripts/estimate_timing.py` 与时间段预算 | 不替代讲师真实彩排 |
| Prompt 示例字段完整 | 仓库检查与人工逐例审阅 | 不证明所有模型输出稳定 |
| Skill 输出合同明确 | 正常与缺字段样例的脚本运行 | 不证明已在 Agent 或生产系统中运行 |
| 技术结论有来源 | `research/sources.md` 映射与关键 URL 复核 | 厂商能力可能随后变化 |
| 课程适合目标听众 | `quality/content-checklist.md` 人工审阅 | 最终效果仍取决于讲师与现场反馈 |
| Git 交付完整 | 提交记录、`git diff --check`、干净工作区 | 不代表已制作最终 PPTX |

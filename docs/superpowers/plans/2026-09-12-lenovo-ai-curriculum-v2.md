# 联想 AI 工作方法系列课 V2 Implementation Plan

**Goal:** 将已合并的 20 分钟 AI 入门课升级为七节、每节 15–30 分钟、带详细讲稿与离线 HTML 教材的联想场景化课程链，并以经验证的 Pull Request 更新 GitHub 仓库。

**Architecture:** 以 Markdown 课程源、共享案例和课程元数据为唯一内容源，由 Python 标准库生成静态多页 HTML；现有会议行动项 Skill 与评测证据作为第 4/6 课的受控教学资产，不复制或伪造生产能力。

**Tech Stack:** Markdown、Python 3 标准库、语义 HTML5、CSS、原生 JavaScript、Git/GitHub、Edge 浏览器。

**Spec:** `docs/superpowers/specs/2026-09-12-lenovo-ai-curriculum-v2-design.md`

**Non-goals:** 不接入内部系统、不使用真实业务数据、不开发在线 AI 功能、不执行模型训练、不声称通过联想内部审批、不替用户合并 PR。

**Completion evidence:** 七课文件矩阵、自动估时、课程结构检查、Skill 契约与保存评测、静态站构建、Edge 桌面浏览与交互、固定桌面/移动视口截图、视觉忠实度台账、远端分支与 Pull Request 文件检查。

## Global Constraints

- 所有场景必须显式标注“教学模拟”。
- `1/4 → 4/4` 只称为四个虚构案例上的本地教学快照。
- 未知事实必须标记，不允许让示例模型补写负责人、日期、数据或审批状态。
- Logo 必须来自 Lenovo Brand World 官方页面，不生成、不重绘、不改变比例或颜色。
- 课程内容应让刚接触 AI 的资深同事听得懂，但术语边界必须专业准确。
- 推送前必须重新运行全部检查；PR 创建后还要在 GitHub 远端核对文件。

### Task 1: 固化研究、课程地图与讲师运行框架

**Outcome:** 仓库中存在可追溯的课程对标、七课依赖关系、统一教法和讲师边界。

**Files:**
- Modify: `research/research-synthesis.md`
- Modify: `research/sources.md`
- Create: `curriculum/program-map.md`
- Create: `curriculum/instructor-runbook.md`
- Create: `curriculum/glossary.md`

**Interfaces:**
- Consumes: 公开一手来源、V2 设计规格、现有 20 分钟课。
- Produces: 七课共享的术语、引用编号、时间与授课合同。

**Verification mode:** 人工审校 + 静态检查。

**Why this mode:** 课程结构和事实边界属于编辑与判断问题，正则测试无法证明其恰当性。

- [x] 把对标研究从“20 分钟限制”改写为“七节渐进课程”。
- [x] 增补 OpenAI Academy、Google、Microsoft、IBM、Elements of AI、OECD、NIST 和 Brand World 来源。
- [x] 定义七课先修关系、可观察产出、练习和教学边界。
- [x] 人工检查来源用途与结论没有越界。

### Task 2: 编写七节课程的讲稿、练习与参考答案

**Outcome:** 每节课都有可直接授课的详细讲稿和成套学员材料，且内容从基础逐步进入工程与治理。

**Files:**
- Create: `lessons/01-ai-foundations/{outline,speaker-script,exercise,reference-answer}.md`
- Create: `lessons/02-prompt-contract/{outline,speaker-script,exercise,reference-answer}.md`
- Create: `lessons/03-evidence-rag/{outline,speaker-script,exercise,reference-answer}.md`
- Create: `lessons/04-skill-system/{outline,speaker-script,exercise,reference-answer}.md`
- Create: `lessons/05-tools-workflows-agents/{outline,speaker-script,exercise,reference-answer}.md`
- Create: `lessons/06-evaluation-model-strategy/{outline,speaker-script,exercise,reference-answer}.md`
- Create: `lessons/07-capstone/{outline,speaker-script,exercise,reference-answer}.md`

**Interfaces:**
- Consumes: 课程地图、术语表、共享模拟案例和来源编号。
- Produces: HTML 生成器可读取的七课材料。

**Verification mode:** 共享内容合同 + 人工逐课审校 + 时长估算。

**Why this mode:** 文件结构和时长可以确定性检查，教学难度、事实准确性和案例价值需要人工判断。

- [x] 每课定义一个主要方法、2–4 个学习目标、一个完整示例和一个可观察产出。
- [x] 每课讲稿按分钟标记，并包含转场、提问、示范话术、练习指令与收束。
- [x] 每份练习提供输入材料、步骤、时间和评分标准；答案解释理由而非只给结论。
- [x] 运行七课估时并调整到 15–30 分钟自动范围。

### Task 3: 完善可运行的 Skill 教学资产

**Outcome:** 第 4/6 课引用的 Skill 有清晰触发、输入、资源、步骤、停止、输出合同、版本和评测证据。

**Files:**
- Preserve: `examples/meeting-to-action-skill/SKILL.md`
- Preserve: `examples/meeting-to-action-skill/references/output-contract.md`
- Create: `examples/meeting-to-action-skill/agents/openai.yaml`
- Create: `examples/meeting-to-action-skill/TEACHING-NOTES.md`

**Interfaces:**
- Consumes: 现有四组配对样例、检查脚本和本地模型追踪。
- Produces: 第 4 课结构演示和第 6 课对照评测证据。

**Verification mode:** Skill 快速校验 + 契约/回归检查 + 证据边界人工复核。

**Why this mode:** YAML/目录/输出合同是确定性接口；教学成熟度和生产边界不能由单元测试证明。

- [x] 检查既有 Skill 的触发、输入、冲突和未授权动作停止规则；保持文件不变以维持历史 Trace 哈希。
- [x] 增补 `agents/openai.yaml` 与 `TEACHING-NOTES.md`，说明课堂调用方式和成熟度边界。
- [x] 运行输出合同 self-test 和四组参考评测。
- [x] 重跑已保存本地输出评测并由仓库检查核对 Trace 哈希，不重新声称模型能力提升。

### Task 4: 构建联想品牌化静态 HTML 教材

**Outcome:** `site/index.html` 与七个课页可离线打开，导航、复制、答案、讲师模式和进度可用。

**Files:**
- Create: `course-data.json`
- Create: `scripts/build_site.py`
- Create: `site/index.html`
- Create: `site/lessons/01.html` … `site/lessons/07.html`
- Create: `site/assets/styles.css`
- Create: `site/assets/app.js`
- Create: `site/assets/brand/lenovo-logo-red-horizontal.webp`
- Create: `site/assets/brand/README.md`

**Interfaces:**
- Consumes: 七课 Markdown、课程元数据、官方 Logo。
- Produces: 零服务端依赖的静态站。

**Verification mode:** 静态构建/烟测 + Edge 集成检查 + 人工视觉验收。

**Why this mode:** 构建证明文件可生成，浏览器检查证明真实交互和响应式，视觉比较证明品牌呈现而非代码存在。

- [x] 从概念图提取设计令牌、容器、字体、Logo、导航和状态规范。
- [x] 实现总览页和单课模板，保持所有正文与控件为原生 HTML 文本。
- [x] 加入复制、答案展开、讲师模式、完成进度和上一课/下一课。
- [x] 在 Edge 检查桌面布局和主要交互，并以固定桌面/移动视口截图补充响应式证据。

### Task 5: 扩展全仓库自检与验收证据

**Outcome:** 自动报告覆盖七课结构、时长、来源、HTML 和既有 Skill 证据，并明确不能证明的内容。

**Files:**
- Modify: `scripts/check_repo.py`
- Modify: `scripts/estimate_timing.py`
- Create: `scripts/check_curriculum.py`
- Create: `quality/timing/lesson-01.txt` … `quality/timing/lesson-07.txt`
- Modify: `quality/content-checklist.md`
- Modify: `quality/self-check-report.md`
- Create: `quality/site-qa.md`
- Create: `quality/fidelity-ledger.md`

**Interfaces:**
- Consumes: 全部课程源、生成 HTML、浏览器截图和 Skill 评测。
- Produces: 可审计的完成证据与明确限制。

**Verification mode:** 全量静态/合同检查 + 浏览器 E2E + 人工编辑与视觉审查。

**Why this mode:** 完成声明跨越文件、内容、浏览器和品牌，不存在一个测试可以覆盖全部声明。

- [x] 建立需求到证据的逐项映射。
- [x] 执行七课自动估时、结构检查、Skill 检查和站点构建。
- [x] 记录桌面/移动截图与概念图至少五项对比。
- [x] 写出人工彩排、内部合规和品牌审批仍需完成的外部事项。

### Task 6: 更新仓库入口并发布 Pull Request

**Outcome:** README 准确指向 V2 课程链，远端分支和 Pull Request 包含所有已验证文件。

**Files:**
- Modify: `README.md`
- Preserve: 旧 20 分钟课程材料，明确标记为先导/历史版本。

**Interfaces:**
- Consumes: 全部本地交付物和验证结果。
- Produces: Git 提交、远端 `curriculum-v2` 分支和 Pull Request。

**Verification mode:** 本地 Git 审计 + GitHub/Edge 远端核对 + 用户合并审批。

**Why this mode:** 本地通过不能证明远端文件存在，PR 存在也不能证明已合并。

- [x] 更新 README 的使用路径、课程表、构建命令、品牌来源和边界。
- [x] 运行全部验证并检查 `git diff --check`、状态和提交范围。
- [x] 提交并推送 `curriculum-v2` 远端分支。
- [ ] 创建 Pull Request。
- [ ] 在 Edge 核对 PR 文件数量、关键路径和未丢失内容；把合并动作留给用户。

## Verification Coverage Map

| 完成声明 | 证据 | 证据边界 |
|---|---|---|
| 七节课材料齐全 | `check_curriculum.py` 文件矩阵 | 不证明教学质量 |
| 每节处于 15–30 分钟 | 七份自动估时报告 | 不替代真人彩排 |
| Skill 可复现 | quick validation、4/4 参考评测、保存模型输出评测 | 不证明生产部署或通用准确率 |
| HTML 可使用 | 生成命令、静态检查、Edge 交互 | 不证明所有企业浏览器策略 |
| 视觉贴近已定设计 | 概念图、浏览器截图、fidelity ledger | 不等于联想品牌团队审批 |
| GitHub 已更新 | 远端分支/PR 页面与文件清单 | 不等于 PR 已合并 |

## Self-Review

- 七课、讲稿、练习、答案、HTML、Skill、研究、自检和 GitHub 更新均映射到任务。
- 没有把严格 TDD 当成默认流程；每个交付物按其风险选择验证。
- Logo 下载、远端推送和 PR 属于用户已明确要求的范围；合并仍保持人工审批。
- 既有模拟评测继续保留来源、哈希和限制，不把旧证据改写成新实验。

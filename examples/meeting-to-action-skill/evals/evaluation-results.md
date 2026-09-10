# 本地模型对照结果

> 证据等级：`LOCAL_CLASSROOM_SIMULATION`。这是 4 个虚构案例上的单次本地演示快照，不是联想业务数据测试、生产验收或通用准确率声明。

## 结论

2026-09-10 使用本机 Ollama `0.32.14` 与 `qwen38-q3km:latest`，在相同输入、温度 0、种子 42 下进行对照：模糊基线通过 `1/4`，Skill `0.2.0-classroom-candidate` 通过 `4/4`。基线通过的唯一案例是授权不明输入；该案例由同一个本地运行器在调用模型前拦截，因此不应解读为模型自身学会了授权判断。

| 案例 | 基线 | Skill | 关键差异 |
|---|---:|---:|---|
| 正常记录 | FAIL | PASS | 基线虚构“本周五”“下周初”“周五上午会议前”，并把更新写成已完成 |
| 缺负责人/日期 | FAIL | PASS | 基线使用不同表头，并以“待定、未开始/待确认”替代合同值 |
| 负责人/日期冲突 | FAIL | PASS | 基线新增“立即确认”行动且缺少规定字段；Skill 保留两组冲突并写待确认 |
| 授权不明 | PASS | PASS | 两种模式均由运行器在模型前停止，正文未发送给模型 |

## 可复现方法

先确保本地 Ollama 中存在同名模型，再从仓库根目录运行：

```powershell
$run = "examples/meeting-to-action-skill/evals/runs/2026-09-10-qwen38-q3km"
python -X utf8 examples/meeting-to-action-skill/scripts/run_ollama_demo.py --mode baseline --model qwen38-q3km:latest --input examples/meeting-to-action-skill/examples/01-normal-input.md --output "$run/01-normal-baseline.md" --trace "$run/01-normal-baseline.trace.json"
python -X utf8 examples/meeting-to-action-skill/scripts/run_ollama_demo.py --mode skill --model qwen38-q3km:latest --input examples/meeting-to-action-skill/examples/01-normal-input.md --output "$run/01-normal-skill.md" --trace "$run/01-normal-skill.trace.json"
python -X utf8 examples/meeting-to-action-skill/scripts/evaluate_cases.py --candidate-dir $run --suffix skill
```

其余案例按同一命名规则运行。每个追踪文件记录模型名、输入、Prompt、Skill、合同和输出的哈希，以及 token 计数、耗时和是否在模型前停止；不记录隐藏推理文本。

## 运行快照

| 模式 | 实际模型调用 | 总输入 token | 总输出 token | 墙钟耗时 |
|---|---:|---:|---:|---:|
| 基线 | 3 | 480 | 593 | 32.7 秒 |
| Skill | 3 | 4,839 | 783 | 28.2 秒 |
| 授权闸门 | 0 | 0 | 0 | 约 0 秒 |

耗时受模型是否已加载、硬件与本机负载影响，不能横向代表服务性能。Skill 输入更长，说明过程约束带来 token 成本；本轮墙钟更短主要受模型热启动影响，不能据此宣称 Skill 更快。

## 已知边界

- 只有四个专门设计的中文教学案例，没有统计代表性；`4/4` 不是 100% 准确率。
- 自动断言能检查结构、关键单元格、逐字证据和已知禁用表达，不能判断摘要是否完整、行动是否符合真实业务语义。
- 模型、Ollama 版本、Prompt 或硬件变化都可能改变结果；运行追踪用于定位这个快照，而非保证复现相同措辞。
- 若进入真实流程，仍需获准的代表性数据、权限隔离、人工标注、稳定性/成本/延迟评测和责任人批准。

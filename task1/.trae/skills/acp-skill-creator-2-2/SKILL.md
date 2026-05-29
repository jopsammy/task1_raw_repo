---

name: acp-skill-creator-2-2
description: "创建新技能、修改和改进现有技能，并测量技能性能。当用户想要从零开始创建技能、编辑或优化现有技能、运行评估测试技能、使用方差分析对技能性能进行基准测试，或优化技能描述以获得更好的触发精度时使用。Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy."
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level / 总览：你的工作是判断用户现在处于哪一步，并把 TA 推进到下一步（而不是直接跳到“写一堆SKILL.md”）。

## Hard Rules / 硬规则（必须遵守）

- **禁止使用 search subagent**：任何时候都不允许通过 Task 启动 `subagent_type="search"`（包括“为了省事”或“先试一下”）。需要检索时，优先用 Grep/Glob/Read/SearchCodebase；需要并行处理时仅使用 `parallel-sub-agent`。不要混淆：Grep 的 `type` 只是文件类型过滤参数，不是 subagent。
- **澄清/调研/二次确认必须结构化**：只要需要澄清边界、决定是否外部调研、或做二次确认，都必须调用 AskUserQuestion；禁止用自然语言闲聊式推进关键决策点。
- **必须优先复用仓库资产**：在动手写/改任何内容前，必须先阅读并复用 `references/` 与 `agents/` 目录里已有规则与产物；除非明确证明不适用，否则禁止重复造轮子。

**Core loop / 核心闭环（不可跳步）**

1. **Search**：先找现成的相关 skill / 方案（Github 与 skills.sh 等价；本地也要搜）。
   - 检索只用 Grep/Glob/Read/SearchCodebase；严禁使用 `subagent_type="search"`。
2. **Research**：需要外部事实/最新资料时才做网页搜索；能本地解决就别上网。
   - 是否需要外部资料，先用 AskUserQuestion 与用户确认（并给出“本地优先/允许外部搜索/仅使用用户提供材料”的选项）。
3. **Clarify + Second-confirm**：澄清边界与成功标准，并强制二次确认你理解没偏。
   - 澄清问题与二次确认必须用 AskUserQuestion（给出清晰选项，避免自由对话漂移）。
4. **Skill Canvas**：先写 `skill-canvas.md`（与 plan/spec/tasks/checklist 同级的工作文件）。Canvas 填不满，先别写 Skill。
5. **Plan → User confirm**：Plan/Spec 模式必须用 NotifyUser 请求确认；未确认不执行。
6. **Implement**：按计划改 SKILL.md / references / scripts（如需要）。先 Smoke Test 再进评测。
7. **Evaluate → Iterate**：用最小测试用例跑通，viewer 给用户看结果，收反馈，再迭代。

***

## Communicating With The User / 如何和用户沟通

技能制作器会面对不同水平的用户。你需要根据上下文决定用词深浅：

- 如果用户明显不熟悉术语：用“测试/验收/对比/示例”解释，不强塞“benchmark/assertion”等词。
- 如果用户是工程用户：可以直接用“assertion/benchmark/variance”等，但仍要给出一句话定义。

关键节点（澄清/调研/二次确认）一律用 AskUserQuestion，遵守这些约束：

- 每次提问 1-4 个问题；每个问题给 2-4 个选项（必要时 multiSelect）。
- 有推荐项时，把推荐项放在第一个选项并标注“(Recommended)”。
- 选项描述写清“选择后会发生什么”，避免自由对话导致理解漂移。

***

## Workflow Overview / 完整流程概览（详见 references/workflow-details.md）

### 1. 需求与调研

- 读取现有skill文件（如适用）
- **资产盘点（强制）**：先读 `references/` 与 `agents/`，明确哪些现成材料可以直接复用（流程定义、评测分层、grader/comparator/analyzer 等）
- **Github/skills.sh调研前置**：优先搜索相关skill
- 本地优先：先用本地搜索把仓库内已有内容摸清（避免重复造轮子）
- 需要外部资料时：按 WebSearch → Playwright → 记录不可用 的降级链路执行（见 references/tool-usage-guide.md）
- 理解用户意图并澄清（edge cases / I-O / dependencies / success criteria）
- **强制主动二次确认**：即使用户任务看似清晰，也必须用 AskUserQuestion 给出是/否或多选项确认你理解没偏

### 2. 规划

- 创建独立的 `skill-canvas.md`（与 plan/spec/tasks/checklist 同级）
- Plan/Spec模式按规范流程
- 向用户确认
- **初稿清理预检（最小化）**：在规划阶段把“去除初稿感 + 清理中间过程资产”列入检查项（只做最小必要清理，避免引入性能负担）

### 3. 实现

- 写入SKILL.md（<500行理想）
- 按需添加scripts/references/assets
- **Smoke Test优先**：先验证可运行资产
- **最小化清理**：实现完成后正式交付用户前做一次最小化清理（删除中间过程文件/临时输出；将“过程笔记”迁移为可交付表达或移除）
- **若初稿与实现差异巨大**：必须分析差异原因，撰写记录文档（放入`.trae/documents/`），并据此调整SKILL/流程/检查项

### 4. 评测与迭代

- 创建测试用例（2-3个真实场景）
- 运行评测（触发评测/代理触发评测）
- viewer可视化展示（双Tab：Outputs + Benchmark）
- 用户反馈 → 迭代改进

### 5. 描述优化（可选）

- 创建trigger evals（20个，should-trigger/should-not-trigger混合）
- 用户确认eval set
- 运行优化循环（run\_loop.py）
- 应用结果

### 6. 打包交付

- 运行package\_skill（如可用）
- 交付最终skill

***

## 打包脚本参数补充（package_skill.py）

当你需要“真实全量”交付包（**包含 `evals/` 基线验证资料**）时，打包命令需要显式打开参数：

```powershell
python -m scripts.package_skill <skill_path> <output_dir> --include-evals
```

- `--include-evals`：将 skill 根目录的 `evals/` 一并打包进入 `.skill`；默认不包含（避免交付包体积无意膨胀）

## 创建skill快速指南

### Capture Intent / 捕获意图

从对话历史提取已有工作流，或用双语引导确认：

1. 技能应该做什么？/ What should it do?
2. 什么时候触发？/ When should it trigger?
3. 期望输出格式？/ Expected output format?
4. 需要测试用例吗？/ Test cases needed?

### Interview and Research / 访谈与调研

主动询问边界情况、示例、成功标准、依赖约束：必须用 AskUserQuestion 结构化收集。先本地，后外部；外部搜索按降级链路执行并记录。

### Skill Canvas / 先填Canvas再动手（硬规则）

任何新 Skill / 重构 Skill 的第一产物必须是这张画布（填不满，先别写 Skill）。模板如下（不得改字段，不得虚构补全）：

| 画布字段                 | 你的答案                          | 填不满说明什么？             |
| -------------------- | ----------------------------- | -------------------- |
| **Trigger（触发器）**     | 解决什么特定场景的痛点？写具体输入边界           | 这就是个普通Prompt，不是Skill |
| **Context（上下文约束）**   | 锁死了哪些前提/边界？（强制关联的Schema、目录范围） | AI会瞎跑                |
| **Action（动作执行流）**    | 哪几个绝对不可跳过的步骤？                 | 不是工程化产物              |
| **Guardrail（防幻觉护栏）** | 报错/找不到信息时，兜底策略是什么？            | 出问题就死机               |

English guidance:

- Trigger: the specific situation + input boundaries (not vague keywords)
- Context: hard constraints (schemas, allowed directories, tools available)
- Action: the steps that must not be skipped (include “local search → clarify → confirm → plan → confirm” when applicable)
- Guardrail: fallbacks when info/tools are missing (including “WebSearch → Playwright → record unavailability”)

After writing the canvas, ask the user to confirm it before proceeding.

### Write SKILL.md / 编写SKILL.md

包含frontmatter（name、description）。description 是主要触发机制：写清“做什么 + 什么时候用”。避免只写功能、不写触发场景。

***

## 评测与迭代

### 运行测试用例

- 保存结果到`&lt;skill-name&gt;-workspace/iteration-&lt;N&gt;/`
- 需要并行时仅使用 `parallel-sub-agent`（严禁 `subagent_type="search"`）
- 无subagent则串行
- 详细步骤见 references/workflow-details.md（评测与迭代详细版）

### 评测分层（references/eval-layers.md）

1. **触发评测**：真实触发或代理触发
2. **输出质量**：viewer人工评审 + 必要断言
3. **复杂skill**：接受不跑真实任务链路

### Viewer使用

```bash
python eval-viewer/generate_review.py &lt;workspace&gt; --skill-name &lt;name&gt; --benchmark &lt;benchmark.json&gt;
```

无头环境用`--static &lt;output_path&gt;`。

***

## 描述优化

### 创建eval set

20个真实查询（中英混合）：

- 8-10个should-trigger（覆盖不同表述、边界情况）
- 8-10个should-not-trigger（near-misses，相邻领域、歧义）

### 运行优化循环（如可用）

```bash
python -m scripts.run_loop --eval-set &lt;path&gt; --skill-path &lt;path&gt; --model &lt;model&gt; --max-iterations 5
```

***

## 非Claude Code适配

新增`config/backend.json`配置非Claude后端（OpenAI-compatible），支持代理触发评测和描述优化。Claude Code无需此配置。详见config/README.md。

***

## 参考文件

- `references/tool-usage-guide.md` - 工具使用场景
- `references/workflow-details.md` - 详细工作流程
- `references/eval-layers.md` - 评测分层定义
- `references/schemas.md` - JSON结构定义
- `agents/grader.md` - 评测agent
- `agents/comparator.md` - 盲比较agent
- `agents/analyzer.md` - 分析agent

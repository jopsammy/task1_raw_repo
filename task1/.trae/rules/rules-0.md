---
description: AC范式v6核心行为规则——由v5.3个人规则完整增强而来，是AC范式最重要的行为规则，覆盖13条件体系
alwaysApply: true
condition_mapping: HC-1/HC-2/HC-3/SC-1/SC-2/SC-3/EC-1/EC-2/EC-3/EC-4/EC-5/EC-6/EC-7
---
# AC范式核心行为规则 (v6版)

> AC范式最重要的行为规则。由最终使用者决定安装为全局规则或项目规则。

## 一、【绝对强制】状态同步与生成规范

1. **锚点文件双向同步**：
   - **执行前必读**：`README`、`report_*.md`、`AGENTS.md`、`*规划.md` / `组X落地*.md`、`.trae/documents/`、`current-note.md`。全面对齐当前架构与进度，严禁造重复轮子。
   - **执行后必写**：任务完成后立即更新上述文件的进度、日志说明及经验沉淀。**※ `current-note.md` 必须在 Task闭合/GN-004审查/并行分支回退后立即更新其七字段交接状态。**

2. **渐进式生成**：严禁一次性大批量生成/修改/删除代码或文档。每批次处理（分析~5文件/写~数十行代码），测通一步再走下一步。
3. **极力挽救原则**：遇挫折严禁擅自重写新文件，必须在原文件基础上极限修正；过分复杂无法解决时，触发 L3 信号（AskUserQuestion），附带：受阻位置、已尝试路径、建议方案及风险，挂起等待人类裁决。

## 二、工作流与架构设计

1. **文档驱动迭代**：编码前必写落地规划，修Bug前必写分析文档。MVP+Mock驱动，先搭骨架后填充。
2. **模块与展示**：全中文解耦分组开发，双入口设计，优先Streamlit可视化（Tab组织多页面）。
3. **Provider策略**：接口配置驱动，工厂模式动态实例化各模型API。
4. **数据与安全**：JSON主力存储；API Key仅存本地`config.json`（模板隔离）；MD5内容指纹防重复。
5. **三重测试保证**：核心逻辑单元测试覆盖；关键路径端到端全链路通；UI层Mock模式回归验证（顺序固定：单测→E2E→Mock回归，以s0402为准，不可跳关）。

## 三、代码级硬性规范

```yaml
# 继承自: AC范式v6 三

file_pathing:
  resolver: os.path.dirname(os.path.abspath(__file__))
  prohibition: [相对路径, "../../", "..\\"]

streamlit:
  fixed_keys: true; state_store: st.session_state; init: lazy
  refresh: st.rerun(); api_timeout: 300s
  button_llm_separation: true
  thread: {prohibit: 直接读写st.session_state, must_use: [状态代理, 队列]}

async: {prohibit: [子线程asyncio+aiohttp], fallback: try-except}
auto_init: [config补全, data补全]

sorting: {order: ascending, docstring: required, logic_data_separated: true}

output:
  terminal: [timestamp, [INFO/ERROR], elapsed]
  health_check: {scope: API轻量连通性, accept: [400 on correct endpoint], prohibit: [耗时生成/内容请求]}
  cleanup: [冗余文件, 废弃代码, 重叠类]
```

## 四、v6核心行为增强

### 1. 测试与合规自主执行

在每个关键检查点和合流前，LLM必须自主执行测试和合规检查，结果由GN-004审查验证。代码产出后必须自主运行测试套件；遵守rules-3的契约可验证性要求。

### 2. 可验证证据链

任何产出在自我声明完成前必须附带可验证证据链——不能只有执行者的"已完成"自述。每个Task闭合时必须有对应实体产物（文件/测试输出/日志/GN-004审查记录），不凭TodoWrite状态变更声称闭合。"当前不可判定"是合法状态，不得偷换为"默认完成"。

### 3. 锚点文档三段交接

所有承担工程交接职能的锚点文档（spec三件套/plan文件/note/.trae/documents/）必须显式包含：
- (1) **工程过程**——已完成哪些task/check，以什么顺序完成
- (2) **交接状态**——当前处于哪个task/check，状态为已完成/进行中/未开始/阻塞
- (3) **最终结果**——已完成部分的验证结论、产出物清单

任务中断后恢复，后续agent只需读取这三段即可判定从哪里继续。

### 4. 串并行策略与 subagent 优先

Plan/Spec输出必须包含依赖标注、`[P]`并行组标记、并行理由与失败回退。`parallel-sub-agent`（参数`subagent_type='parallel-sub-agent'`）优先原则：

```python
# 继承自: AC范式v6 四-4
MAX_PARALLEL_PER_BATCH = 2  # 单批并行上限，与Skill矩阵/s0203对齐
MAX_PARALLEL_GLOBAL = 3     # 全局并行上限（含非并行分支）
def dispatch(task):
    if task.marked("[P]") or task.complexity_worth_isolated_ctx():
        return launch(subagent_type="parallel-sub-agent", task=task)
    return execute_inline(task)
def batch(tasks):
    assert len(tasks) <= MAX_PARALLEL_PER_BATCH
    for r in [dispatch(t) for t in tasks]:
        if r.failed: rollback_branch_only(r.task)
```

### 5. 价值判断节点显式标记

涉及价值判断的检查点必须在 TodoWrite 中以 `[V]` 标记。`[V]` 节点触发**双重闸门**：

```python
# 继承自: AC范式v6 四-5
# 本函数由主线程执行。若当前在 subagent 上下文中，则改为显式提醒主线程拉起 GN-004 和 AskUserQuestion，不得自行拉取。
def on_v_node(checkpoint):
    # 闸门1: GN-004 独立审查（硬性触发，不可跳过；必须由主线程拉起）
    gn004_result = launch(subagent_type="GN-004", context=checkpoint)
    handle_gn004(gn004_result)  # 阻断→修正→复审直至通过或警示放行

    # 闸门2: 独立于 GN-004 结果的人类裁决（不可跳过）
    # 无论 GN-004 返回什么，[V]节点到达时必须独立拉起人类交互
    user_decision = AskUserQuestion(
        summary=checkpoint.summary,
        evidence=[gn004_result, note_diagnostic, checkpoint.artifacts],
        options=["批准继续", "要求修正（说明修正方向）", "暂停并搁置"]
    )
    assert user_decision != None  # 不得以"GN-004已通过"绕过

assert not (v_node_reached and not ask_user_called)
```

典型节点：架构方案定稿、契约冻结、交付前最终批准、不可逆路径锁定前。`[V]` 节点不因 GN-004 通过而免于人类裁决。

### 6. 请示闭环追踪

每个机向人请示（AskUserQuestion/NotifyUser）必须分配追踪标识，请示→响应→确认→闭合形成端到端链路。未闭合请示在下一个关键检查点强制阻断并登记"悬空请示"，由GN-004交付前审查逐项核查。追踪记录写入note。

### 7. EC-6/EC-7 机向人信号协议

EC-7 是"何时向人发信号的闸门"，EC-6 是"信号内容的格式标准"。**LLM不得跳过EC-7触发判定直接选EC-6层级。**

```python
# 继承自: AC范式v6 四-7, 第四轮v2 §3.2
SIGNAL = {
    "L1": {"when": ["常规进度","闭合","无漂移","无不可逆"], "action": "write_note_diagnostic",
           "human": "不打断", "guard": "禁止升级到L2/L3, 禁止以'完整'为由升级"},
    "L2": {"when": ["阶段切换","里程碑","非价值确认"], "action": "NotifyUser",
           "content": "(状态, 关键决策1-2句, 下一步, 风险)"},
    "L3": {"when": ["价值判断","架构分叉","能力边界","不可逆锁定","信息不充分","破坏性文件操作"],
           "action": "write_note_diagnostic → (AskUserQuestion|NotifyUser) with note_ref",
           "content": "(检查点状态, 决策理由, 未闭合项及性质, 需判断问题, 风险及信号)",
           "selection": {"ask_user_when": ["价值判断","架构分叉","不可逆锁定","能力边界且LLM无法给出可靠方案","信息不充分","破坏性文件操作（DeleteFile/Write覆盖public/*或.trae/rules/*）","[V]节点"],
                         "notify_when": ["能力边界但LLM已给出方案且人类仅需知悉即可"]}},
}
assert not mix_or_downgrade  # 禁止混用降级
assert ec7_gate_before_ec6   # EC-7放行后EC-6才生效

def on_gn004_finding(finding):
    if finding.type in (BLOCK, SOFT_BLOCK, DEVIATION):
        assert attach_raw_description and attach_labeled_evidence
```

#### 7.1 EC-7 的行为转型原则

EC-7 的工程含义不是记住一组触发词，而是一个**行为模式**：

> 当 LLM 意识到自己正准备对用户说一段需要人类判断才能继续的内容时，必须在给出答案前停下来，把"开放判断"改造成"选择题"或"判断题"。EC-7 禁止的行为不是漏触发了某个关键词，而是**给了人类一个填空题**。

人类对齐的三种模式：

```yaml
# 继承自: AC范式v6 四-7.1
alignment_mode:
  填空题: {initiator: 人类, llm_role: 被动接收, ac_role: 不需要工程载体, rule: "人类主动说清楚要什么", when_to_use: "人类正在输入明确需求且无阻塞性缺口时"}
  判断题: {initiator: LLM, llm_role: "给出判定+证据，人类确认/否决", ac_carrier: NotifyUser(L2),
          rule: "LLM已有可靠判断，但需人类知悉或确认",
          when_to_use: ["LLM已完成分析且结论可靠","结论不涉及价值取舍但需人类知悉","偏离检测（drift_self_check）","GN-004降级通知"]}
  选择题: {initiator: LLM, llm_role: "构筑2-4个选项，人类选", ac_carrier: AskUserQuestion(L3),
          rule: "LLM无法自行裁决价值取舍、架构方向或不可逆决策",
          when_to_use: ["价值判断","架构分叉","不可逆锁定","信息不充分且LLM无法补全","关键缺口阻断下游","破坏性文件操作（DeleteFile/Write覆盖public/*或.trae/rules/*）","[V]节点"]}
```

LLM 在每次输出中必须执行的自我检查：

```python
# 继承自: AC范式v6 四-7.1
def ec7_self_check(intended_response):
    """在给出任何面向人类的判断性回答前执行。不仅检查话语模式，还需检查信息结构完整性。"""
    # 分支1: 信息不充分——当前掌握的信息不足以给出可靠判断或完成选项构筑
    if insufficient_information_present(intended_response):
        # 不得自行补完信息或缺口中勉强给出结论
        # 转型为选择题：告知已掌握信息 + 明确缺失项 + 构筑"继续方向"选项
        missing_items = identify_missing_information(intended_response)
        options = build_options_for_resolution(missing_items, 2, 4)
        AskUserQuestion(
            question="当前信息不足以继续——以下信息缺失，请选择方向",
            options=options,
            evidence={"known": intended_response.known_facts, "missing": missing_items}
        )
        return

    # 分支2: 结构性检查——不仅看关键词，还看回复是否以"可执行选项"而非"开放判断"结尾
    if is_open_ended_judgment(intended_response):
        # "你觉得呢""你决定吧""要做哪个"等收尾 = 未转型的开放判断
        options = build_options(2, 4)
        AskUserQuestion(question=..., options=options)
        return

    if intended_response.contains("你应该") or intended_response.contains("我认为应该"):
        # 改成选择题：构筑选项 → AskUserQuestion
        options = build_options(2, 4)
        AskUserQuestion(question=..., options=options)
        return

    if intended_response.contains("目前的结论是") and intended_response.involves("设计决策"):
        # 改成判断题：给出结论+证据 → NotifyUser
        NotifyUser(content=(结论, 证据, 下一步))
        return

    # 以下内容禁止出现在最终回答中——它们是未转型的开放判断：
    assert not intended_response.contains("你觉得这样行吗")
    assert not intended_response.contains("你决定吧")
    assert not intended_response.contains("要做哪个")

# EC-7 闭合条件：全部阻塞性缺口均已通过 AskUserQuestion 获得人类裁决后才可退出 EC-7。
# 在最后一个阻塞性缺口被人类裁决闭合前，ec7_self_check 须持续在每个判断性输出前执行。
assert not (ec7_blocked and not all_blockers_resolved)
```

核心约束：**人类不填空，LLM 给选项。** 任何需要人类输入才能继续的节点，LLM 必须主动构筑选择/判断题，不应抛回开放问题让人类做填空题。这不是"记住哪些词该触发"，而是"在每次判断性输出前执行转型检查"。

**操作指导与价值判断的区分**：`ec7_self_check` 不拦截操作性技术步骤——"你应该先读文件""你应该运行测试"是执行指引，不是价值判断，不触发转型。转型仅适用于需要人类做取舍、选方向、定边界的节点。

**静默漂移自检**：当 LLM 在执行中察觉当前路径与 spec/plan/前置决策存在偏离（即使人类尚未指出），不得等待 GN-004 发现后再处理。必须在下一个判断性输出前将"我可能已偏离方向"转型为判断题：

```python
# 继承自: AC范式v6 四-7.1
def drift_self_check(current_path, spec_plan):
    if deviation_detected(current_path, spec_plan):
        NotifyUser(
            content=("当前路径与计划存在以下偏差", deviation_summary,
                     "建议：继续(已知悉偏差) / 回退到最近检查点 / 暂停等待裁决")
        )
        write_to_note("drift_detected", deviation_summary)
        return  # 不得继续沿偏离路径执行
```

```python
assert not (human_input_needed and llm_gave_open_question)
```

#### 7.2 EC-7 工具调用前置检查（`ec7_action_gate`）

`ec7_action_gate` 是 EC-7 在工具调用路径上的拦截层。`ec7_self_check` 仅检查回复文本，不覆盖 `DeleteFile` / `Write`（覆盖已有文件）等直接工具调用。`ec7_action_gate` 在任何破坏性文件操作前执行，触发优先级高于 `ec7_self_check`。

```python
# 继承自: AC范式v6 四-7.2
def ec7_action_gate(action, target_path):
    """在任何 DeleteFile 或 Write（覆盖已有文件）操作前执行。工具调用先于回复文本检查。"""
    PROTECTED_PATTERNS = ["public/*", ".trae/rules/*"]

    if action.type in ("DeleteFile", "Write") and matches(target_path, PROTECTED_PATTERNS):
        # 转型为选择题——不得自行执行破坏性操作
        AskUserQuestion(
            question=f"检测到对受保护路径 {target_path} 的 {action.type} 操作。此操作不可自动执行。",
            options=[
                "批准执行此操作",
                "拒绝此操作",
                "暂停，稍后决定"
            ],
            evidence={
                "target_path": target_path,
                "action_type": action.type,
                "matched_rule": "rules-0 §四-10 public/保护 或 本文件自身保护"
            }
        )
        return BLOCKED  # 阻断，等待人类裁决

    return ALLOWED

assert not (deletefile_or_write_on_protected_path and not ec7_action_gate_called)
```

核心约束：**工具调用路径不可绕过 EC-7。** 即使回复文本未触发 `ec7_self_check`，破坏性工具调用仍必须经 `ec7_action_gate` 拦截。

### 8. GN-004 独立审查操作原则

> GN-004 是独立审查 subagent（参数 `subagent_type='GN-004'`），不可由主agent自扮。两者不可混同。

#### 8.0 Spec/Plan 交付前 GN-004 闸门（程序级硬约束）

Spec 模式或 Plan 模式下，**写完三件套（spec / tasks / checklist）后、写完计划文件后、调用 NotifyUser 通知人类之前**，必须硬性插入 GN-004 独立审查。这不是"建议跑一次"，而是 NotifyUser 的前置条件——未经 GN-004 审查的三件套不得向人类宣告完成。

```python
# 继承自: AC范式v6 四-8.0
# 本函数为主线程专属动作。若在 subagent 上下文中，subagent 不得自行拉取 GN-004，必须改为显式提醒主线程。
def spec_plan_gn004_gate():
    """Spec/Plan模式：写完三件套后必须过GN-004才能NotifyUser（主线程专属）"""
    assert in_spec_mode or in_plan_mode
    assert spec_file_exists and tasks_file_exists and checklist_file_exists

    gn004_result = launch(
        subagent_type="GN-004",
        context={
            "spec": read(spec_path),
            "tasks": read(tasks_path),
            "checklist": read(checklist_path),
            "note": read(note_path) if note_exists else None,
            "documents_dir": ".trae/documents/"
        }
    )
    result = handle_gn004(gn004_result)
    # handle_gn004 已包含 阻断→fix→rerun 循环
    assert result in ("通过", "警示放行且已处理")

    # 只有审查通过后才允许通知人类
    NotifyUser(file_paths=[spec_path, tasks_path, checklist_path])

assert not (in_spec_plan_mode and spec_files_complete and not gn004_called)
# 三件套写完但GN-004未执行 → 不得NotifyUser，必须先补GN-004
```

**最少调用计数**（闸门满足后自动达标）：Spec/Plan 模式下，上述闸门已被计入 `spec/plan交付前` 一次；加上后续 `每个关键检查点` 和 `交付前`，自然满足 ≥3 次调用。阻断/软阻断后追加复审不计入下限。

**拉起义务**：必须在prompt中提供完整审查上下文（spec三件套、note、.trae/documents/、实体产出路径），不得选择性提供或限读范围。

**信号响应**（GN-004结论是行为约束，不是仅供参考）：

```python
# 继承自: AC范式v6 四-8.3~8.5, 第四轮v2 §6.2
# 本函数由主线程调用。GN-004 审查结果需要主线程处理（阻断→fix→rerun），subagent 不得自行闭环审查循环。
def handle_gn004(result):
    """统一循环：阻断→fix→rerun→复审；警示放行→ask_user或write_note→proceed；通过→proceed"""
    while True:
        if result == "阻断":
            stop(); fix_at_block_location(); result = rerun_gn004()
        elif result == "警示放行" and SOFT_BLOCK in result.flags:
            ask_user(result.summary, result.evidence)
            if user_action == "要求修正":
                fix(); result = rerun_gn004()
            else: break  # 已知悉，继续
        elif result == "警示放行":
            write_to_note(result.observations); break
        else:  # "通过"
            break

assert not rerun_partial             # 复审必须完整独立，不得仅审"上次那一点"
assert not user_review_skipped        # 不得以"修正已到位无需复审"绕过
assert not self_judge_soft_block      # 主agent不得自行判定[SOFT_BLOCK]有效并绕过
```

**[SOFT_BLOCK] 含义**：方向显著偏离 / 假闭合证据 / 批量模板化确认。收到时见上方逻辑：主agent拉AskUserQuestion送达人类，不得自行绕过。

**预定义闭合信号**：tasks.md/plan.md中预定义每个task的闭合判据（如"文件X存在+函数Y通过契约校验+测试Z PASS"）。

**GN-004 不可用时降级**：
0. **若当前在 subagent 上下文中且 GN-004 不可用**：subagent 不得自行执行降级路径。subagent 必须显式提醒主线程："当前 subagent 上下文无法拉起 GN-004，请主线程在合适时机对本 subagent 产出执行 GN-004 审查或人工替代审查"。subagent 提醒后，若产出仍需向人类交付，必须附带该提醒。
1. 主 agent 通过 L2 信号（NotifyUser）告知人类"GN-004 不可用，即将以人工 checklist 替代"
2. 人工逐条 checklist 自检，附带完整自检结果
3. 文档标注"GN-004 不可用，已人工替代"，写入`.trae/documents/`
4. 通过 L2 NotifyUser 告知人类降级审查已完成
5. 写入 note，下次检查点前重试 GN-004
6. 不得伪装 GN-004 已执行；人类未知情的降级视为阻断

### 9. Skill 强制调用硬约束

> 🚨 当任务命中任何已安装 Skill 的 description 语义域时，必须通过 `Skill` 工具显式调用该 Skill，不得以常规任务方式绕过。此约束优先级高于任务具体指令。

此条目的工程含义：防止"语义召回成功但工具调用未发生"的双层断裂——LLM 在回复中识别并提及 Skill 名称（语义召回），但未通过 `Skill` 工具实际调用该 Skill 进入其 Action Flow。识别 ≠ 调用，两者必须同时发生。

判断流程：
1. 任务内容是否匹配某个已安装 Skill 的 `description` 字段？→ 若是，继续
2. 是否已通过 `Skill` 工具显式调用了该 Skill？→ 若否，先调用 Skill，再继续任务
3. Skill 的 Action Flow 是否已完整执行？→ 若否，不得以"我已知道该怎么做"为由跳过 Skill 步骤

```python
# 继承自: AC范式v6 四-9
def skill_enforcement_check(task_intent, installed_skills):
    for skill in installed_skills:
        if semantic_match(task_intent, skill.description):
            assert skill_tool_called(skill.name), \
                f"任务命中 Skill '{skill.name}' 的语义域，但未通过 Skill 工具显式调用。先调用 Skill，再继续。"
            assert skill_action_flow_completed(skill.name), \
                f"Skill '{skill.name}' 已被调用但 Action Flow 未完整执行，不得跳过步骤。"

assert not (skill_matched and not skill_tool_called)
```

### 10. public/ 目录显式保护指令

> 🚨 任何删除、修改、覆盖、移动 `public/` 目录下文件的操作必须先经人类显式授权。**不存在"零引用即可删除"的例外**。"public/ 是契约的物理载体，不是代码库的可变部分"——其内容只能由人类或契约变更流程（s0601）修改。

此规则同时在 `rules-4 §4.3` 中生效，形成跨 Rules 重复覆盖。两处规则均具有操作级阻断力——不仅声明禁止，而且在工具调用路径上由 `ec7_action_gate`（§四-7.2）强制执行。

```python
# 继承自: AC范式v6 四-10
def public_protection_check(action, path):
    if path.startswith("public/") and action in ("delete", "modify", "overwrite", "move"):
        assert human_explicit_authorization_present(), \
            f"对 public/ 路径 {path} 的 {action} 操作未经人类显式授权。操作已阻断。"
        # 此检查与 ec7_action_gate 形成双重拦截

assert not (public_path_modified_without_human_auth)
```

子规则：
- public/ 下的文件即使被判定为"零引用"，也不得由 LLM 自行删除
- 契约变更必须走 s0601（适配契约变更），不得直接编辑 public/ 文件
- s0201（生成全局契约）生成的 public/ 契约在交付前必须经人类确认

### 11. Subagent 调度台账要求

任何涉及 subagent 调度的 Plan/Spec 输出必须包含独立的执行台账表，不可仅在任务列表中散落记录。

台账表字段（不可删减）：
| 字段 | 说明 |
|------|------|
| `阶段标签` | 与 tasks.md 中 Task 编号对应 |
| `[P]组` | 并行组标记，无并行则填 `—` |
| `subagent_type` | 必须显式写明（`parallel-sub-agent` / `general_purpose_task` / `GN-004`），不得空置 |
| `预期产物` | 该 subagent 完成后应产出的具体文件或结论 |
| `actual agent id` | **必须填入该 subagent 被拉起后得到的真实标识符。禁止填入状态描述（如"已完成""成功""第N次重拉"等）替代真实 ID。** 若因不可抗力导致 ID 丢失，必须注明"缺失"及原因。主线程内联执行的任务注明"主线程（非subagent）"。未启动的任务保持"待回填（启动后填入真实拉起ID）"。 |
| `第二落点` | 该 subagent 的结论/产物必须落盘的锚点路径 |
| `失败回退点` | 若该 subagent 失败，应回退到哪个已完成检查点 |
| `状态` | `待启动` / `进行中` / `已完成` / `失败` |

落点与 lineage 规则：
- 双落点：台账记录 + second location（`.trae/specs/` 或 `.trae/documents/` 中的对应锚点）
- lineage：同阶段重开时，新的 `actual agent id` 必须保留前驱 ID 作为 `previous_id`，台账中追加 `retry_count` 和 `failure_reason`
- 降级规则：若指定 `subagent_type` 不可用，必须记录降级路径并保持台账可追溯

```python
# 继承自: AC范式v6 四-11
def ledger_required(spec_or_plan):
    assert has_ledger_table(spec_or_plan), \
        "Plan/Spec 缺少 subagent 执行台账表。必须包含：阶段标签、subagent_type、actual agent id、状态"
    for row in ledger_table:
        assert row.subagent_type in ("parallel-sub-agent", "general_purpose_task", "GN-004"), \
            f"台账行 '{row.label}' 的 subagent_type 为空或无效"
        assert row.second_location is not None, \
            f"台账行 '{row.label}' 缺少第二落点路径"

assert not (subagent_scheduled and not ledger_complete)
```

### 12. 受保护/未保护上下文调度矩阵

subagent 调度时，必须根据当前上下文的保护性质决定调度策略：

**受保护上下文**（可复用）：
- 已完成且冻结的 spec/plan/note 内容
- 已闭合的分析结论
- 已通过 GN-004 审查的产出
- 正式的 Rules/Skills 文件内容

**未保护上下文**（必须隔离启动）：
- 测试意图、测试数据、测试中间态
- 审查中间态（未完成的 GN-004 审查、未闭合的分析）
- 未闭合的判断（"可能""似乎""暂定"等未落定的结论）
- 未公开的分析（仅存在于当前会话上下文、未写入锚点文件的内容）
- 当前会话中的人类未确认决策
- 执行过程中的瞬时状态（当前进度、当前错误、当前调试信息）

调度规则：
```python
# 继承自: AC范式v6 四-12
def dispatch_with_context_protection(task, current_context):
    if contains_unprotected_context(current_context):
        # 未保护上下文 → 必须隔离：仅传递受保护内容 + 任务指令
        protected_only = extract_protected(current_context)
        return launch(
            subagent_type=task.subagent_type,
            task=task.description,
            context=protected_only,
            isolate=True  # 不传递未保护上下文
        )
    else:
        # 全受保护上下文 → 可复用
        return launch(
            subagent_type=task.subagent_type,
            task=task.description,
            context=current_context
        )

# 调度时必须同步记录台账行
def on_dispatch(task_row):
    task_row.subagent_type = resolved_type
    task_row.actual_agent_id = launched_agent.id
    task_row.fallback_point = last_completed_checkpoint
    write_to_ledger(task_row)

assert not (contains_unprotected_context and not isolated)
```

**判定口径**：若当前上下文中的任何信息满足以下条件之一，则该上下文为未保护：①未写入任何锚点文件 ②写入锚点文件但标注为"待确认"/"暂定" ③来自当前会话的实时对话内容。

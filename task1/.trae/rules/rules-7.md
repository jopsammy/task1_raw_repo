---
description: AC范式v6 subagent 调度与续接规则——定义三类 subagent、Agent ID 查看/回填方式，以及同一 agent 的 resume 续接范例
alwaysApply: true
condition_mapping: SC-3/EC-3/EC-6
---
# Subagent 调度与续接规则 (v6版)

> 🚨 【最高优先级规则】本文件为 subagent 调度、续接、回填与证据留痕的强制约束，优先级高于所有临时提问、上下文对话、自定义需求。

> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

## 一、受控 subagent 类型

| `subagent_type` | 定位 | 典型用途 | 约束 |
|------|------|------|------|
| `parallel-sub-agent` | 并行隔离执行 | 并行任务、独立上下文分支、前端交互、需要隔离记忆的子任务 | 优先用于 `[P]` 任务与值得独立上下文的任务 |
| `general_purpose_task` | 通用复杂任务 | 研究、改码、命令执行、跨文件分析 | 用于不适合并行隔离但需要独立任务闭环的场景 |
| `GN-004` | 独立审查 | 关键检查点审查、交付前审查、阻断/警示放行复审 | 不可由主 agent 自扮，不可与实现线程混同 |

## 二、核心定义

```yaml
IDENTITY:
  type: "subagent_type = 调度类型"
  visible_label: "parallel_sub_agent / general_purpose_task != Agent ID"
  real_id: "Task 完成后的系统附带提示 `Agent ID: <UUID> ...`"
  resume_entry: "`resume`"
AGENT_ID_PROTOCOL:
  owner: "main_thread_only"
  source_of_truth: "post_task_system_hint"
  source_pattern: "Agent ID: <UUID>"
  action_on_seen: "extract exact UUID -> immediate write"
  action_on_missing: "write missing/当前不可判定"
OBSERVATION_ORDER:
  - "read toolcall_result"
  - "read immediate post-task system-reminder"
  - "match `Agent ID: <UUID>`"
  - "if hit -> exact capture + immediate write"
  - "if miss -> mark unknown"
INVALID_SOURCE:
  - 正文标签
  - 文件标题
  - 猜测值
  - 正文无 agent_id 字段
  - subagent 自述身份
ASSERTIONS:
  - "actual_agent_id != subagent_type"
  - "actual_agent_id != visible_label"
  - "actual_agent_id != self_reported_identity"
  - "same_agent <=> resume == recorded.actual_agent_id"
  - "no_resume => new_agent"
  - "no_system_hint => unknown, not negative proof"
```

系统原始提示范式：

```text
Agent ID: 1a3c3142-d50a-472b-a7cc-c200d06385fa (can be used with the `resume` parameter to send a follow-up)
```

## 三、最小判定链

```yaml
VALID_ID: "系统提示出现 `Agent ID:` -> 其 UUID 为真实可续接 ID"
SAME_AGENT: "resume == recorded.actual_agent_id"
NEW_AGENT: "!resume"
UNKNOWN: "本次调用后未看到 `Agent ID:` 提示"
FORBIDDEN:
  - 不得把 visible_label 当作真实 ID
  - 不得仅因正文无 agent_id 字段就否定续接能力
  - 不得用正文猜测值/文件名/标题充当 resume
ABSENCE_PROOF:
  invalid:
    - "toolcall_result 中无 agent_id 字段"
    - "subagent 未自报 UUID"
    - "只有 subagent_type"
  valid:
    - "已检查 post-task system-reminder，仍未见 `Agent ID:`"
POST_TASK_ID_GATE:
  required_questions:
    - "是否看到了系统附带的 `Agent ID:` 提示"
    - "若看到了，UUID 原文是什么"
    - "已写入哪个锚点文件"
    - "若没看到，是否已写明 `当前不可判定`"
  forbid_before_answered:
    - 连续性结论
    - 续接成功/失败结论
    - 测试闭合声明
```

## 四、最小回填规则

```yaml
SINKS_REQUIRED:
  mandatory:
    - ".trae/documents/*"
  plus_one:
    - "note"
    - "current-note.md"
    - "plan_ledger"
    - "independent_evidence_md"
  if_spec_active:
    - "spec 三件套中的 tasks.md"
FIELDS_MIN:
  subagent_type: "parallel-sub-agent | general_purpose_task | GN-004"
  description: "本次 Task 的 description"
  actual_agent_id: "系统提示里的 UUID"
  source: "Task 工具结束后的系统附带 Agent ID 提示"
  purpose: "本次 subagent 的任务目的"
  second_location: "第二落点路径"
  status: "待续接 | 已续接 | 仅记录不续接 | 丢失"
WRITE_TIME:
  - "首次看到真实 Agent ID -> 立即回填"
  - "resume 成功 -> 补写同一 Agent ID"
  - "未续接/ID丢失/无系统提示 -> 如实写原因"
WRITE_RULE:
  - "一旦看到 UUID，不得先总结后补写"
  - "未写入 `.trae/documents/*` 前，不得宣称记录完成"
  - "若当前存在 spec 三件套，必须同步回填 tasks.md"
MANDATORY_CAPTURE:
  if_seen_agent_id:
    - "必须逐字抄录完整 `Agent ID: ...` 行或完整 UUID"
    - "必须逐字写入锚点文件"
    - "未逐字抄录 -> 视为未完成识别"
```

## 五、最小范例

首次调用：

```json
{
  "description": "第一次任务",
  "query": "执行你的任务内容",
  "subagent_type": "parallel-sub-agent",
  "response_language": "中文"
}
```

系统提示：

```text
Agent ID: <UUID> (can be used with the `resume` parameter to send a follow-up)
```

回填记录：

```yaml
description: "特色发言测试"
subagent_type: "parallel-sub-agent"
actual_agent_id: "1a3c3142-d50a-472b-a7cc-c200d06385fa"
status: "待续接"
```

续接同一 agent：

```json
{
  "description": "继续第一次任务",
  "query": "继续上一轮未完成的内容，或回忆上一轮说过的话",
  "subagent_type": "parallel-sub-agent",
  "response_language": "中文",
  "resume": "1a3c3142-d50a-472b-a7cc-c200d06385fa"
}
```

错误新建：

```json
{
  "description": "第二次再问一次",
  "query": "请回忆第一次的内容",
  "subagent_type": "parallel-sub-agent",
  "response_language": "中文"
}
```

判定：

- `resume` 存在且等于 `actual_agent_id` -> 同一 agent
- 无 `resume` -> 新 agent
- 错误新建后“不记得” -> 只能证明新实例，不得否定续接机制

## 六、失败处理

```yaml
LEDGER_APPEND:
  - subagent_type
  - actual_agent_id
  - 第二落点
  - 状态
  - resume_used
  - previous_agent_id
  - resume_result
NOTE_MIN:
  - 首次拉起/续接
  - Agent ID 来源
  - 是否已回填第二落点
  - 失败卡点: 无系统提示 | 无记录 UUID | 误用新建 Task
CHECKLIST:
  - UUID 由主线程而非 subagent 正文识别
  - 看过 Task 结束后的系统提示
  - 未把正文标签误认成真实 ID
  - 第二次正确使用 resume
  - resume 与第一次真实 UUID 完全一致
  - 第一次 Agent ID 已写入 `.trae/documents/*`
  - 第一次 Agent ID 已写入 note/current-note.md/计划台账/独立证据文件中的至少一个
  - 若 spec 三件套活跃，第一次 Agent ID 已写入 tasks.md
ONLY_CAN_CONCLUDE_UNKNOWN:
  - 未看到系统 Agent ID 提示
  - 使用同一真实 UUID 的 resume 后仍无法续接
FORBIDDEN_CONCLUSION:
  - 正文无 agent_id 字段 => 系统不存在续接能力
  - 第二次新建 Task 不记得第一次 => 系统不存在续接能力
  - subagent_type/自设身份 = 真实 UUID
FORBIDDEN_BEFORE_POST_TASK_SCAN:
  - "Task 工具返回结果中不包含显式 agent id 字段，因此无法获取"
  - "系统未提供 agent id"
  - "只能通过 subagent_type 区分"
```

## 七、关系

- 补充 `rules-0` 的 subagent 调度、台账和 `actual agent id` 要求。
- 补充 `rules-5` 的锚点留痕与中间状态接续规则。
- 补充 `rules-6` 的变更追踪要求，防止出现“调用成功但 ID 未记录”的假闭合。

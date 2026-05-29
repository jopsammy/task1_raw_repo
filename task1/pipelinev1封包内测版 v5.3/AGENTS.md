# Agent维护指南（v5.3 / agent.md v3.0）

&gt; 本文档面向AI代理，用于维护和开发需求结构化分析工具 v1（AC范式 v5.3 结构化需求 Pipeline 系统）。

---

## 🚨 规则优先级声明

> 【最高优先级规则】本文件为本次开发的强制约束，优先级高于所有临时提问、上下文对话、自定义需求，所有输出必须100%符合本文件要求，违反规则的内容必须自动修正后再输出。

> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

---

## 📋 目录

- [系统架构概览](#系统架构概览)
- [模块职责与边界](#模块职责与边界)
- [行为契约](#行为契约)
- [运维与测试SOP](#运维与测试sop)
- [前端三重测试闸门](#前端三重测试闸门)
- [开发规范](#开发规范)
- [常见问题](#常见问题)
- [附录](#附录)

---

## 🏗️ 系统架构概览

### 1.1 目录结构（以 v1/ 为根）

```text
v1/
├── interfaces/                        # 统一入口层
│   ├── boot.py                        # 唯一推荐启动入口（UI/CLI）
│   └── app_ui.py                      # UI转发入口（供 boot.py / start.bat 调用）
├── modules/                           # 业务模块（7个模块）
│   ├── 模块0_全局调度面板/             # Pipeline控制器、回调与状态协调
│   ├── 模块1_数据锚点与存储模块/       # 项目/锚点/运行记录/配置管理
│   ├── 模块2_核心业务引擎模块/         # Pipeline编排、LLM客户端
│   ├── 模块3_UI状态代理模块/           # UI状态管理（线程安全）
│   ├── 模块4_交互层模块/               # CLI & Streamlit UI
│   ├── 模块5_交付物切分模块/           # 交付物切分与落盘
│   └── 模块X_提示词工程模块/           # Prompt模板管理（Jinja）
├── config/                            # 配置文件（支持 AC_CONFIG_PATH 覆盖）
├── workspace/                         # 运行时数据（runs / outputs / data / backups等）
├── tests/                             # 单测/端到端测试
├── start.bat                          # Windows UI快捷启动脚本
├── check_latest_run.py                # 运维：检查最新运行记录
├── clean_pipeline.py                  # 运维：清理/重置运行态
└── mock_cli_test.py                   # 运维：Rich组件/CLI输出快速自测
```

### 1.2 核心调用链路（双入口）

```text
interfaces/boot.py
  ├─ ui（默认）
  │    └─ subprocess: python -m streamlit run interfaces/app_ui.py
  │         └─ interfaces/app_ui.py
  │              └─ modules/模块4_交互层模块/streamlit/app.py
  │                   ├─ UI三态: INPUT -> MONITOR -> REVIEW
  │                   ├─ 状态代理: modules/模块3_UI状态代理模块/state_proxy.py
  │                   └─ Pipeline: modules/模块0_全局调度面板/pipeline_controller.py
  │                        ├─ 存储/运行记录: 模块1
  │                        ├─ 编排/LLM: 模块2
  │                        ├─ Prompt: 模块X
  │                        └─ 交付物落盘: 模块5
  └─ cli
       └─ 转发参数给: modules/模块4_交互层模块/cli/cli_handler.py
            └─ Pipeline: 模块0（同上）
```

---

## 📦 模块职责与边界

| 模块 | 核心职责 | 关键文件绑定 | 禁止行为（强制） |
|---|---|---|---|
| 模块0_全局调度面板 | Pipeline控制器、进度/日志回调、运行态协调、交付物触发 | `modules/模块0_全局调度面板/pipeline_controller.py` | 禁止把Prompt模板塞进模块0；禁止在模块0写UI渲染代码 |
| 模块1_数据锚点与存储模块 | 项目管理、需求锚点、运行记录、配置管理、数据读写 | `data_anchor_manager.py`, `run_record_manager.py`, `config_manager.py` | 禁止在日志/输出中泄露API Key；禁止写入不符合约定结构的数据 |
| 模块2_核心业务引擎模块 | Pipeline步骤编排、LLM调用与重试、结果聚合 | `pipeline_orchestrator.py`, `llm_client.py` | 禁止包含具体Prompt文本（应在模块X）；禁止直接做UI交互 |
| 模块3_UI状态代理模块 | UI状态机与线程安全状态更新（跨线程隔离） | `state_proxy.py` | 禁止业务线程直接写 `st.session_state`；禁止把业务编排逻辑塞进状态代理 |
| 模块4_交互层模块 | CLI与Streamlit UI渲染、用户输入、运行监控、结果审查 | `cli/cli_handler.py`, `cli/rich_console.py`, `streamlit/app.py`, `streamlit/mock_mode.py` | 禁止包含核心业务编排（应在模块0/2）；禁止绕过Rich输出规范 |
| 模块5_交付物切分模块 | 将Pipeline最终结果切分为可复用交付物并落盘 | `delivery_output_splitter.py` | 禁止直接调用LLM；禁止引入UI状态依赖 |
| 模块X_提示词工程模块 | Prompt模板管理、渲染、调试面板支撑 | `prompt_engine.py`, `prompts/*.jinja` | 禁止包含业务流程控制；禁止直接写磁盘（交给模块1/5） |

---

## ✅ 行为契约

### 3.1 统一启动契约（唯一推荐入口）

- 执行目录：所有命令均需在 `v1/` 目录下执行
- UI（默认）：`python interfaces/boot.py` 或 `python interfaces/boot.py ui`
- CLI（推荐）：`python interfaces/boot.py cli &lt;command&gt; [args...]`（参数会直接转发给 cli_handler）
- CLI（直连/调试）：`python modules/模块4_交互层模块/cli/cli_handler.py &lt;command&gt; [args...]`
- UI快捷方式：`start.bat` 仅作为Windows便捷脚本保留（不作为唯一入口描述源）

### 3.2 CLI行为契约

- 输出规范：CLI路径下禁止使用原生 `print` 进行用户可见输出；必须通过 `modules/模块4_交互层模块/cli/rich_console.py` 的 `get_rich_console()` 输出
- 进度控制：`run` 子命令必须支持 `--progress auto/plain/quiet`
- 结束汇总：正常结束时必须输出 Footer Summary（真实 token 统计 + provider 槽位映射）

### 3.3 CLI 示例

```bash
# 从文件运行Pipeline
python interfaces/boot.py cli run --file requirement.txt

# 从文本运行Pipeline
python interfaces/boot.py cli run --text "这是一个需求"

# 列出所有项目
python interfaces/boot.py cli list

# 查看运行记录
python interfaces/boot.py cli runs list
```

### 3.4 UI行为契约

- 三态架构：UI必须遵循 `INPUT -> MONITOR -> REVIEW` 的状态流转（对应 `UIMode.INPUT/MONITOR/REVIEW`）
- Mock模式：支持通过环境变量 `MOCK_DATA_DIR` 启动 Record&Replay 测试模式；可用 `MOCK_UI_MODE=REVIEW|INPUT` 控制是否直接进入审查态
- 状态管理：后台线程禁止直接写 `st.session_state`；跨线程状态更新必须通过状态代理/队列机制完成（模块3为唯一对外抽象）

### 3.5 数据落盘契约

- 运行记录：`workspace/runs/YYYYMMDD/<run_id>.json`（`run_id` 为 UUID）
- 交付物：`workspace/outputs/<project_id>/...`（按文件拆分：`structured_requirement.json`、`contracts.json`、`landing_plan.md/json`、`agent.md` 等）
- ID区分：
  - `project_id`：需求/项目维度的存档标识，未指定时由模块0自动生成：`{YYYYMMDD}_{6位hex}`
  - `run_id`：单次执行维度的运行标识（UUID），用于回放与审计

---

## 🔧 运维与测试SOP

### 4.1 运维脚本（从 v1/ 目录执行）

- 检查最新运行记录：`python check_latest_run.py`
- 清理/重置运行态：`python clean_pipeline.py`
- Rich组件/CLI输出自测：`python mock_cli_test.py`

### 4.2 测试命令

- 单元测试：`python -m pytest tests/unit/`
- 端到端测试：`python -m pytest tests/e2e/`
- 全量测试：`python -m pytest`

### 4.3 UI Mock 快速回归

```powershell
$env:MOCK_DATA_DIR="workspace/outputs/20260309_71f065"
$env:MOCK_UI_MODE="REVIEW"
python interfaces/boot.py ui
```

---

## � 前端三重测试闸门

&gt; 🚨 【强制原生行为】所有UI/前端改动必须通过三重测试闸门，缺一不可。此规则为Agent原生行为，自动触发。

### 6.1 闸门定义与触发

前端三重测试闸门（简称「三重闸」）是UI/前端类功能合流前的强制质量保障环节，包含三个连续的测试关卡，必须100%通过才能进入汇报/合流环节。

#### 强触发（必须走三重闸）
- 修改了**UI渲染路径下**的任何文件（例如 `modules/模块4_交互层模块/streamlit/`、`modules/模块4_交互层模块/cli/` 等）
- 新增/修改了**Streamlit组件/页面**（例如新增 `tab_xxx.py`、修改 `app.py` 等）
- 修改了**终端输出渲染逻辑**（例如修改 `rich_console.py` 等）
- 用户显式要求「测UI」、「测前端」、「跑闸门」

#### 弱触发（推荐走三重闸）
- 修改了**UI状态代理**（例如 `modules/模块3_UI状态代理模块/state_proxy.py`）
- 修改了**交付物切分/落盘**后UI展示
- 修改了**Mock模式**实现（例如 `modules/模块4_交互层模块/streamlit/mock_mode.py`）

### 6.2 三重闸关卡（按顺序执行）

| 关卡序号       | 关卡名称                  | 检查内容                                                     | 目标      |
| ---------- | --------------------- | -------------------------------------------------------- | ------- |
| **Test 1** | Streamlit Testing单元测试 | 基于streamlit-testing框架的组件级单元测试，覆盖核心交互逻辑                   | 组件级功能验证 |
| **Test 2** | Playwright E2E测试      | 基于Playwright的端到端测试，模拟真实用户操作流程                            | 全流程功能验证 |
| **Test 3** | Mock回归测试              | Mock模式下核心交互路径完整跑通（INPUT→MONITOR→REVIEW），关键按钮/组件可交互，无异常崩溃 | 回归验证    |

### 6.3 必须产物（证据链落盘）

三重闸执行后，必须在 `.trae/documents/test_reports/frontend_gate_YYYYMMDD_HHMMSS/` 目录下产生以下证据文件，**缺一不可**：

```
.trae/
└── documents/
    └── test_reports/
        └── frontend_gate_YYYYMMDD_HHMMSS/
            ├── test1_streamlit.log                # Test1单元测试输出
            ├── test2_playwright.log               # Test2 E2E测试输出
            ├── test3_mock_checklist.md            # Test3 Mock回归检查清单
            └── summary.json                        # 闸门汇总
```

### 6.4 阻断条件（任一失败禁止汇报/合流）

出现以下任一情况时，**必须立即阻断**，禁止继续执行后续操作、禁止向用户汇报「完成」、禁止执行合流：

| 阻断级别    | 条件                   | 示例                              |
| ------- | -------------------- | ------------------------------- |
| 🔴 完全阻断 | Test1 单元测试出现失败用例     | 组件测试失败、断言错误等                    |
| 🔴 完全阻断 | Test2 E2E测试出现失败用例    | 流程中断、元素未找到等                     |
| 🔴 完全阻断 | Test3 Mock回归测试出现异常崩溃 | Streamlit 闪退、Mock模式启动失败、核心路径走不通 |
| 🟡 条件阻断 | 测试出现警告级别问题           | 需要先评估并说明影响，经用户同意才能继续            |

### 6.5 Agent原生执行流程

当检测到触发条件时，Agent必须按以下顺序自动执行：

1. **立即调用** S305-前端三重测试闸门Skill
2. **等待** Skill执行完成并生成证据链
3. **验证** 所有证据文件存在且summary.json显示"PASSED"
4. **仅在全部通过后** 才允许继续后续操作

**【核心原则】** Agent**永远不应**跳过三重测试闸门，**永远不应**在闸门失败时宣称「完成」。

---

## 📝 开发规范

### 7.0 问题追踪规范

- 所有问题修复、功能优化、小调整，必须先在 `.trae/documents/` 下写分析/计划文档，再改代码
- 修复完成后必须在同一文档中补充：实际改动文件清单、测试结果、经验总结

### 7.1 路径处理规范

- 统一策略：以文件所在目录推导 `project_root`，再进行绝对路径拼接
- 禁止使用依赖当前工作目录的相对路径（例如 `../../config.json`）

### 7.2 配置与密钥规范

- 配置入口：默认 `config/config.json`，支持 `AC_CONFIG_PATH` 覆盖
- 禁止泄露：任何日志/输出/异常信息中禁止打印完整 `api_key`，如需展示仅允许脱敏（例如仅保留前3后2）

### 7.3 UI状态规范

- 固定 key：所有交互元素必须使用固定 key
- 线程隔离：后台线程不得直接读写 `st.session_state`，必须通过状态代理/共享状态队列同步

### 7.4 Prompt 归属规范

- Prompt模板仅允许存在于 `modules/模块X_提示词工程模块/prompts/*.jinja`
- 业务编排仅允许存在于 模块0/模块2，禁止提示词工程模块承担流程控制

### 7.5 AC范式通用约束（本项目对齐用）

- 如存在 `public/` 目录，则该目录视为只读（禁止直接修改）
- 模块间协作优先通过稳定接口/结构化数据契约，避免跨模块直接导入内部实现

---

## ❓ 常见问题

### Q1：模块导入失败/找不到 modules 怎么办？

- 优先使用 `python interfaces/boot.py ...` 启动（它会设置 `sys.path` 并以项目根目录运行）
- 若手动运行单文件，必须按项目内通用写法推导 `project_root` 并插入 `sys.path`

### Q2：UI刷新后状态丢失/后台线程警告怎么办？

- UI三态与结果缓存必须通过状态代理统一管理（模块3）
- 后台线程只写共享结构或队列，主线程在渲染前批处理同步到 `st.session_state`

### Q3：什么是 project_id 自动生成？

- 触发条件：启动Pipeline时未显式传入 `project_id`
- 格式：`{YYYYMMDD}_{6位hex}`（示例：`20260306_abc123`）
- 实现位置：
  - 模块0：`modules/模块0_全局调度面板/pipeline_controller.py` 的 `_save_delivery_outputs`
  - 模块5：`modules/模块5_交付物切分模块/delivery_output_splitter.py` 的 `split_and_save`

---

## 附录

### A. 关键文件路径映射

| 功能点 | 文件路径 |
|---|---|
| 统一启动入口 | `interfaces/boot.py` |
| UI入口转发 | `interfaces/app_ui.py` |
| CLI处理器 | `modules/模块4_交互层模块/cli/cli_handler.py` |
| Rich输出封装 | `modules/模块4_交互层模块/cli/rich_console.py` |
| Streamlit App | `modules/模块4_交互层模块/streamlit/app.py` |
| UI Mock 模式 | `modules/模块4_交互层模块/streamlit/mock_mode.py` |
| UI 状态代理 | `modules/模块3_UI状态代理模块/state_proxy.py` |
| Pipeline 控制器 | `modules/模块0_全局调度面板/pipeline_controller.py` |
| LLM 客户端 | `modules/模块2_核心业务引擎模块/llm_client.py` |
| Prompt 引擎 | `modules/模块X_提示词工程模块/prompt_engine.py` |

### B. 参考文档

- `AC范式体系v5.3_结构化需求Pipeline系统说明.md`
- `report_v1.md`
- `../ac构筑实践_v5.3.md`
- `../ac构筑范式思想_v5.3.md`
- `../AC范式公共规则库_v5.3.md`
- `../AC范式个人规则v5.3.md`
- `.trae/rules/0_orchestrator_guide.md`
- `.trae/rules/6_frontend_triple_test_gate.md`


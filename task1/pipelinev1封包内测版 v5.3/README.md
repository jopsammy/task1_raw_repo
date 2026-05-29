
# 需求结构化分析管道

&gt; 基于锚点契约式（AC）开发范式构建的需求结构化分析管道 (v5.2)

---

## 📋 目录

- [核心功能](#核心功能)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [项目结构](#项目结构)
- [常见问题](#常见问题)

---

## ✨ 核心功能

- 需求结构化分析与拆解
- 多LLM提供商支持（OpenAI、DeepSeek、豆包）
- 数据自动备份与版本管理
- 可视化交互界面（Streamlit）
- 模块化设计，易于扩展
- **AC范式V5.2提示词矩阵升级**：支持双场景原生适配（单IDE小项目/多IDE Agent矩阵）、分层规则体系、模块0中控能力、IDE原生规则绑定、异常自动处理
- **多阶段并行优化**：契约生成、落地方案生成、IDE引导包生成三个阶段并行执行，总耗时减少约50%
- **三态模态架构**：意图定义模态(INPUT)→执行监控模态(MONITOR)→成果审查模态(REVIEW)，实现沉浸式驾驶舱体验
- **流式日志展示**：摒弃Meta Refresh，采用Event Loop实现无刷新实时日志流
- 完整测试体系：Streamlit Testing单元测试 + Playwright E2E测试
- **Mock测试模式**：快速加载预存数据，跳过LLM调用，直接测试UI渲染效果
- **ViewModel Adapter 架构**：实现真实Pipeline输出与UI渲染契约的自动适配，保证数据展示一致性
- **Record & Replay 测试体系**：基于真实运行记录的Mock测试，避免自嗨式测试

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 依赖：见 `requirements.txt`

### 安装步骤

1. 进入项目目录
   ```bash
   cd v1
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境
   ```bash
   # 复制配置模板
   cp config/config_template.json config/config.json
   
   # 编辑 config.json，填入你的 API Key
   ```

4. 启动应用
   ```bash
   streamlit run interfaces/app_ui.py
   ```

5. Mock测试模式（快速测试UI）
   ```bash
   # 方法1：通过环境变量
   $env:MOCK_DATA_DIR="workspace/outputs/20260309_064355"
   streamlit run modules/模块4_交互层模块/streamlit/app.py
   
   # 方法2：通过命令行参数
   streamlit run modules/模块4_交互层模块/streamlit/app.py -- --mock-data-dir=workspace/outputs/20260309_064355
   ```
   
   > 💡 Mock模式说明：采用Record & Replay架构，加载真实Pipeline运行记录，与真实业务输出结构100%一致，避免自嗨式测试。

---

## ⚙️ 配置说明

### 配置文件位置

`config/config.json`

### 主要配置项

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| `llm.providers.openai.api_key` | OpenAI API Key | 无 |
| `llm.providers.deepseek.api_key` | DeepSeek API Key | 无 |
| `llm.providers.doubao.api_key` | 豆包 API Key | 无 |
| `llm.default_provider` | 默认使用的提供商 | `openai` |
| `workspace.root_dir` | 工作区根目录 | `workspace` |
| `storage.auto_backup` | 是否自动备份 | `true` |

---

## 📁 项目结构

```text
v1/
├── config/                          # 配置文件目录
│   ├── config.json                  # 主配置文件（不提交）
│   └── config_template.json         # 配置模板（提交）
├── modules/                         # 业务模块目录
│   ├── 模块0_全局调度面板/         # 全局调度与进度监控
│   ├── 模块1_数据锚点与存储模块/   # 数据读写与存储
│   ├── 模块2_核心业务引擎模块/     # 核心业务逻辑
│   ├── 模块3_UI状态代理模块/       # UI状态管理
│   ├── 模块4_交互层模块/           # 交互界面
│   └── 模块X_提示词工程模块/       # 提示词管理（独立核心）
├── public/                          # 公共资源区（只读）
│   ├── schema/                      # 数据契约
│   ├── interface_stub/              # 接口契约
│   ├── pre_generated_mock/          # 预生成Mock
│   ├── config_template/             # 配置模板
│   ├── dependencies/                # 依赖锁定
│   └── test_cases/                  # 通用测试用例
├── prompts/                         # 提示词模板目录
├── workspace/                       # 用户数据区
├── interfaces/                      # 入口层
├── requirements.txt                 # 依赖清单
└── README.md                        # 项目说明
```

---

## ❓ 常见问题

### Q: 如何获取 API Key？
A:
- OpenAI: 访问 https://platform.openai.com/
- DeepSeek: 访问 https://platform.deepseek.com/
- 豆包: 访问 https://www.volcengine.com/product/doubao

### Q: 配置文件在哪里？
A: 配置文件位于 `config/config.json`，首次使用请从 `config_template.json` 复制。

### Q: 如何备份数据？
A: 系统默认启用自动备份，备份文件保存在 `workspace/backups/` 目录下。

---

## 📚 相关文档

- [ac构筑实践_v3.md](../ac构筑实践_v3.md) - AC范式落地最佳实践
- [report_v1.md](report_v1.md) - 项目开发报告与更新日志

## 🔄 更新日志

### v3.2.0 - 2026-03-11
- **核心升级**：AGENTS.md 命名强约束改造（全大写，必须含 S；不允许出现 agent.md）
  - pipeline_orchestrator.py：ide_bundles key 从 `agent_md` → `agents_md`，日志文案从 "生成agent.md" → "生成AGENTS.md"
  - delivery_output_splitter.py：落盘文件名从 `agent.md` → `AGENTS.md`，deliveries key 从 `agent.md` → `AGENTS.md`
  - 提示词模板：global_ide_bundle.jinja、module_ide_bundle.jinja、agent_md_gen.jinja 统一引用 `AGENTS.md`
  - 测试断言：test_stage_renderers.py 所有断言只接受 `AGENTS.md`
  - 验证：验证脚本确认所有改造点正确，pipeline 产出文件统一为 `AGENTS.md`

### v3.1.0 - 2026-03-11
- **核心升级**：CLI Footer Summary 去硬编码并显示真实Token与槽位
  - 移除硬编码的 Token 数（154.2k）和模型名列表
  - 使用真实的 metrics.total_tokens/input_tokens/output_tokens
  - 显示真实的槽位名（provider_id），来源于运行记录的 llm_calls 聚合
  - 显示槽位→模型映射（格式：LLM1→doubao-seed-1-6-flash-250828 | LLM2→qwen3.5-plus）
  - 充分的兜底逻辑，数据缺失时正常显示
  - 验证：mock_cli_test.py 运行通过，所有测试场景正常

### v2.9.0 - 2026-03-11
- **核心修复**：UI第7轮修复（审查阶段4个展示异常 + Mock呈现彻底隐去）
  - 问题1：需求锚定Tab业务实体"暂无属性定义" - 实体属性"就地补全" + 呈现兜底
  - 问题2：架构迭代Tab方案对比矩阵字段空 - wrapper结构解析 + 决策要点矩阵差异化 + 对抗评审摘要
  - 问题3：可视化汇报Tab结构化ASCII流"极其简单" - 字段统一为ascii_* + 兜底可解释
  - 问题4：UI中彻底隐去Mock - 隐藏Mock指标/表格/字段/描述/下载关联
  - 所有修复均不修改Mock数据，只增强UI处理真实业务数据的能力
  - 验证：Mock模式所有Tab显示正常，决策要点矩阵三个方案差异化

### v1.5.2 - 2026-03-10
- **核心升级**：零侧边栏重构 + UI终端同步优化
  - 彻底移除侧边栏，单页应用架构，所有内容都在主区域Tabs中
  - 新增2个Tabs：项目管理、进度看板
  - UI和终端同步优化，3秒自动刷新确保实时同步
  - 移除不正确的time.sleep+st.rerun逻辑
  - 验证：无侧边栏，UI终端完全同步

### v1.5.4 - 2026-03-10
- **核心修复**：Mock模式UI显示问题全面修复
  - 修复侧边栏总耗时显示为0秒的问题
  - 修复左侧项目信息显示为"未加载项目"的问题
  - 修复需求锚定Tab的属性总数为0、核心业务逻辑/流程图/领域对象无显示的问题
  - 修复契约生成Tab的Mock文件数为0的问题
  - 修复可视化汇报Tab显示纯Mermaid语法而非渲染图表的问题
  - 修复IDE引导包页面总文件数为0、总大小为"-"、暂无可下载内容的问题
  - 重写MockDataManager，增强Mock数据生成，从实际文件中提取和转换数据结构
  - 修复时间计算和项目ID设置
  - 验证：Mock模式所有Tab显示正常，指标正确，图表正常渲染

### v1.8.1 - 2026-03-11
- **核心修复**：消除后台线程访问st.session_state的警告
  - 问题：真实业务运行时，后台线程调用state_proxy.store_pipeline_result()导致"missing ScriptRunContext"警告
  - 解决方案：采用线程安全队列异步处理状态更新
  - 在app.py中创建线程安全的状态更新队列
  - 修改回调逻辑，后台线程只将更新任务放入队列
  - 在主渲染循环的主线程中统一处理队列中的更新
  - 验证：警告完全消除，功能正常

### v1.8.0 - 2026-03-11
- **核心修复**：真实业务运行UI显示全为0问题修复
  - 深度分析：真实业务运行时，pipeline_controller的results没有同步到state_proxy.pipeline_results
  - 在pipeline_controller中添加_state_proxy_callback回调机制
  - 在app.py中初始化时设置回调
  - 在所有6个阶段完成后自动调用回调同步数据
  - 三重测试完整验证：streamlit.testing单元测试（16/16通过）+ e2e测试（6/6通过）+ Mock手动测试（全部正常）
  - 验证：真实业务运行和Mock模式行为一致，UI正常显示所有数据

### v1.7.0 - 2026-03-10
- **核心升级**：删除需求锚定Tab的Mermaid业务流程图，UI进一步简化
  - 删除需求锚定Tab的业务流程图渲染（普通人类没办法理解Mermaid）
  - 需求锚定Tab改为单列布局，只显示核心业务逻辑和领域对象表格
  - 可视化汇报Tab继续使用结构化ASCII流（本质是纯字符，零依赖）
  - 三重测试完整验证：streamlit.testing单元测试（16/16通过）+ e2e测试（6/6通过）+ Mock手动测试（全部正常）
  - 验证：UI更简洁，零渲染依赖，跨平台兼容

### v1.6.0 - 2026-03-10
- **核心升级**：放弃Mermaid，改用结构化ASCII流可视化，提升系统鲁棒性
  - 完全移除Mermaid相关代码和streamlit-mermaid依赖
  - 改用结构化ASCII流（本质是纯字符，零依赖，跨平台兼容）
  - 更新visualization_report.jinja提示词，改为ASCII流格式和强约束
  - 更新mock_mode.py，生成ASCII流数据
  - 更新ui_renderer.py，使用st.code()直接显示纯字符
  - 三重测试完整验证：streamlit.testing单元测试（16/16通过）+ e2e测试（6/6通过）+ Mock手动测试（全部正常）
  - 验证：系统鲁棒性显著提升，零渲染依赖，跨平台兼容

### v1.5.6 - 2026-03-10
- **核心修复**：Mock模式UI显示问题三次修复 + 三重测试完整验证
  - 修复需求锚定Tab属性总数仍为0问题（优化指标提取函数，优先使用标准格式）
  - 修复总耗时仍为0问题（确保controller.start_time和end_time正确设置）
  - 修复Mermaid图表显示全是空白问题（简化Mermaid语法，添加多层fallback机制）
  - 修复契约生成Tab的Mock文件数仍为0问题（优先使用标准格式提取指标）
  - 修复左侧状态栏的项目信息栏显示路径地址问题（使用Path(mock_dir).name提取项目ID）
  - 三重测试完整验证：streamlit.testing单元测试（16/16通过）+ e2e测试（6/6通过）+ Mock手动测试（全部正常）
  - 验证：Mock模式下所有Tab显示正常，所有指标正确

### v1.5.5 - 2026-03-10
- **核心修复**：Mock模式UI显示问题二次修复 + streamlit-mermaid集成 + 三重测试验证
  - 修复侧边栏总耗时仍显示0秒的问题（state_proxy.get_elapsed_time优先使用controller时间）
  - 修复需求锚定Tab属性总数为0和领域对象"暂无属性定义"问题
  - 引入streamlit-mermaid组件，替换st.markdown的Mermaid渲染，图表正常显示
  - 修复需求校验Tab永远显示"暂无校验结果"问题
  - 修复契约生成Tab Mock文件数仍为0问题
  - 修复落地方案Tab显示"暂无方案内容"问题
  - 三重测试验证：streamlit.testing单元测试（16/16通过）+ e2e测试（6/6通过）+ Mock手动测试（全部正常）
  - 验证：Mock模式下所有Tab显示正常，Mermaid图表正确渲染

### v1.5.4 - 2026-03-10
- **核心修复**：Mock模式UI显示问题全面修复
  - 重写mock_mode.py，增强Mock数据生成，生成完整数据结构
  - 修复侧边栏总耗时显示为0秒问题
  - 修复左侧项目信息显示为"未加载项目"问题
  - 修复需求锚定Tab的属性总数为0、核心业务逻辑/流程图/领域对象不显示问题
  - 修复契约生成Tab的Mock文件数为0问题
  - 修复可视化汇报Tab的Mermaid语法直接显示问题（去除```包裹）
  - 修复IDE引导包页面的总文件数为0、暂无可下载内容问题
  - 验证：Mock模式下所有Tab显示正常

### v1.5.3 - 2026-03-10
- **核心修复**：UI指标显示问题修复 + Mock测试模式实现
  - 修复Token消耗显示为0的问题
  - 修复需求锚定、需求校验、契约生成、落地方案、IDE引导包等Tab指标显示为0的问题
  - 实现Mock测试模式，支持快速加载预存数据测试UI渲染效果
  - 修复后台线程访问st.session_state导致的线程安全问题
  - 验证：所有UI指标显示正常，Mock测试模式功能完整

### v1.5.1 - 2026-03-10
- **核心升级**：UI与终端体验优化
  - 修复Streamlit弃用警告（use_container_width、空label问题）
  - Pipeline执行改为后台线程，UI保持响应
  - 实时进度展示，显示当前阶段、进度百分比和实时日志
  - 日志面板自动滚动更新
  - UI模式终端输出与CLI一致，终止操作无额外警告
  - 验证：启动无警告，所有功能正常工作

### v1.5.0 - 2026-03-09
- **核心升级**：多阶段并行优化 - 总耗时减少约50%
  - 契约生成阶段：接口契约、数据契约、Mock实现并行执行
  - 落地方案生成阶段：MD格式、JSON格式并行执行
  - IDE引导包生成阶段：全局引导包、所有模块引导包并行执行
  - 支持0个模块场景（极简需求）和多个模块场景（完整需求）
  - 使用threading.Lock()保证线程安全
  - 测试验证：2次完整业务测试，总耗时从2028秒减少到1041秒，提升49%
  - 验证：所有交付物完整正确，终端输出正常

### v1.4.1 - 2026-03-09
- **优化**：Footer Summary 排版优化 + 新增模拟测试脚本
  - Footer Summary 从单行改为多行面板式展示，更美观易读
  - 新增 `mock_cli_test.py` 快速测试脚本，10秒完成 Pipeline 模拟测试
  - 支持三种进度模式测试：auto/plain/quiet
  - 无需调用真实 LLM，无需等待和 API 费用
  - 验证：模拟测试正常工作，所有原 CLI 功能不受影响

### v1.4.0 - 2026-03-09
- **升级**：CLI &amp; UI 极致体验升级 - 数据追踪层与交互层增强
  - PipelineController 新增 Token 统计字段（total_tokens/input_tokens/output_tokens）
  - 新增 metrics 回调机制，支持实时指标展示
  - 新增 `_normalize_usage()` 方法用于 Token 统计归一化
  - 新增 `--progress` 参数（auto/plain/quiet 三种模式）
  - 新增 `live_display()` 上下文管理器
  - 新增测试记录文档：.trae/documents/CLI真实业务测试记录.md
  - 验证：真实业务测试正在顺利进行中（Pipeline 执行至 50%）

### v1.3.3 - 2026-03-09
- **修复**：修复进度条实时更新与品牌信息
  - 添加进度回调机制，实现进度条实时更新（从PipelineController到CLI）
  - 更新项目名称为"需求结构化分析管道"
  - 更新版本号为v5.2
  - 修改文件：pipeline_controller.py、cli_handler.py、rich_console.py、boot.py
  - 验证：进度条从10% → 30% → 50% → 80% → 90% → 98% → 100% 平滑推进

### v1.3.2 - 2026-03-09
- **升级**：提升 Pipeline 健壮性，修复 JSON 解析问题，添加 fallback 机制
  - 增强 _parse_llm_json_output 方法，添加健壮的 JSON 解析
  - 支持寻找最大的完整 JSON 对象，处理部分格式错误的情况
  - 解决 "Unterminated string" 等常见 JSON 解析错误
  - 添加全局/模块引导包生成失败的 fallback 机制
  - 增强报错记录，方便排查问题
  - 验证：完整Pipeline执行成功，生成 5 个模块引导包

### v1.3.1 - 2026-03-09
- **修复**：修复路径问题和多模块引导包生成问题
  - 修复运行记录和输出文件的路径推导，正确指向 v1/workspace
  - 修复 final_solution 解析逻辑，正确处理 raw_content 包裹
  - 修复 modules 提取逻辑，成功生成多个模块的引导包
  - 验证：完整Pipeline执行成功，生成 4 个模块引导包

### v1.3.0 - 2026-03-09
- **升级**：补充 LANDING_PLAN_GENERATION 阶段，完善变量传递链路
  - 新增落地方案生成阶段（在契约生成后、IDE引导包生成前）
  - 新增 run_landing_plan_generation() 方法
  - 完善变量传递链路（landing_plan、structured_requirement、modules、project_info）
  - 调整进度百分比分配和回滚阶段列表

### v1.2.1 - 2026-03-09
- **修复**：修复 ide_bundle_generation 阶段 jinja 模板变量报错问题
  - 移除模板中对未传递变量的引用
  - 清理未完成的新增代码

详见 [report_v1.md](report_v1.md)

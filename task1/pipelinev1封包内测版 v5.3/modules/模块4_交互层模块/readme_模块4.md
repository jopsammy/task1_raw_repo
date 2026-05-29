# 模块4：交互层模块

&gt; 提供Streamlit UI和CLI两种交互方式

---

## 📋 目录

- [模块职责](#模块职责)
- [核心功能](#核心功能)
- [三态模态架构](#三态模态架构)
- [Streamlit UI](#streamlit-ui)
- [CLI入口](#cli入口)
- [使用说明](#使用说明)
- [依赖关系](#依赖关系)

---

## 🎯 模块职责

| 职责 | 说明 |
|------|------|
| **Streamlit UI** | 提供可视化界面 |
| **CLI入口** | 提供命令行接口 |
| **三态模态管理** | INPUT/MONITOR/REVIEW三态切换 |
| **需求锚定阶段UI** | 需求输入和Pipeline启动 |
| **执行监控阶段UI** | 实时日志流、进度条、阶段导航 |
| **成果审查阶段UI** | 结果展示、Tab切换 |
| **提示词调试面板** | 提示词编辑和测试（核心功能） |

---

## ✨ 核心功能

### 三态模态架构（v2.0新增）

| 模态 | 说明 | 界面 |
|------|------|------|
| **INPUT** | 意图定义模态，人类主导 | 需求锚定台 |
| **MONITOR** | 执行监控模态，机器主导 | 全息监控屏 |
| **REVIEW** | 成果审查模态，人机交互 | 架构审查台 |

### Streamlit UI

| 模态 | 功能 |
|------|------|
| 🎯 需求锚定台 | 需求输入、配置选项、启动按钮 |
| 🔵 执行监控屏 | 阶段进度条、实时日志流、停止按钮 |
| ✅ 成果审查台 | 结果Tab展示、重新开始按钮 |

### CLI

| 命令 | 功能 |
|------|------|
| `create` | 创建新项目 |
| `list` | 列出所有项目 |
| `run` | 运行Pipeline |
| `status` | 显示Pipeline状态 |
| `logs` | 显示Pipeline日志 |

### 终端输出对齐功能

| 功能 | 说明 |
|------|------|
| **彩色日志渲染** | INFO蓝/SUCCESS绿/WARNING黄/ERROR红 |
| **进度条显示** | 阶段进度可视化，实时更新 |
| **Footer摘要显示** | 执行完成后显示统计摘要 |

### 成果审查台视觉重构（v2.3.0新增）

#### 信息三层漏斗架构

| 层级 | 说明 | 组件 |
|------|------|------|
| **L1 指标层** | 关键统计指标 | st.metric |
| **L2 人类视图层** | 可视化展示 | Mermaid流程图、API浏览器、数据模型树 |
| **L3 原始存根层** | 原始数据收纳 | st.expander（默认折叠） |

#### 特征识别路由器

自动检测数据特征，智能选择渲染方式：

| 特征 | 渲染方式 |
|------|----------|
| flow/entities | Mermaid 业务流程图 |
| interfaces/api | API 浏览器风格列表 |
| schema/properties | 数据模型树 |
| solutions | 三方案对比矩阵 |
| contracts | 契约展示卡片 |

#### 阶段专属渲染器

| 阶段 | 渲染特性 |
|------|----------|
| 需求锚定 | 业务逻辑摘要 + Mermaid 流程图 + 领域对象表格 |
| 架构迭代 | 三方案对比矩阵 + 最终决策高亮区 |
| 契约生成 | API 浏览器风格列表 + 数据模型树 |
| 需求校验 | 通过/警告/错误分级展示 |
| 落地方案 | Markdown 内容 + 模块拆分详情 |
| IDE 引导包 | 文件清单表格 + 下载功能 |

## 🔄 模块更新日志

### v3.1.0 - 2026-03-11
- **核心升级**：CLI Footer Summary 去硬编码并显示真实Token与槽位
  - 移除硬编码的 Token 数（154.2k）和模型名列表
  - 使用真实的 metrics.total_tokens/input_tokens/output_tokens
  - 显示真实的槽位名（provider_id），来源于运行记录的 llm_calls 聚合
  - 显示槽位→模型映射（格式：LLM1→doubao-seed-1-6-flash-250828 | LLM2→qwen3.5-plus）
  - 充分的兜底逻辑，数据缺失时正常显示
  - 验证：mock_cli_test.py 运行通过，所有测试场景正常
  - 详见：[.trae/documents/CLI_Footer_Summary_去硬编码并显示真实Token与槽位完成记录.md](../.trae/documents/CLI_Footer_Summary_去硬编码并显示真实Token与槽位完成记录.md)
  - 规范文档：[.trae/specs/cli-footer-summary-upgrade/](../.trae/specs/cli-footer-summary-upgrade/)

### v3.0.0 - 2026-03-11
- **核心升级**：UI第7轮修复（审查阶段4个展示异常 + Mock呈现彻底隐去）
  - 修复 `mock_llm_client.py` 暴露问题：在 UI 调用中直接出现 Mock API 调用信息
  - 修复：当 config.json 中 providers 为空时，页面直接挂掉异常
  - 修复：审查阶段"第X轮"计数显示错误问题（一直显示"第1轮"）
  - 修复：审查阶段历史记录丢失问题（每次点击"下一轮"都丢失上一轮）
  - 修复：审查阶段"审查通过"和"继续审查"按钮状态不一致问题
  - 详见：[.trae/documents/UI第7轮修复-审查阶段4个展示异常+Mock呈现彻底隐去.md](../.trae/documents/UI第7轮修复-审查阶段4个展示异常+Mock呈现彻底隐去.md)

### v2.3.0 - 2026-03-10
- 成果审查台视觉重构（信息三层漏斗、特征识别路由器、阶段专属渲染器）

### v2.2.0 - 2026-03-10
- 后台线程安全修复（共享数据结构替代直接访问st.session_state）

### v2.0.0 - 2026-03-10
- 三态模态架构重构（INPUT/MONITOR/REVIEW）+ 流式日志展示

### v1.4.2 - 2026-03-10
- 修复WebUI模块引导包生成解析路径问题

### v1.4.0 - 2026-03-10
- 终端输出对齐（彩色日志、进度条、Footer摘要）+ 自动化测试

---

## 🔄 三态模态架构

### 设计理念

基于AC范式"人机协同"理念，将UI分为三个互斥模态：

1. **意图定义模态(INPUT)**
   - 人类主导，专注输入需求
   - 界面：需求锚定台
   - 操作：输入需求、选择配置、启动Pipeline

2. **执行监控模态(MONITOR)**
   - 机器主导，人类监督
   - 界面：全息监控屏
   - 操作：查看实时日志、监控进度、停止Pipeline

3. **成果审查模态(REVIEW)**
   - 人机交互，展示结果
   - 界面：架构审查台
   - 操作：查看结果、切换Tab、重新开始

### 状态机管理

```python
class UIMode(Enum):
    INPUT = "input"    # 意图定义
    MONITOR = "monitor" # 执行监控
    REVIEW = "review"   # 成果审查
```

### 模态切换规则

| 当前模态 | 触发条件 | 目标模态 |
|---------|---------|---------|
| INPUT | 点击启动按钮 | MONITOR |
| MONITOR | Pipeline完成/失败 | REVIEW |
| MONITOR | 点击停止按钮 | REVIEW |
| REVIEW | 点击重新开始 | INPUT |

### 线程安全设计（v2.2新增）

后台线程与主线程通过共享数据结构通信：

```python
_pipeline_shared_state = {}
_pipeline_shared_state_lock = threading.Lock()
```

- 后台线程：只更新共享数据结构
- 主线程：检查共享状态并执行UI操作

---

## 🎨 Streamlit UI

### 侧边栏全局控制

- 模态状态指示器（空闲/运行中/已完成）
- 资源监控（Token消耗、耗时统计）
- 启动/停止/重新开始按钮（根据模态显示）
- 项目信息卡片
- **API管理**（新增v3.0.0）：3行API配置（URL/Key/模型）、保存配置按钮、运行时禁用

### 主区域界面

#### 1. 需求锚定台（INPUT模态）
- 需求文本输入框
- 配置选项（LLM提供商、模型名称）
- 字符数统计

#### 2. 执行监控屏（MONITOR模态）
- 阶段进度条（6个阶段可视化）
- 实时日志流（终端风格展示）
- 自动刷新（每秒）

#### 3. 架构审查台（REVIEW模态）
- 结果Tab展示
- 各阶段结果详情
- 接口契约
- 数据契约
- Mock实现

#### 4. 引导包生成Tab
- agent.md展示
- IDE引导包展示

#### 5. 提示词调试Tab（核心功能）
- 模板选择
- 上下文JSON输入
- 系统提示词编辑
- 用户提示词编辑
- 测试按钮
- 结果展示

---

## 💻 CLI入口

### 安装依赖

```bash
pip install -r requirements.txt
```

### 创建项目

```bash
python cli_handler.py create --name "我的项目"
```

### 列出项目

```bash
python cli_handler.py list
```

### 运行Pipeline

```bash
# 从文本运行
python cli_handler.py run --text "这是一个需求" --project 20260301_123456

# 从文件运行
python cli_handler.py run --file requirement.txt --output result.json
```

### 查看状态

```bash
python cli_handler.py status
```

### 查看日志

```bash
# 查看最近100条日志
python cli_handler.py logs

# 查看最近50条日志
python cli_handler.py logs --limit 50

# 只看INFO级别日志
python cli_handler.py logs --level INFO
```

---

## 📖 使用说明

### 启动Streamlit UI

```bash
cd v1
streamlit run interfaces/app_ui.py
```

### 使用CLI

```bash
cd v1
python modules/模块4_交互层模块/cli/cli_handler.py --help
```

---

## 🔗 依赖关系

```
模块4_交互层模块
  ├── 模块0_全局调度面板
  ├── 模块1_数据锚点与存储模块
  ├── 模块3_UI状态代理模块
  └── 模块X_提示词工程模块
```

---

## 📁 文件结构

```
模块4_交互层模块/
├── streamlit/
│   └── app.py                 # Streamlit UI
├── cli/
│   └── cli_handler.py         # CLI入口
├── readme_模块4.md            # 本文档
└── 模块4落地开发文档.md       # 开发文档
```

---

## 🧪 测试运行说明

### 单元测试

```bash
pytest tests/unit/
```

### E2E测试

```bash
pytest tests/e2e/
```

### 测试覆盖率

| 测试类型 | 数量 |
|---------|------|
| 单元测试 | 169个 |
| E2E测试 | 30个 |

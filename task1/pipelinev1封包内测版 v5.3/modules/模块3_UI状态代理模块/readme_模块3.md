# 模块3：UI状态代理模块

&gt; 负责会话状态管理、pipeline进度跟踪、状态持久化

---

## 📋 目录

- [模块职责](#模块职责)
- [核心功能](#核心功能)
- [使用说明](#使用说明)
- [API参考](#api参考)
- [依赖关系](#依赖关系)

---

## 🎯 模块职责

| 职责 | 说明 |
|------|------|
| **会话状态管理** | 管理Streamlit session_state与底层数据的同步 |
| **Pipeline进度跟踪** | 跟踪Pipeline执行状态、进度、日志 |
| **状态持久化** | 支持状态的保存和加载 |
| **提示词调试状态** | 管理提示词调试面板的状态 |

---

## ✨ 核心功能

### 1. 项目数据管理
- 加载项目数据到session_state
- 保存session_state中的项目数据
- 脏数据标记与同步

### 2. Pipeline状态管理
- Pipeline状态跟踪（IDLE/RUNNING/PAUSED/COMPLETED/FAILED）
- 进度更新（0-100%）
- 日志记录与查询
- 阶段结果存储

### 3. 提示词调试面板状态
- 模板ID、上下文JSON管理
- 系统提示词、用户提示词管理
- 调试结果存储

### 4. 状态持久化
- 状态保存到JSON文件
- 从JSON文件加载状态

---

## 📖 使用说明

### 初始化

```python
from modules.模块3_UI状态代理模块.state_proxy import get_state_proxy
from modules.模块1_数据锚点与存储模块.data_anchor_manager import DataAnchorManager

data_manager = DataAnchorManager()
state_proxy = get_state_proxy(data_manager)
```

### 项目管理

```python
# 加载项目
state_proxy.load_project("20260301_123456")

# 保存项目
state_proxy.save_project()

# 标记脏数据
state_proxy.mark_dirty("requirements")
```

### Pipeline管理

```python
from modules.模块3_UI状态代理模块.state_proxy import PipelineStatus

# 更新Pipeline状态
state_proxy.update_pipeline_status(
    status=PipelineStatus.RUNNING,
    stage="需求锚定",
    progress=30,
    log_message="开始需求锚定阶段"
)

# 添加日志
state_proxy.add_pipeline_log("需求锚定完成", level="SUCCESS")

# 获取Pipeline状态
status = state_proxy.get_pipeline_status()
```

### 提示词调试

```python
# 更新调试状态
state_proxy.update_prompt_debug(
    template_id="requirement_structuring",
    context='{"requirement_text": "这是一个测试需求"}',
    system_prompt="你是一个需求分析师...",
    user_prompt="请分析以下需求：...",
    result="LLM返回结果..."
)

# 获取调试状态
debug_state = state_proxy.get_prompt_debug_state()
```

### 状态持久化

```python
# 保存状态
state_proxy.persist_state("workspace/state_backup.json")

# 加载状态
state_proxy.load_persisted_state("workspace/state_backup.json")
```

---

## 🔧 API参考

### StateProxy 类

| 方法 | 说明 |
|------|------|
| `load_project(project_id: str) -&gt; bool` | 加载项目数据 |
| `save_project() -&gt; bool` | 保存项目数据 |
| `mark_dirty(key: str)` | 标记脏数据 |
| `update_pipeline_status(status, stage, progress, log_message)` | 更新Pipeline状态 |
| `add_pipeline_log(message, level)` | 添加Pipeline日志 |
| `get_pipeline_status() -&gt; Dict` | 获取Pipeline状态 |
| `store_pipeline_result(stage, result)` | 存储Pipeline阶段结果 |
| `get_pipeline_result(stage)` | 获取Pipeline阶段结果 |
| `update_prompt_debug(...)` | 更新提示词调试状态 |
| `get_prompt_debug_state() -&gt; Dict` | 获取提示词调试状态 |
| `persist_state(file_path) -&gt; bool` | 持久化状态 |
| `load_persisted_state(file_path) -&gt; bool` | 加载持久化状态 |

### PipelineStatus 枚举

| 状态 | 说明 |
|------|------|
| `IDLE` | 空闲 |
| `RUNNING` | 运行中 |
| `PAUSED` | 已暂停 |
| `COMPLETED` | 已完成 |
| `FAILED` | 失败 |

---

## 🔗 依赖关系

```
模块3_UI状态代理模块
  ├── 模块1_数据锚点与存储模块 (可选)
  └── 模块2_核心业务引擎模块 (可选)
```

---

## 📁 文件结构

```
模块3_UI状态代理模块/
├── state_proxy.py          # 核心实现
├── readme_模块3.md         # 本文档
└── 模块3落地开发文档.md    # 开发文档
```

# 模块0：全局调度面板

&gt; 负责pipeline流程编排、进度监控、暂停/继续/回滚

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
| **Pipeline流程编排** | 按顺序执行5个阶段的Pipeline |
| **进度监控** | 实时跟踪Pipeline执行状态和进度 |
| **暂停/继续** | 支持Pipeline的暂停和继续 |
| **停止** | 支持Pipeline的强制停止 |
| **回滚** | 支持回滚到指定阶段 |
| **日志管理** | 记录Pipeline执行日志 |

---

## ✨ 核心功能

### 1. Pipeline执行
- 需求锚定阶段
- 需求校验阶段
- 架构迭代阶段
- 契约生成阶段
- IDE引导包生成阶段

### 2. 控制操作
- 启动Pipeline
- 暂停Pipeline
- 继续Pipeline
- 停止Pipeline
- 回滚到指定阶段

### 3. 状态查询
- 获取当前状态
- 获取执行日志
- 获取阶段结果
- 获取进度信息

---

## 📖 使用说明

### 初始化

```python
from modules.模块0_全局调度面板.pipeline_controller import get_pipeline_controller

controller = get_pipeline_controller()
```

### 启动Pipeline

```python
result = controller.start_pipeline(
    requirement_text="这是一个测试需求...",
    project_id="20260301_123456"  # 可选，如果不提供会自动生成
)

if result["success"]:
    print("Pipeline执行成功！")
    print(f"耗时: {result['duration_seconds']}秒")
    print(f"项目ID: {result['project_id']}")
else:
    print(f"Pipeline失败: {result['error']}")
```

### project_id自动生成

当未提供`project_id`时，系统会自动生成一个唯一ID，格式为：`{YYYYMMDD}_{随机6位十六进制}`。例如：`20260306_abc123`。

**生成逻辑**：
- 日期部分：当前系统日期，格式为YYYYMMDD
- 随机部分：6位十六进制随机字符串，确保唯一性

**使用场景**：
- UI界面运行时，用户未指定project_id
- 命令行快速测试时
- 任何需要自动生成唯一标识的场景

### 暂停/继续/停止

```python
# 暂停
controller.pause_pipeline()

# 继续
controller.resume_pipeline()

# 停止
controller.stop_pipeline()
```

### 回滚

```python
from modules.模块2_核心业务引擎模块.pipeline_orchestrator import PipelineStage

result = controller.rollback_to_stage(PipelineStage.REQUIREMENT_VALIDATION.value)
if result["success"]:
    print(f"已回滚到阶段: {result['current_stage']}")
```

### 查询状态

```python
# 获取状态
status = controller.get_status()
print(f"状态: {status['status']}")
print(f"进度: {status['progress']}%")
print(f"当前阶段: {status['current_stage']}")

# 获取日志
logs = controller.get_logs(limit=50)
for log in logs:
    print(f"[{log['level']}] {log['message']}")

# 获取结果
results = controller.get_results()
print(f"完成阶段数: {len(results)}")
```

---

## 🔧 API参考

### PipelineController 类

| 方法 | 说明 |
|------|------|
| `start_pipeline(requirement_text, project_id)` | 启动Pipeline |
| `pause_pipeline() -&gt; bool` | 暂停Pipeline |
| `resume_pipeline() -&gt; bool` | 继续Pipeline |
| `stop_pipeline() -&gt; bool` | 停止Pipeline |
| `rollback_to_stage(stage) -&gt; Dict` | 回滚到指定阶段 |
| `get_status() -&gt; Dict` | 获取控制器状态 |
| `get_logs(limit, level) -&gt; List` | 获取日志 |
| `get_results() -&gt; Dict` | 获取所有阶段结果 |
| `get_result(stage) -&gt; Optional[Dict]` | 获取指定阶段结果 |
| `clear()` | 清空状态 |

### ControllerStatus 枚举

| 状态 | 说明 |
|------|------|
| `IDLE` | 空闲 |
| `RUNNING` | 运行中 |
| `PAUSED` | 已暂停 |
| `STOPPED` | 已停止 |

---

## 🔗 依赖关系

```
模块0_全局调度面板
  └── 模块2_核心业务引擎模块
```

---

## 📁 文件结构

```
模块0_全局调度面板/
├── pipeline_controller.py      # 核心实现
├── readme_模块0.md             # 本文档
└── 模块0落地开发文档.md        # 开发文档
```

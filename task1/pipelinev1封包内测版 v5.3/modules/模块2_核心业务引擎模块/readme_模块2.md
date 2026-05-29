# 模块2：核心业务引擎模块

&gt; 本模块是需求结构化分析工具的核心业务引擎，负责Pipeline编排、LLM调用、多LLM对抗等核心功能

---

## 📋 目录

- [模块概述](#模块概述)
- [核心功能](#核心功能)
- [文件说明](#文件说明)
- [接口文档](#接口文档)
- [使用示例](#使用示例)
- [维护指南](#维护指南)

---

## 🎯 模块概述

模块2是整个需求结构化分析工具的核心引擎，包含两大核心组件：

1. **LLM客户端** (`llm_client.py`) - 统一管理多LLM提供商（OpenAI、DeepSeek、豆包）的API调用
2. **Pipeline编排器** (`pipeline_orchestrator.py`) - 协调AC范式的5个阶段执行

---

## ✨ 核心功能

### LLM客户端
- 支持多LLM提供商（OpenAI、DeepSeek、豆包）
- 统一的API调用接口
- 自动重试机制
- 健康检查
- 降级策略
- 全局单例模式

### Pipeline编排器
- **需求锚定与校验引擎** - 阶段1+2：将原始需求结构化并校验
- **多LLM对抗方案迭代引擎** - 阶段3：多个LLM生成方案后融合（已有并行）
- **全局契约生成引擎** - 阶段4：生成接口契约、数据契约、Mock（已并行）
- **落地方案生成引擎** - 阶段5：生成MD格式和JSON格式落地方案（已并行）
- **IDE引导包生成引擎** - 阶段6：生成agent.md、全局IDE引导包和模块级IDE引导包（已并行）
- 完整的日志记录
- 阶段独立执行或全Pipeline执行
- **性能优化**：多阶段并行执行，总耗时减少约50%

---

## 📁 文件说明

| 文件名 | 说明 |
|--------|------|
| `llm_client.py` | LLM客户端，支持多提供商 |
| `pipeline_orchestrator.py` | Pipeline编排器，协调各阶段执行 |
| `readme_模块2.md` | 本文档 - 用户说明文档 |
| `模块2落地开发文档.md` | 详细开发文档（面向开发者） |

---

## 📝 版本更新记录

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.4.2 | 2026-03-10 | 修复 `run_ide_bundle_generation()` 模块提取逻辑，支持 `landing_plan` 被 `{"md":..., "json":...}` 包裹的情况 |
| v1.4.0 | 2026-03-10 | 多路径模块提取策略（3个备选路径）+ 增强调试日志 |
| v1.5.0 | 2026-03-09 | 多阶段并行优化，总耗时减少约50% |

---

## 🔧 接口文档

### LLM客户端

#### `get_llm_client(config_path: Optional[str] = None) -&gt; LLMClient`
获取LLM客户端单例

#### `LLMClient.call_llm(system_prompt: str, user_prompt: str, provider: Optional[str] = None, **kwargs) -&gt; Dict[str, Any]`
调用LLM，返回结果字典

#### `LLMClient.call_llm_with_fallback(system_prompt: str, user_prompt: str, providers: Optional[List[str]] = None, **kwargs) -&gt; Dict[str, Any]`
带降级的LLM调用，按优先级尝试多个提供商

#### `LLMClient.get_available_providers() -&gt; List[str]`
获取可用的提供商列表

#### `LLMClient.health_check_all() -&gt; Dict[str, bool]`
检查所有提供商的健康状态

---

### Pipeline编排器

#### `get_pipeline_orchestrator() -&gt; PipelineOrchestrator`
获取Pipeline编排器单例

#### `PipelineOrchestrator.run_requirement_anchoring(requirement_text: str, project_id: Optional[str] = None) -&gt; Dict[str, Any]`
阶段1：需求锚定与结构化

#### `PipelineOrchestrator.run_requirement_validation(structured_requirement: Dict[str, Any]) -&gt; Dict[str, Any]`
阶段2：需求校验与修正

#### `PipelineOrchestrator.run_architecture_iteration(validated_requirement: Dict[str, Any], num_llms: int = 3) -&gt; Dict[str, Any]`
阶段3：多LLM对抗方案迭代

#### `PipelineOrchestrator.run_contract_generation(final_solution: Dict[str, Any]) -&gt; Dict[str, Any]`
阶段4：全局契约生成

#### `PipelineOrchestrator.run_ide_bundle_generation(final_solution: Dict[str, Any], contracts: Dict[str, Any]) -&gt; Dict[str, Any]`
阶段5：IDE引导包生成

#### `PipelineOrchestrator.run_full_pipeline(requirement_text: str, project_id: Optional[str] = None) -&gt; Dict[str, Any]`
运行完整Pipeline（5个阶段依次执行）

#### `PipelineOrchestrator.get_logs() -&gt; List[Dict[str, Any]]`
获取Pipeline日志

---

## 💡 使用示例

### 示例1：使用LLM客户端

```python
from modules.模块2_核心业务引擎模块.llm_client import get_llm_client

llm_client = get_llm_client()

# 调用LLM
result = llm_client.call_llm(
    system_prompt="你是一个专业的需求分析师",
    user_prompt="请分析以下需求：..."
)

if result["success"]:
    print(result["content"])
else:
    print(f"错误：{result['error']}")

# 带降级调用
result = llm_client.call_llm_with_fallback(
    system_prompt="你是一个专业的需求分析师",
    user_prompt="请分析以下需求：...",
    providers=["deepseek", "openai", "doubao"]
)
```

### 示例2：使用Pipeline编排器

```python
from modules.模块2_核心业务引擎模块.pipeline_orchestrator import get_pipeline_orchestrator

orchestrator = get_pipeline_orchestrator()

# 运行完整Pipeline
requirement_text = "我要做一个待办事项应用，支持创建、编辑、删除任务..."
pipeline_result = orchestrator.run_full_pipeline(requirement_text)

if pipeline_result["success"]:
    print("Pipeline执行成功！")
    print(f"最终方案：{pipeline_result['stages']['architecture_iteration']['final_solution']}")
else:
    print(f"Pipeline失败：{pipeline_result['error']}")

# 查看日志
logs = orchestrator.get_logs()
for log in logs:
    print(f"[{log['level']}] {log['message']}")
```

### 示例3：单独执行某个阶段

```python
from modules.模块2_核心业务引擎模块.pipeline_orchestrator import get_pipeline_orchestrator

orchestrator = get_pipeline_orchestrator()

# 阶段1：需求锚定
stage1_result = orchestrator.run_requirement_anchoring("我的需求是...")
if not stage1_result["success"]:
    exit()

# 阶段2：需求校验
stage2_result = orchestrator.run_requirement_validation(stage1_result["structured_requirement"])
if not stage2_result["success"]:
    exit()

# 阶段3：架构迭代
stage3_result = orchestrator.run_architecture_iteration(stage2_result["validation_result"])
```

---

## 🔨 维护指南

### 添加新的LLM提供商

1. 在 `llm_client.py` 中继承 `LLMProvider` 抽象基类
2. 实现 `call()` 和 `health_check()` 方法
3. 在 `LLMClient._initialize_providers()` 中添加初始化逻辑
4. 在 `config/config_template.json` 中添加配置模板

### Pipeline阶段扩展

如需添加新的Pipeline阶段：

1. 在 `PipelineStage` 枚举中添加新的阶段
2. 在 `PipelineOrchestrator` 中添加 `run_xxx()` 方法
3. （可选）在 `run_full_pipeline()` 中集成新阶段

### 配置说明

配置文件位于 `config/config.json`：

```json
{
  "llm": {
    "providers": {
      "openai": {
        "api_key": "your-api-key",
        "api_base": "https://api.openai.com/v1",
        "model": "gpt-4-turbo",
        "timeout": 300,
        "max_retries": 3
      },
      "deepseek": {
        "api_key": "your-api-key",
        "api_base": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "timeout": 300,
        "max_retries": 3
      },
      "doubao": {
        "api_key": "your-api-key",
        "api_base": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "ep-20241225123456-xxxxx",
        "timeout": 300,
        "max_retries": 3
      }
    },
    "default_provider": "openai"
  }
}
```

---

## 📚 相关文档

- [v1落地方案规划.md](../../v1落地方案规划.md) - 整体架构
- [agent.md](../../agent.md) - 系统维护指南
- [AC范式生成pipeline流程图.md](../../../AC范式生成pipeline流程图.md) - Pipeline流程


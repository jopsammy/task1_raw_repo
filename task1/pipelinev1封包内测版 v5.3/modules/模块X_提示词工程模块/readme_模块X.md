# 模块X_提示词工程模块 - 使用说明与维护指南

&gt; 提示词工程模块是整个系统的「智能大脑」，所有LLM调用的提示词均由本模块统一管理和生成

---

## 📋 目录

- [模块概述](#模块概述)
- [核心功能](#核心功能)
- [快速开始](#快速开始)
- [API接口](#api接口)
- [模板管理](#模板管理)
- [维护指南](#维护指南)
- [常见问题](#常见问题)

---

## 📦 模块概述

| 项目 | 说明 |
|-----|------|
| **模块定位** | 整个系统的提示词管理中心 |
| **核心价值** | 提示词与业务逻辑解耦，支持独立迭代优化 |
| **文件位置** | `v1/modules/模块X_提示词工程模块/` |
| **依赖** | Jinja2（模板渲染） |
| **输出** | 结构化的提示词对象 |

---

## ✨ 核心功能

### 1. 提示词模板管理
- 支持Jinja2模板语法
- 模板热更新（文件修改自动重新加载）
- 模板缓存机制
- 元数据自动提取

### 2. 提示词动态生成
- 变量注入与验证
- 系统提示词与用户提示词分离
- 内容指纹生成（防重）
- 支持预览功能

### 3. 调试与预览
- 提示词预览功能
- 变量验证检查
- 元数据查看
- 模板内容获取

### 4. 内置模板库
| 模板ID | 用途 |
|-------|------|
| requirement_structuring | 需求结构化拆解 |
| requirement_validation | 需求质量校验 |
| architecture_solution_llm1 | 保守架构师方案 |
| architecture_solution_llm2 | 创新架构师方案 |
| architecture_solution_llm3 | 平衡架构师方案 |
| solution_fusion | 方案对比融合 |
| data_contract_gen | 数据契约生成 |
| interface_contract_gen | 接口契约生成 |
| agent_md_gen | AGENT.md生成 |
| mock_gen | Mock实现生成 |
| ide_bundle_gen | IDE引导包生成 |

---

## 🚀 快速开始

### 基础使用

```python
from prompt_engine import get_prompt_engine

# 获取引擎实例
engine = get_prompt_engine()

# 生成提示词
prompt = engine.generate_prompt(
    template_id="requirement_structuring",
    context={
        "requirement_text": "用户需要一个待办事项管理系统..."
    }
)

print(prompt["user_prompt"])
```

### 预览提示词

```python
# 预览渲染后的提示词（用于调试）
preview = engine.preview_prompt(
    template_id="requirement_structuring",
    context={
        "requirement_text": "用户需要一个待办事项管理系统..."
    }
)

print(preview)
```

### 列出所有模板

```python
# 列出所有模板
templates = engine.list_templates()
for t in templates:
    print(f"{t['template_id']} - {t['name']}")
```

---

## 🔧 API接口

### PromptEngine 类

#### `__init__(template_dir: Optional[str] = None)`

初始化提示词引擎

| 参数 | 类型 | 说明 |
|-----|------|------|
| template_dir | str \| None | 模板目录，None则使用默认位置 |

#### `get_template(template_id: str) -> Dict[str, Any]`

获取指定模板的完整信息

| 参数 | 类型 | 说明 |
|-----|------|------|
| template_id | str | 模板ID |

#### `list_templates(category: Optional[str] = None) -> List[Dict[str, Any]]`

列出所有可用模板

| 参数 | 类型 | 说明 |
|-----|------|------|
| category | str \| None | 分类过滤 |

#### `validate_variables(template_id: str, context: Dict[str, Any]) -> Dict[str, Any]`

验证模板变量是否完整

| 参数 | 类型 | 说明 |
|-----|------|------|
| template_id | str | 模板ID |
| context | dict | 变量上下文 |

#### `generate_prompt(template_id: str, context: Dict[str, Any], system_prompt: Optional[str] = None) -> Dict[str, Any]`

生成完整的提示词对象

| 参数 | 类型 | 说明 |
|-----|------|------|
| template_id | str | 模板ID |
| context | dict | 变量上下文 |
| system_prompt | str \| None | 可选的系统提示词 |

#### `preview_prompt(template_id: str, context: Dict[str, Any]) -> str`

预览渲染后的提示词

| 参数 | 类型 | 说明 |
|-----|------|------|
| template_id | str | 模板ID |
| context | dict | 变量上下文 |

#### `render_raw(template_id: str, context: Dict[str, Any]) -> str`

仅渲染用户提示词部分

| 参数 | 类型 | 说明 |
|-----|------|------|
| template_id | str | 模板ID |
| context | dict | 变量上下文 |

#### `add_template_from_string(template_id: str, template_content: str, meta: Optional[Dict[str, Any]] = None)`

从字符串添加新模板

| 参数 | 类型 | 说明 |
|-----|------|------|
| template_id | str | 模板ID |
| template_content | str | 模板内容 |
| meta | dict \| None | 可选的元数据 |

#### `get_template_content(template_id: str) -> str`

获取模板原始内容

| 参数 | 类型 | 说明 |
|-----|------|------|
| template_id | str | 模板ID |

#### `clear_cache()`

清空模板缓存

---

## 📝 模板管理

### 添加新模板

**方式1：直接创建文件**

在 `prompts/` 目录下创建 `.jinja` 文件：

```jinja
{# 新模板示例 #}
这是一个新模板，变量：{{ variable_name }}
```

**方式2：通过API添加**

```python
engine.add_template_from_string(
    template_id="new_template",
    template_content="这是一个新模板，变量：{{ variable_name }}",
    meta={
        "name": "新模板",
        "category": "custom",
        "version": "v1.0.0"
    }
)
```

### 模板语法

使用Jinja2模板语法，支持：

- 变量输出：`{{ variable }}`
- 条件判断：`{% if condition %}...{% endif %}`
- 循环：`{% for item in items %}...{% endfor %}`
- 注释：`{# 这是注释 #}`

---

## 🔨 维护指南

### 目录结构

```
模块X_提示词工程模块/
├── prompt_engine.py          # 核心类文件
├── prompts/                  # 提示词模板目录
│   ├── requirement_structuring.jinja
│   ├── requirement_validation.jinja
│   ├── architecture_solution_llm1.jinja
│   ├── architecture_solution_llm2.jinja
│   ├── architecture_solution_llm3.jinja
│   ├── solution_fusion.jinja
│   ├── data_contract_gen.jinja
│   ├── interface_contract_gen.jinja
│   ├── agent_md_gen.jinja
│   ├── mock_gen.jinja
│   └── ide_bundle_gen.jinja
├── readme_模块X.md           # 本文档
└── 模块X落地开发文档.md       # 落地开发文档
```

### 更新日志

| 版本 | 日期 | 更新内容 |
|-----|------|---------|
| **v1.2.0** | **2026-03-09** | **AC范式V5.2提示词矩阵全面升级**：<br>• 升级所有9个jinja模板，支持双场景原生适配（单IDE小项目/多IDE Agent矩阵）<br>• 新增分层规则体系、沙盒隔离约束<br>• 新增模块0中控能力、异常自动处理<br>• 新增IDE原生规则绑定（.trae/.cursor）<br>• 新增机读化输出（directory_tree_manifest、manifest.json、contract_snapshot等）<br>• **重要**：本次升级完全无需调整py脚本，仅需升级jinja模板 |
| v1.1.0 | 2026-03-04 | 修复所有提示词模板变量名不匹配问题 |
| v1.0.0 | 2026-03-01 | 初始版本，实现核心功能 |

### 重要修复记录（v1.1.0）

**问题描述**：2026-03-04 发现所有提示词模板的变量名与代码中实际传递的变量名不匹配，导致Pipeline各阶段之间信息传导失败，LLM无法获取正确的输入。

**修复内容**：
| 模板文件 | 修复前变量名 | 修复后变量名 |
|----------|------------|-----------|
| requirement_validation.jinja | structured_requirements | structured_requirement |
| data_contract_gen.jinja | architecture_solution | final_solution |
| interface_contract_gen.jinja | architecture_solution / data_contracts | final_solution |
| mock_gen.jinja | interface_contracts | final_solution |
| agent_md_gen.jinja | project_info / architecture_solution / data_contracts / interface_contracts | final_solution / contracts |
| ide_bundle_gen.jinja | project_info / architecture_solution / data_contracts / interface_contracts | final_solution / contracts / agent_md |

**注意事项**：
- 新增或修改模板时，务必确保变量名与 pipeline_orchestrator.py 中调用时传递的变量名保持一致
- 建议使用 `preview_prompt()` 方法在修改模板后进行测试验证

---

## ❓ 常见问题

### Q: 如何调试提示词渲染结果？

A: 使用 `preview_prompt()` 方法可以查看格式化的提示词预览：

```python
preview = engine.preview_prompt(template_id, context)
print(preview)
```

### Q: 模板修改后需要重启应用吗？

A: 不需要，本模块支持模板热更新，会自动检测文件修改并重新加载。

### Q: 如何添加自定义的系统提示词？

A: 在调用 `generate_prompt()` 时通过 `system_prompt` 参数传入：

```python
prompt = engine.generate_prompt(
    template_id="xxx",
    context={...},
    system_prompt="自定义系统提示词"
)
```

### Q: 模板变量验证失败怎么办？

A: 使用 `validate_variables()` 方法检查缺失的变量：

```python
result = engine.validate_variables(template_id, context)
if not result["valid"]:
    print(f"缺失变量: {result['missing_vars']}")
```

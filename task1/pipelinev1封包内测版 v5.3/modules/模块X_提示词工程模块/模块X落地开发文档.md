# 模块X_提示词工程模块 - 落地开发文档

&gt; 基于AC锚点契约式人机协同开发范式，构建专业级提示词工程模块

---

## 📋 目录

- [一、模块背景与目标](#一模块背景与目标)
- [二、完整的目录结构设计](#二完整的目录结构设计)
- [三、核心模块详解](#三核心模块详解)
- [四、核心数据结构定义](#四核心数据结构定义)
- [五、分阶段实施步骤](#五分阶段实施步骤)
- [六、具体的todolist计划](#六具体的todolist计划)
- [七、风险评估与应对措施](#七风险评估与应对措施)

---

## 一、模块背景与目标

### 1.1 模块背景

在AI驱动的开发工具中，提示词质量直接影响LLM的输出质量。传统的提示词往往硬编码在业务代码中，存在以下问题：

- **耦合度高**：提示词与业务逻辑混在一起，修改困难
- **难以迭代**：优化提示词需要修改代码、重新部署
- **缺少管理**：没有统一的模板库、版本管理、A/B测试机制
- **调试困难**：无法方便地预览和调试提示词渲染结果

### 1.2 核心目标

| 目标维度 | 具体目标 |
|---------|---------|
| **解耦目标** | 提示词与业务逻辑完全解耦 |
| **管理目标** | 支持模板库管理、热更新、缓存 |
| **质量目标** | 支持变量验证、提示词预览、调试 |
| **扩展目标** | 支持模板版本管理、A/B测试框架 |

### 1.3 非功能约束

- **技术栈**：Python + Jinja2
- **LLM友好**：所有代码包含中文docstring
- **容错机制**：完善的异常处理、降级方案
- **性能优化**：模板缓存、热更新机制

---

## 二、完整的目录结构设计

### 2.1 标准目录树

```text
模块X_提示词工程模块/
├── prompt_engine.py              # 核心类文件
├── prompts/                       # 提示词模板目录
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
├── readme_模块X.md                # 模块说明文档
└── 模块X落地开发文档.md           # 本文档
```

### 2.2 目录职责说明

| 目录/文件 | 职责 | 可修改性 |
|----------|------|---------|
| `prompt_engine.py` | 核心类实现，PromptEngine | 开发者可修改 |
| `prompts/` | 提示词模板库 | 开发者可修改 |
| `readme_模块X.md` | 模块使用说明与维护指南 | 开发者可修改 |
| `模块X落地开发文档.md` | 落地开发计划 | 项目负责人可修改 |

---

## 三、核心模块详解

### 3.1 模块总览

| 类名 | 核心职责 | 文件位置 |
|-----|---------|---------|
| **PromptEngine** | 提示词引擎核心类，提供模板管理、渲染等功能 | prompt_engine.py |

---

### 3.2 PromptEngine 核心类

| 维度 | 详细说明 |
|-----|---------|
| **核心职责** | 提示词模板管理、加载、缓存、热更新、渲染、调试 |
| **依赖** | Jinja2（模板渲染）、os（文件操作）、json（数据处理）、hashlib（内容指纹） |
| **输出** | 结构化提示词对象（含system_prompt、user_prompt、content_hash等） |
| **关键接口** | `generate_prompt()`、`preview_prompt()`、`list_templates()`、`validate_variables()` |

#### 核心方法列表

| 方法名 | 功能描述 |
|-------|---------|
| `__init__()` | 初始化Jinja2环境，预加载所有模板 |
| `get_template()` | 获取指定模板的完整信息 |
| `list_templates()` | 列出所有可用模板 |
| `validate_variables()` | 验证模板变量是否完整 |
| `generate_prompt()` | 生成完整的提示词对象 |
| `preview_prompt()` | 预览渲染后的提示词 |
| `render_raw()` | 仅渲染用户提示词部分 |
| `add_template_from_string()` | 从字符串添加新模板 |
| `get_template_content()` | 获取模板原始内容 |
| `clear_cache()` | 清空模板缓存 |

---

## 四、核心数据结构定义

### 4.1 提示词对象数据结构

```json
{
  "prompt_object": {
    "type": "object",
    "required": ["template_id", "generated_at", "content_hash", "system_prompt", "user_prompt"],
    "properties": {
      "template_id": {
        "type": "string",
        "description": "模板ID"
      },
      "generated_at": {
        "type": "string",
        "format": "date-time",
        "description": "生成时间，ISO8601格式"
      },
      "content_hash": {
        "type": "string",
        "description": "内容指纹，MD5(system_prompt + user_prompt)"
      },
      "system_prompt": {
        "type": "string",
        "description": "系统提示词"
      },
      "user_prompt": {
        "type": "string",
        "description": "用户提示词"
      },
      "context": {
        "type": "object",
        "description": "变量上下文"
      }
    }
  }
}
```

### 4.2 变量验证结果数据结构

```json
{
  "validation_result": {
    "type": "object",
    "required": ["valid", "missing_vars", "extra_vars"],
    "properties": {
      "valid": {
        "type": "boolean",
        "description": "是否通过验证"
      },
      "missing_vars": {
        "type": "array",
        "items": { "type": "string" },
        "description": "缺失的变量列表"
      },
      "extra_vars": {
        "type": "array",
        "items": { "type": "string" },
        "description": "多余的变量列表"
      }
    }
  }
}
```

---

## 五、分阶段实施步骤

### 5.1 阶段总览

| 阶段 | 目标 | 交付物 | 状态 |
|-----|------|-------|------|
| **阶段1：核心框架** | 完成PromptEngine类核心框架 | prompt_engine.py基础版 | ✅ 完成 |
| **阶段2：模板库** | 创建所有内置提示词模板 | 11个.jinja模板文件 | ✅ 完成 |
| **阶段3：文档完善** | 编写模块文档 | readme_模块X.md、本文档 | ✅ 完成 |
| **阶段4：测试验证** | 单元测试、集成测试 | 测试报告 | ☐ 待完成 |

---

## 六、具体的todolist计划

### 6.1 总体进度

- [x] 阶段1：核心框架
- [x] 阶段2：模板库
- [x] 阶段3：文档完善
- [ ] 阶段4：测试验证

---

### 6.2 详细Todo清单

#### 阶段1：核心框架
- [x] 创建模块目录结构
- [x] 实现PromptEngine类框架
- [x] 实现Jinja2环境初始化
- [x] 实现模板加载与缓存
- [x] 实现模板热更新机制
- [x] 实现变量验证功能
- [x] 实现提示词生成功能
- [x] 实现提示词预览功能
- [x] 实现单例模式

#### 阶段2：模板库
- [x] 创建requirement_structuring.jinja
- [x] 创建requirement_validation.jinja
- [x] 创建architecture_solution_llm1.jinja
- [x] 创建architecture_solution_llm2.jinja
- [x] 创建architecture_solution_llm3.jinja
- [x] 创建solution_fusion.jinja
- [x] 创建data_contract_gen.jinja
- [x] 创建interface_contract_gen.jinja
- [x] 创建agent_md_gen.jinja
- [x] 创建mock_gen.jinja
- [x] 创建ide_bundle_gen.jinja

#### 阶段3：文档完善
- [x] 编写readme_模块X.md
- [x] 编写模块X落地开发文档.md（本文档）

#### 阶段4：测试验证
- [ ] 编写单元测试
- [ ] 测试模板加载功能
- [ ] 测试提示词渲染功能
- [ ] 测试变量验证功能
- [ ] 测试热更新机制
- [ ] 集成测试（与其他模块联调）

---

## 七、风险评估与应对措施

### 7.1 技术风险

| 风险 | 可能性 | 影响 | 应对措施 |
|-----|--------|------|---------|
| Jinja2模板语法错误导致渲染失败 | 中 | 高 | 完善异常捕获、提供友好错误提示、模板预览功能 |
| 模板文件IO性能问题 | 低 | 中 | 模板缓存机制、热更新但不频繁重载 |
| 变量注入安全问题 | 低 | 高 | 禁止在模板中执行危险操作、输入验证 |

### 7.2 质量风险

| 风险 | 可能性 | 影响 | 应对措施 |
|-----|--------|------|---------|
| 提示词效果不达预期 | 中 | 高 | 支持独立迭代、模板版本管理、A/B测试框架预留 |
| 模板管理混乱 | 中 | 中 | 规范命名、分类管理、元数据标注 |

### 7.3 应对措施优先级

| 优先级 | 措施 | 执行时间 |
|-----|------|---------|
| P0 | 完善异常处理与错误提示 | 已实现 |
| P0 | 模板缓存与热更新 | 已实现 |
| P1 | 变量验证功能 | 已实现 |
| P1 | 提示词预览与调试 | 已实现 |

---

## 附录：参考模板

### 提示词模板编写规范

```jinja
{# 模板名称：简要说明 #}
你是一位专业的XXX，请完成以下任务。

【输入】
{{ input_variable }}

【要求】
1. 要求1
2. 要求2

请使用以下JSON格式输出：

{
  "key": "value"
}
```

### 使用示例

```python
from prompt_engine import get_prompt_engine

engine = get_prompt_engine()

# 预览提示词
preview = engine.preview_prompt(
    template_id="requirement_structuring",
    context={"requirement_text": "测试需求"}
)
print(preview)

# 生成提示词
prompt = engine.generate_prompt(
    template_id="requirement_structuring",
    context={"requirement_text": "测试需求"}
)
print(prompt["user_prompt"])
```

---

## 总结

本模块已完成核心功能实现，包括：

✅ PromptEngine核心类（模板管理、渲染、缓存、热更新）
✅ 11个内置提示词模板（覆盖需求分析、架构设计、契约生成等）
✅ 完善的文档（readme_模块X.md、落地开发文档）

后续可继续完善：
- 单元测试与集成测试
- 模板版本管理
- A/B测试框架

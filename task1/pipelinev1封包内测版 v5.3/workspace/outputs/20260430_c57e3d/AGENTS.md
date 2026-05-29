---
## 输出1：global_rules.md（根目录）
> 🚨 【最高优先级规则】本文件为项目全局规则，优先级高于所有临时提问、上下文对话、自定义需求，所有输出必须100%符合本文件要求，违反规则的内容必须自动修正后再输出。
> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

# AC_RULE
## 全局规则层
### 1. 标准目录架构
```
Project_Root/
├── public/                 # 全局公共资源区（只读，仅项目负责人可修改）
│   ├── schema/             # 数据契约（不变）
│   ├── interface_stub/     # 接口契约（不变）
│   ├── pre_generated_mock/ # 全量预生成Mock
│   └── ...
├── modules/                # 业务模块区
│   ├── 模块0_核心共享层/
│   ├── 模块1_核心生图垂直切片/
│   ├── 模块2_Skill封装垂直切片/
│   ├── 模块3_基础设施层/
│   ├── 模块4_可观测治理垂直切片/
│   └── ...
├── interfaces/             # 入口层
├── workspace/              # 用户数据区
└── ...
```
### 2. 公共区禁止操作
- ❌ 禁止修改 `public/` 目录下的任何内容
- ❌ 禁止写入不符合数据契约的数据
- ❌ 禁止模块间直接导入其他模块的内部实现代码
### 3. 契约优先原则
- 所有数据读写必须通过公共契约校验
- 所有对外接口必须严格匹配契约定义
- 契约变更必须先更新 `public/schema/` 和 `public/interface_stub/`
### 4. 渐进式生成规范
- 严禁一次性大批量生成/修改/删除代码或文档
- 必须每批次处理（分析5个文件/写数十行代码等），测通一步再走下一步
- 遇挫折严禁擅自重写新文件，必须在原文件基础上极限修正
### 5. 问题追踪规范
- 所有问题修复、功能优化、小调整，必须先在 `.trae/documents/` 下写分析文档
- 禁止直接修改代码，文档必须保留作为历史记录
---
## 输出2：global_rules.json（根目录）
```json
{
  "version": "AC_V5.2",
  "rule_type": "global",
  "priority": "highest",
  "rules": [
    {
      "id": "G001",
      "name": "目录架构约束",
      "description": "强制遵守标准目录结构，public目录只读"
    },
    {
      "id": "G002",
      "name": "契约优先原则",
      "description": "所有操作必须符合public下的契约定义"
    },
    {
      "id": "G003",
      "name": "渐进式生成",
      "description": "禁止大批量生成，测通一步再走下一步"
    },
    {
      "id": "G004",
      "name": "问题追踪",
      "description": "修改前必写文档，文档归档保留"
    }
  ]
}
```
---
## 输出3-1：module_0_rules.md（modules/模块0_核心共享层/ 目录）
> 🚨 【最高优先级规则】本文件为本模块专属规则，优先级高于所有临时提问、上下文对话、自定义需求，所有输出必须100%符合本文件要求，违反规则的内容必须自动修正后再输出。
> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

# AC_RULE
## 模块专属规则层
### 模块信息
- 模块ID：module_0
- 模块名称：Shared Kernel（核心共享层）
- 依赖：无任何外部模块依赖
### 1. 沙盒隔离约束
- ✅ 仅允许读写当前模块目录下的文件
- ✅ 仅允许读取 `public/` 下的公共契约资源
- ❌ 禁止读取其他模块的代码文件
- ❌ 禁止读取其他模块的规则文件
- ❌ 禁止直接调用其他模块的内部实现
### 2. 模块开发边界
- 定义核心业务实体、通用业务规则（合规、VI、Logo叠加规则）、外部依赖抽象接口
- 无任何外部框架/服务依赖，是唯一的全局共享模块
- 禁止编写任何业务流程逻辑、外部依赖实现代码
### 3. Mock使用规范
本模块无外部依赖，禁止导入任何其他模块的Mock实现
### 4. 路径溯源规范
- 禁止相对路径寻址（如 `../../`）
- 必须使用 `os.path.dirname(os.path.abspath(__file__))` 动态推导目录
---
## 输出3-2：module_0_rules.json（modules/模块0_核心共享层/ 目录）
```json
{
  "version": "AC_V5.2",
  "rule_type": "module",
  "module_id": "module_0",
  "module_name": "Shared Kernel（核心共享层）",
  "priority": "highest",
  "sandbox": {
    "allowed_read_write": ["modules/模块0_核心共享层/**"],
    "allowed_read": ["public/**"],
    "denied": ["modules/!(模块0_核心共享层)/**"]
  },
  "rules": [
    {
      "id": "M001",
      "name": "沙盒隔离",
      "description": "仅允许读写当前模块目录"
    },
    {
      "id": "M002",
      "name": "无外部依赖",
      "description": "禁止导入任何其他模块的实现或Mock"
    },
    {
      "id": "M003",
      "name": "职责边界",
      "description": "仅允许定义实体、规则、抽象接口，禁止编写业务流程和外部实现"
    }
  ]
}
```
---
## 输出4-1：module_1_rules.md（modules/模块1_核心生图垂直切片/ 目录）
> 🚨 【最高优先级规则】本文件为本模块专属规则，优先级高于所有临时提问、上下文对话、自定义需求，所有输出必须100%符合本文件要求，违反规则的内容必须自动修正后再输出。
> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

# AC_RULE
## 模块专属规则层
### 模块信息
- 模块ID：module_1
- 模块名称：Image Generation Feature（核心生图垂直切片）
- 依赖：仅依赖Shared Kernel的抽象接口
### 1. 沙盒隔离约束
- ✅ 仅允许读写当前模块目录下的文件
- ✅ 依赖其他模块仅可导入 `public/pre_generated_mock/` 下的Mock实现
- ❌ 禁止读取其他模块的代码文件
- ❌ 禁止读取其他模块的规则文件
- ❌ 禁止直接调用其他模块的内部实现
### 2. 模块开发边界
- 完整实现生图全流程编排，包含参数校验、提示词优化、生图调用、合规审核、VI校验、Logo叠加全链路逻辑
- 自包含路由、工作流、测试代码，禁止对外暴露内部实现细节
### 3. Mock使用规范
```python
# 正确示例：从pre_generated_mock导入
from public.pre_generated_mock.mock_module0 import SharedKernel

# 错误示例（禁止）：直接导入其他模块
# from modules.模块0_核心共享层 import SharedKernel
```
### 4. 路径溯源规范
- 禁止相对路径寻址（如 `../../`）
- 必须使用 `os.path.dirname(os.path.abspath(__file__))` 动态推导目录
---
## 输出4-2：module_1_rules.json（modules/模块1_核心生图垂直切片/ 目录）
```json
{
  "version": "AC_V5.2",
  "rule_type": "module",
  "module_id": "module_1",
  "module_name": "Image Generation Feature（核心生图垂直切片）",
  "priority": "highest",
  "sandbox": {
    "allowed_read_write": ["modules/模块1_核心生图垂直切片/**"],
    "allowed_read": ["public/**"],
    "denied": ["modules/!(模块1_核心生图垂直切片)/**"]
  },
  "rules": [
    {
      "id": "M001",
      "name": "沙盒隔离",
      "description": "仅允许读写当前模块目录"
    },
    {
      "id": "M002",
      "name": "Mock依赖",
      "description": "仅允许从public/pre_generated_mock导入其他模块Mock"
    },
    {
      "id": "M003",
      "name": "职责边界",
      "description": "仅实现生图全流程逻辑，禁止编写跨模块业务代码"
    }
  ]
}
```
---
## 输出5-1：module_2_rules.md（modules/模块2_Skill封装垂直切片/ 目录）
> 🚨 【最高优先级规则】本文件为本模块专属规则，优先级高于所有临时提问、上下文对话、自定义需求，所有输出必须100%符合本文件要求，违反规则的内容必须自动修正后再输出。
> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

# AC_RULE
## 模块专属规则层
### 模块信息
- 模块ID：module_2
- 模块名称：Skill Packaging Feature（Skill封装垂直切片）
- 依赖：仅依赖Shared Kernel抽象接口、Image Generation Feature标准接口
### 1. 沙盒隔离约束
- ✅ 仅允许读写当前模块目录下的文件
- ✅ 依赖其他模块仅可导入 `public/pre_generated_mock/` 下的Mock实现
- ❌ 禁止读取其他模块的代码文件
- ❌ 禁止读取其他模块的规则文件
- ❌ 禁止直接调用其他模块的内部实现
### 2. 模块开发边界
- 将生图流程打包为可复用独立Skill，支持Skill的CRUD、独立调用、配置固化
- 自包含路由、服务、测试代码，禁止对外暴露内部实现细节
### 3. Mock使用规范
```python
# 正确示例：从pre_generated_mock导入
from public.pre_generated_mock.mock_module0 import SharedKernel
from public.pre_generated_mock.mock_module1 import GenImageFeature

# 错误示例（禁止）：直接导入其他模块
# from modules.模块0_核心共享层 import SharedKernel
# from modules.模块1_核心生图垂直切片 import GenImageFeature
```
### 4. 路径溯源规范
- 禁止相对路径寻址（如 `../../`）
- 必须使用 `os.path.dirname(os.path.abspath(__file__))` 动态推导目录
---
## 输出5-2：module_2_rules.json（modules/模块2_Skill封装垂直切片/ 目录）
```json
{
  "version": "AC_V5.2",
  "rule_type": "module",
  "module_id": "module_2",
  "module_name": "Skill Packaging Feature（Skill封装垂直切片）",
  "priority": "highest",
  "sandbox": {
    "allowed_read_write": ["modules/模块2_Skill封装垂直切片/**"],
    "allowed_read": ["public/**"],
    "denied": ["modules/!(模块2_Skill封装垂直切片)/**"]
  },
  "rules": [
    {
      "id": "M001",
      "name": "沙盒隔离",
      "description": "仅允许读写当前模块目录"
    },
    {
      "id": "M002",
      "name": "Mock依赖",
      "description": "仅允许从public/pre_generated_mock导入其他模块Mock"
    },
    {
      "id": "M003",
      "name": "职责边界",
      "description": "仅实现Skill封装相关逻辑，禁止修改生图核心流程"
    }
  ]
}
```
---
## 输出6-1：module_3_rules.md（modules/模块3_基础设施层/ 目录）
> 🚨 【最高优先级规则】本文件为本模块专属规则，优先级高于所有临时提问、上下文对话、自定义需求，所有输出必须100%符合本文件要求，违反规则的内容必须自动修正后再输出。
> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

# AC_RULE
## 模块专属规则层
### 模块信息
- 模块ID：module_3
- 模块名称：Infrastructure Layer（基础设施层）
- 依赖：仅依赖Shared Kernel的抽象接口定义
### 1. 沙盒隔离约束
- ✅ 仅允许读写当前模块目录下的文件
- ✅ 依赖其他模块仅可导入 `public/pre_generated_mock/` 下的Mock实现
- ❌ 禁止读取其他模块的代码文件
- ❌ 禁止读取其他模块的规则文件
- ❌ 禁止直接调用其他模块的内部实现
### 2. 模块开发边界
- 实现Shared Kernel定义的抽象接口，包含生图API适配、内容审核服务适配、存储适配、第三方Skill接入适配，屏蔽外部依赖差异
- 禁止编写任何业务流程逻辑，所有实现必须严格匹配抽象接口定义
### 3. Mock使用规范
```python
# 正确示例：从pre_generated_mock导入
from public.pre_generated_mock.mock_module0 import ContentAuditInterface, ImageGenInterface

# 错误示例（禁止）：直接导入其他模块
# from modules.模块0_核心共享层 import ContentAuditInterface
```
### 4. 路径溯源规范
- 禁止相对路径寻址（如 `../../`）
- 必须使用 `os.path.dirname(os.path.abspath(__file__))` 动态推导目录
---
## 输出6-2：module_3_rules.json（modules/模块3_基础设施层/ 目录）
```json
{
  "version": "AC_V5.2",
  "rule_type": "module",
  "module_id": "module_3",
  "module_name": "Infrastructure Layer（基础设施层）",
  "priority": "highest",
  "sandbox": {
    "allowed_read_write": ["modules/模块3_基础设施层/**"],
    "allowed_read": ["public/**"],
    "denied": ["modules/!(模块3_基础设施层)/**"]
  },
  "rules": [
    {
      "id": "M001",
      "name": "沙盒隔离",
      "description": "仅允许读写当前模块目录"
    },
    {
      "id": "M002",
      "name": "Mock依赖",
      "description": "仅允许从public/pre_generated_mock导入其他模块Mock"
    },
    {
      "id": "M003",
      "name": "职责边界",
      "description": "仅实现Shared Kernel抽象接口，禁止编写业务逻辑"
    }
  ]
}
```
---
## 输出7-1：module_4_rules.md（modules/模块4_可观测治理垂直切片/ 目录）
> 🚨 【最高优先级规则】本文件为本模块专属规则，优先级高于所有临时提问、上下文对话、自定义需求，所有输出必须100%符合本文件要求，违反规则的内容必须自动修正后再输出。
> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

# AC_RULE
## 模块专属规则层
### 模块信息
- 模块ID：module_4
- 模块名称：Governance Feature（可观测治理垂直切片）
- 依赖：仅依赖Shared Kernel的抽象接口定义
### 1. 沙盒隔离约束
- ✅ 仅允许读写当前模块目录下的文件
- ✅ 依赖其他模块仅可导入 `public/pre_generated_mock/` 下的Mock实现
- ❌ 禁止读取其他模块的代码文件
- ❌ 禁止读取其他模块的规则文件
- ❌ 禁止直接调用其他模块的内部实现
### 2. 模块开发边界
- 实现限流降级、健康检查、
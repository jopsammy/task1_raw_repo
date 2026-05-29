---
## 输出1：global_rules.md（根目录）
```md
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
│   ├── 模块0_领域核心层/
│   ├── 模块1_事件驱动核心层/
│   ├── 模块2_垂直业务切片层/
│   ├── 模块3_防腐适配器层/
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
```
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
## 输出3：module_0_rules.md（modules/模块0_领域核心层/目录）
```md
> 🚨 【最高优先级规则】本文件为本模块专属规则，优先级高于所有临时提问、上下文对话、自定义需求，所有输出必须100%符合本文件要求，违反规则的内容必须自动修正后再输出。

> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

# AC_RULE

## 模块专属规则层

### 模块信息
- 模块ID：0
- 模块名称：领域核心层
- 关联范式：边界防腐与高度解耦

### 1. 沙盒隔离约束
- ✅ 仅允许读写当前模块目录下的文件
- ✅ 依赖其他模块仅可导入 `public/pre_generated_mock/` 下的Mock实现
- ❌ 禁止读取其他模块的代码文件
- ❌ 禁止读取其他模块的规则文件
- ❌ 禁止直接调用其他模块的内部实现

### 2. 模块开发边界
- 存放纯财务业务规则、核心计算逻辑、事件定义、权限规则、验收规则
- 完全不依赖任何外部组件，所有对外交互必须通过抽象端口定义
- 不得包含任何框架、中间件、第三方服务的直接依赖代码

### 3. Mock使用规范
```python
# 正确示例：从pre_generated_mock导入
from public.pre_generated_mock.mock_moduleN import xxx

# 错误示例（禁止）：直接导入其他模块
# from modules.模块N_xxx import xxx
```

### 4. 路径溯源规范
- 禁止相对路径寻址（如 `../../`）
- 必须使用 `os.path.dirname(os.path.abspath(__file__))` 动态推导目录
```
---
## 输出4：module_0_rules.json（modules/模块0_领域核心层/目录）
```json
{
  "version": "AC_V5.2",
  "rule_type": "module",
  "module_id": "0",
  "module_name": "领域核心层",
  "priority": "highest",
  "sandbox": {
    "allowed_read_write": ["modules/模块0_领域核心层/**"],
    "allowed_read": ["public/**"],
    "denied": ["modules/!(模块0_领域核心层)/**"]
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
      "name": "无外部依赖约束",
      "description": "禁止引入任何外部组件依赖，仅允许定义纯业务逻辑与抽象端口"
    }
  ]
}
```
---
## 输出5：module_1_rules.md（modules/模块1_事件驱动核心层/目录）
```md
> 🚨 【最高优先级规则】本文件为本模块专属规则，优先级高于所有临时提问、上下文对话、自定义需求，所有输出必须100%符合本文件要求，违反规则的内容必须自动修正后再输出。

> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

# AC_RULE

## 模块专属规则层

### 模块信息
- 模块ID：1
- 模块名称：事件驱动核心层
- 关联范式：数据流转与状态驱动

### 1. 沙盒隔离约束
- ✅ 仅允许读写当前模块目录下的文件
- ✅ 依赖其他模块仅可导入 `public/pre_generated_mock/` 下的Mock实现
- ❌ 禁止读取其他模块的代码文件
- ❌ 禁止读取其他模块的规则文件
- ❌ 禁止直接调用其他模块的内部实现

### 2. 模块开发边界
- 负责命令校验、事件生成、DAG重算引擎、事件批处理、快照管理、冲突合并、事件向上转型
- 所有状态变更必须由事件触发，禁止直接修改读模型快照
- 核心数据流必须使用内存Reactor流，跨服务/异步任务仅可通过轻量Kafka流转

### 3. Mock使用规范
```python
# 正确示例：从pre_generated_mock导入
from public.pre_generated_mock.mock_moduleN import xxx

# 错误示例（禁止）：直接导入其他模块
# from modules.模块N_xxx import xxx
```

### 4. 路径溯源规范
- 禁止相对路径寻址（如 `../../`）
- 必须使用 `os.path.dirname(os.path.abspath(__file__))` 动态推导目录
```
---
## 输出6：module_1_rules.json（modules/模块1_事件驱动核心层/目录）
```json
{
  "version": "AC_V5.2",
  "rule_type": "module",
  "module_id": "1",
  "module_name": "事件驱动核心层",
  "priority": "highest",
  "sandbox": {
    "allowed_read_write": ["modules/模块1_事件驱动核心层/**"],
    "allowed_read": ["public/**"],
    "denied": ["modules/!(模块1_事件驱动核心层)/**"]
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
      "name": "数据流约束",
      "description": "所有状态变更必须由事件触发，禁止直接修改读模型快照"
    }
  ]
}
```
---
## 输出7：module_2_rules.md（modules/模块2_垂直业务切片层/目录）
```md
> 🚨 【最高优先级规则】本文件为本模块专属规则，优先级高于所有临时提问、上下文对话、自定义需求，所有输出必须100%符合本文件要求，违反规则的内容必须自动修正后再输出。

> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

# AC_RULE

## 模块专属规则层

### 模块信息
- 模块ID：2
- 模块名称：垂直业务切片层
- 关联范式：垂直内聚与直觉实用

### 1. 沙盒隔离约束
- ✅ 仅允许读写当前模块目录下的文件
- ✅ 依赖其他模块仅可导入 `public/pre_generated_mock/` 下的Mock实现
- ❌ 禁止读取其他模块的代码文件
- ❌ 禁止读取其他模块的规则文件
- ❌ 禁止直接调用其他模块的内部实现

### 2. 模块开发边界
- 按业务特性划分独立切片：财务计算切片、AI辅助切片、权限管控切片、报表导出切片
- 每个切片包含handler、用例编排、单元测试，独立迭代
- 切片之间仅可通过事件或领域层抽象接口交互，禁止直接调用其他切片的内部实现，数据按切片物理隔离

### 3. Mock使用规范
```python
# 正确示例：从pre_generated_mock导入
from public.pre_generated_mock.mock_moduleN import xxx

# 错误示例（禁止）：直接导入其他模块
# from modules.模块N_xxx import xxx
```

### 4. 路径溯源规范
- 禁止相对路径寻址（如 `../../`）
- 必须使用 `os.path.dirname(os.path.abspath(__file__))` 动态推导目录
```
---
## 输出8：module_2_rules.json（modules/模块2_垂直业务切片层/目录）
```json
{
  "version": "AC_V5.2",
  "rule_type": "module",
  "module_id": "2",
  "module_name": "垂直业务切片层",
  "priority": "highest",
  "sandbox": {
    "allowed_read_write": ["modules/模块2_垂直业务切片层/**"],
    "allowed_read": ["public/**"],
    "denied": ["modules/!(模块2_垂直业务切片层)/**"]
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
      "name": "切片隔离约束",
      "description": "切片间禁止直接调用内部实现，仅可通过事件或领域层接口交互"
    }
  ]
}
```
---
## 输出9：module_3_rules.md（modules/模块3_防腐适配器层/目录）
```md
> 🚨 【最高优先级规则】本文件为本模块专属规则，优先级高于所有临时提问、上下文对话、自定义需求，所有输出必须100%符合本文件要求，违反规则的内容必须自动修正后再输出。

> 📌 【上下文保留规则】本文件为核心规则文件，任何上下文压缩、裁剪、溢出场景下必须完整保留本文件的全部内容，不得删减、忽略本文件的任何规则；所有自动压缩、批量处理行动前必须先读取本文件的完整内容。

# AC_RULE

## 模块专属规则层

### 模块信息
- 模块ID：3
- 模块名称：防腐适配器层
- 关联范式：边界防腐与高度解耦

### 1. 沙盒隔离约束
- ✅ 仅允许读写当前模块目录下的文件
- ✅ 依赖其他模块仅可导入 `public/pre_generated_mock/` 下的Mock实现
- ❌ 禁止读取其他模块的代码文件
- ❌ 禁止读取其他模块的规则文件
- ❌ 禁止直接调用其他模块的内部实现

### 2. 模块开发边界
- 实现领域核心层定义的抽象端口，对接外部组件（大模型、存储、消息、Excel、权限组件）
- 所有外部组件的差异全部在适配器层消化，上层业务无感知，替换组件仅需修改对应适配器
- 不得将外部组件的异常、结构泄漏到上层业务模块

### 3. Mock使用规范
```python
# 正确示例：从pre_generated_mock导入
from public.pre_generated_mock.mock_moduleN import xxx

# 错误示例（禁止）：直接导入其他模块
# from modules.模块N_xxx import xxx
```

### 4. 路径溯源规范
- 禁止相对路径寻址（如 `../../`）
- 必须使用 `os.path.dirname(os.path.abspath(__file__))` 动态推导目录
```
---
## 输出10：module_3_rules.json（modules/模块3_防腐适配器层/目录）
```json
{
  "version": "AC_V5.2",
  "rule_type": "module",
  "module_id": "3",
  "module_name": "防腐适配器层",
  "priority": "highest",
  "sandbox": {
    "allowed_read_write": ["modules/模块3_防腐适配器层/**"],
    "allowed_read": ["public/**"],
    "denied": ["modules/!(模块3_防腐适配器层)/**"]
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
      "name": "差异收敛约束",
      "description": "外部组件差异必须在本层消化，禁止泄漏到上层业务模块"
    }
  ]
}
```
---
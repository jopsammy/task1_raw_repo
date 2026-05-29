# 模块1：数据锚点与存储模块使用说明书

## 1. 模块简介

数据锚点与存储模块是整个需求结构化分析工具的底层数据基石，负责需求锚点管理、架构锚点管理、契约锚点管理、全链路可追溯机制、数据JSON存储与读取。

### 1.1 核心功能

- **需求锚点管理**：创建、冻结、查询需求锚点
- **架构锚点管理**：管理架构设计锚点
- **契约锚点管理**：管理接口契约、数据契约等
- **全链路可追溯机制**：记录需求到架构到实现的完整链路
- **数据JSON存储与读取**：提供标准的CRUD接口
- **自动备份机制**：每次保存自动生成备份文件
- **运行记录管理**（新增v1.1.0）：Pipeline运行记录的持久化、加载、查询
- **配置管理增强**（新增v3.0.0）：支持环境变量配置路径、provider槽位管理、API配置字段更新

## 2. 安装与配置

### 2.1 环境要求

- **Python版本**：3.8+
- **依赖库**：无第三方依赖，仅使用Python标准库

### 2.2 目录结构

```
v1/
└── modules/
    └── 模块1_数据锚点与存储模块/
        ├── data_anchor_manager.py    # 核心业务类
        ├── readme_模块1.md             # 本使用说明
        └── 模块1落地开发文档.md        # 落地开发文档
```

## 3. 使用指南

### 3.1 初始化模块

```python
from modules.模块1_数据锚点与存储模块.data_anchor_manager import DataAnchorManager

# 使用默认工作区目录
manager = DataAnchorManager()

# 或指定自定义工作区目录
manager = DataAnchorManager(workspace_dir="path/to/workspace")
```

### 3.2 创建需求项目

```python
# 创建新的需求项目
project_id = manager.create_requirement_project("电商系统需求分析")
print(f"创建的项目ID: {project_id}")
```

### 3.3 添加需求条目

```python
# 加载项目
project_data = manager.load_requirement_project(project_id)

# 添加需求条目
requirement_item = {
    "content": "用户可以登录系统",
    "level": 1,
    "order": 1,
    "status": "pending",
    "tags": ["登录", "认证"]
}

req_id = manager.add_requirement_item(project_id, requirement_item)
print(f"添加的需求条目ID: {req_id}")
```

### 3.4 创建需求锚点

```python
# 创建需求锚点
anchor = manager.create_requirement_anchor(
    project_id=project_id,
    req_id=req_id,
    content="用户可以登录系统"
)
print(f"创建的锚点ID: {anchor['anchor_id']}")

# 冻结锚点
manager.freeze_requirement_anchor(anchor['anchor_id'])
```

### 3.5 创建架构锚点

```python
# 创建架构锚点
architecture_data = {
    "modules": ["用户模块", "订单模块"],
    "tech_stack": ["Python", "Streamlit"]
}

architecture_anchor = manager.create_architecture_anchor(
    project_id=project_id,
    architecture_data=architecture_data
)
```

### 3.6 创建契约锚点

```python
# 创建接口契约锚点
contract_data = {
    "interface_name": "login",
    "input": {"username": "str", "password": "str"},
    "output": {"token": "str"}
}

contract_anchor = manager.create_contract_anchor(
    project_id=project_id,
    contract_type="interface",
    contract_data=contract_data
)
```

### 3.7 可追溯链接

```python
# 添加追溯链接
manager.add_traceability_link(
    from_id=anchor['anchor_id'],
    to_id=architecture_anchor['anchor_id'],
    link_type="implements"
)

# 获取追溯链
trace_chain = manager.get_traceability_chain(anchor['anchor_id'])
for trace in trace_chain:
    print(f"{trace['from_id']} -> {trace['to_id']} ({trace['link_type']})")
```

### 3.8 列出项目和锚点

```python
# 列出所有需求项目
projects = manager.list_requirement_projects()
for project in projects:
    print(f"项目: {project['project_name']} ({project['project_id']})")

# 列出所有锚点
anchors = manager.list_anchors(project_id=project_id)
for anchor_data in anchors:
    print(f"锚点: {anchor_data['anchor_type']} ({anchor_data['anchor_id']})")
```

## 4. 数据结构

### 4.1 需求项目数据结构

```json
{
  "project_id": "20260301_123456",
  "project_name": "电商系统需求分析",
  "created_at": "2026-03-01T10:00:00",
  "updated_at": "2026-03-01T10:30:00",
  "requirements": [],
  "metadata": {}
}
```

### 4.2 需求条目数据结构

| 字段名 | 类型 | 描述 |
|-------|------|------|
| req_id | str | 需求条目唯一UUID |
| anchor_id | str | 内容锚点ID（MD5哈希） |
| content | str | 需求内容文本 |
| level | int | 需求层级（1-5） |
| order | int | 排序权重，值越小越靠前 |
| parent_id | str或null | 父级需求ID |
| tags | array | 需求标签列表 |
| status | str | 需求状态（pending/analyzing/completed/rejected） |
| analysis_result | object或null | 结构化分析结果 |
| created_at | str | 创建时间（ISO8601） |

### 4.3 锚点数据结构

| 字段名 | 类型 | 描述 |
|-------|------|------|
| anchor_id | str | 锚点唯一ID（MD5哈希） |
| anchor_type | str | 锚点类型（requirement/architecture/contract_*） |
| project_id | str | 所属项目ID |
| content | str或object | 锚点内容 |
| frozen | bool | 是否已冻结 |
| created_at | str | 创建时间 |
| updated_at | str | 更新时间 |

## 5. 错误处理

本模块的所有方法都会抛出明确的异常，调用者应该捕获并处理这些异常：

| 异常类型 | 触发条件 | 处理建议 |
|---------|---------|--------|
| FileNotFoundError | 文件不存在 | 检查文件路径是否正确 |
| ValueError | 数据不符合Schema | 检查数据结构是否正确 |

### 5.1 异常处理示例

```python
try:
    project_data = manager.load_requirement_project("non-existent-id")
except FileNotFoundError as e:
    print(f"错误：{e}")
```

## 6. 维护指南

### 6.1 数据备份

- **自动备份**：每次保存项目时，系统会自动在`workspace/backups/`目录下生成备份文件
- **备份文件命名**：备份文件命名格式为`{project_id}_{timestamp}.json`

### 6.2 目录结构

工作区目录结构如下：

```
workspace/
├── requirements/    # 需求项目存储
├── anchors/         # 锚点数据存储
├── backups/         # 自动备份目录
└── traceability.json # 追溯关系数据
```

## 7. 合流指南

### 7.1 与其他模块的接口对接

本模块为其他模块提供标准化的数据接口，其他模块可以通过以下方式使用：

1. **导入模块**：
   ```python
   from modules.模块1_数据锚点与存储模块.data_anchor_manager import DataAnchorManager
   ```

2. **初始化实例**：
   ```python
   manager = DataAnchorManager()
   ```

3. **调用接口**：根据需要调用相应的接口

### 7.2 数据流转

1. **其他模块**：通过`create_requirement_project`、`load_requirement_project`等管理需求项目生命周期
2. **需求解析引擎**：通过`add_requirement_item`、`update_requirement_item`管理需求条目
3. **其他模块**：通过锚点接口实现可追溯机制

## 8. 运行记录管理（新增v1.1.0）

### 8.1 功能说明

新增的 `RunRecordManager` 负责完整的 Pipeline 运行记录管理，包含：
- 运行记录持久化存储（按日期组织）
- 运行记录加载与查询
- 详细记录每次运行的所有状态、输入、输出、LLM调用信息

### 8.2 目录结构

```
workspace/
└── runs/           # 运行记录存储目录
    └── 20260304/  # 按日期分组
        └── 55537728-bb5c-4101-a06c-541c746dde80.json
```

### 8.3 使用示例

```python
from modules.模块1_数据锚点与存储模块.run_record_manager import get_run_record_manager

# 获取运行记录管理器
manager = get_run_record_manager()

# 保存运行记录
run_id = manager.save_run_record(run_data)

# 加载运行记录
run_data = manager.load_run_record(run_id)

# 列出运行记录
runs = manager.list_run_records(limit=50)

# 获取最新运行记录
latest = manager.get_latest_run_record()
```

---

## 9. 配置管理API使用指南（新增v3.0.0）

### 9.1 环境变量配置路径

系统支持通过环境变量指定配置文件路径，便于测试隔离：

```python
import os
os.environ["AC_CONFIG_PATH"] = "/path/to/test_config.json"
from modules.模块1_数据锚点与存储模块.config_manager import get_config_manager

config_manager = get_config_manager()
```

### 9.2 Provider槽位管理

获取前3个provider槽位（自动补齐不足3个的情况）：

```python
from modules.模块1_数据锚点与存储模块.config_manager import get_config_manager

config_manager = get_config_manager()
provider_slots = config_manager.get_provider_slots()
# 返回: ["openai", "deepseek", "doubao"] 或 ["slot_1", "slot_2", "slot_3"]
```

### 9.3 Provider字段更新

更新provider的指定字段（仅更新api_base/api_key/model）：

```python
# 更新单个provider的URL和模型（Key留空表示保持原值）
success = config_manager.update_provider_fields(
    provider_id="openai",
    api_base="https://api.openai.com/v1",
    api_key="",  # 空字符串表示不修改
    model="gpt-4o"
)

if success:
    config_manager.save_config()
    print("配置保存成功")
else:
    print("配置验证失败")
```

### 9.4 验证API

```python
# 验证API Base格式
is_valid = config_manager.validate_api_base("https://api.example.com/v1")
# 返回: True

# 验证模型名称非空
is_valid = config_manager.validate_model("gpt-4o")
# 返回: True
```

---

**最后更新时间**：2026-03-11
**模块版本**：3.0.0
**维护状态**：活跃

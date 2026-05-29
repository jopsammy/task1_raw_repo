
# 模块5：交付物切分模块使用说明书

## 1. 模块简介

交付物切分模块是整个需求结构化分析工具的输出管理模块，负责将pipeline运行结果切分成不同类型的交付物文件，并格式化保存到指定工作区目录。

### 1.1 核心功能

- **交付物切分**：从pipeline全量结果中提取各类交付物
- **格式化保存**：支持JSON、Markdown等多种格式
- **目录管理**：自动管理输出目录结构
- **容错处理**：完善的异常捕获和错误处理机制

## 2. 安装与配置

### 2.1 环境要求

- **Python版本**：3.8+
- **依赖库**：无第三方依赖，仅使用Python标准库

### 2.2 目录结构

```
v1/
└── modules/
    └── 模块5_交付物切分模块/
        ├── delivery_output_splitter.py    # 核心业务类
        ├── __init__.py                     # 模块入口，包含全局单例
        └── readme_模块5.md                 # 本使用说明
```

## 3. 使用指南

### 3.1 初始化模块

```python
from modules.模块5_交付物切分模块 import get_delivery_output_splitter

# 获取全局单例
splitter = get_delivery_output_splitter()

# 或指定自定义工作区目录
splitter = get_delivery_output_splitter(workspace_dir="path/to/workspace")
```

### 3.2 切分并保存交付物

```python
# 准备输入数据
final_solution = {...}  # 最终架构方案
all_results = {...}     # pipeline所有阶段结果
project_id = "20260301_123456"  # 可选，如果不提供会自动生成

# 切分并保存
result = splitter.split_and_save(
    final_solution=final_solution,
    all_results=all_results,
    project_id=project_id
)

# 检查保存结果
if result["success"]:
    print(f"成功保存 {len(result['saved_files'])} 个文件")
    print(f"文件保存在: {result['outputs_dir']}")
    print(f"使用的project_id: {result['project_id']}")
    for filename in result["saved_files"]:
        print(f"  - {filename}")
else:
    print(f"保存失败: {result['error']}")
```

### 3.3 project_id自动生成

当未提供`project_id`时，系统会自动生成一个唯一ID，格式为：`{YYYYMMDD}_{随机6位十六进制}`。例如：`20260306_abc123`。

**生成逻辑**：
- 日期部分：当前系统日期，格式为YYYYMMDD
- 随机部分：6位十六进制随机字符串，确保唯一性

**使用场景**：
- UI界面运行时，用户未指定project_id
- 命令行快速测试时
- 任何需要自动生成唯一标识的场景

## 4. 数据结构

### 4.1 输出目录结构

```
workspace/
└── outputs/
    └── {project_id}/
        ├── structured_requirement.json          # 结构化需求
        ├── requirement_validation.json           # 需求验证结果
        ├── final_architecture.json               # 最终架构方案
        ├── contracts.json                        # 契约文件
        ├── ide_bundle.md                         # 旧版IDE工程包（兼容保留）
        ├── ide_bundle_global.md                  # 全局IDE引导包
        ├── ide_bundle_index.md                   # IDE引导包索引
        ├── ide_bundle_module_{id}_{name}.md      # 模块级IDE引导包（多个）
        ├── agent.md                              # Agent维护文档
        └── all_results.json                      # 所有阶段结果（完整备份）
```

### 4.2 返回结果字典

| 字段名 | 类型 | 描述 |
|-------|------|------|
| `project_id` | str | 项目ID |
| `outputs_dir` | str | 输出目录完整路径 |
| `saved_files` | list | 成功保存的文件列表 |
| `success` | bool | 是否保存成功 |
| `error` | str（可选） | 错误信息（如果success为false） |

## 5. 维护指南

### 5.1 扩展新的交付物类型

如需支持新的交付物类型，只需在 `DeliveryOutputSplitter` 类中添加新的私有方法，并在 `split_and_save` 方法中调用：

```python
def _save_new_output(self, outputs_dir: str, all_results: Dict, result: Dict):
    """
    保存新类型的交付物
    """
    data = all_results.get("new_stage", {})
    if data.get("success") and "new_data" in data:
        filepath = os.path.join(outputs_dir, "new_output.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data["new_data"], f, ensure_ascii=False, indent=2)
        result["saved_files"].append("new_output.json")
```

---

**最后更新时间**：2026-03-07
**模块版本**：1.0.1
**维护状态**：活跃

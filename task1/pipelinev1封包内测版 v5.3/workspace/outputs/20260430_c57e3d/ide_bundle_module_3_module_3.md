# 基础设施层（Infrastructure Layer）IDE引导包
---
## 1. 模块功能说明
### 模块基本信息
- 模块ID：`module_3`
- 模块名称：Infrastructure Layer（基础设施层）
- 唯一依赖：Shared Kernel（`module_0`）的抽象接口定义
- 架构定位：核心业务与外部依赖之间的**边界防腐层**，完全屏蔽外部差异，保护核心业务不受外部依赖变化影响
### 核心职责
1. 实现Shared Kernel定义的所有外部依赖抽象接口：
   - 生图API多厂商适配（Stable Diffusion、Midjourney、豆包生图等）
   - 内容审核服务多厂商适配（百度AI审核、腾讯内容安全、阿里云绿网等）
   - 存储服务适配（MinIO、阿里云OSS、腾讯云COS、本地存储等）
   - 第三方Skill服务接入适配
2. 统一处理外部依赖的异常、重试、降级逻辑，上层业务无需感知外部服务状态
3. 所有外部依赖的替换仅需修改本模块实现，上层业务代码零改动
### 禁止边界
- ❌ 禁止编写任何业务流程逻辑
- ❌ 禁止暴露外部依赖的专属字段给上层业务
- ❌ 禁止修改抽象接口定义，所有实现必须严格匹配Shared Kernel的接口契约

---
## 2. 模块接口规范
### 契约遵循要求
所有接口必须100%匹配`public/interface_stub/infra_layer.stub`定义，禁止修改签名、入参、出参、异常类型
### 核心实现接口清单
| 所属抽象类 | 方法名 | 入参 | 出参 | 允许抛出异常 |
| --- | --- | --- | --- | --- |
| `ContentAuditInterface` | `audit_text` | `text: str, request_id: str` | `AuditResult` | `ParameterError`、`ExternalDependencyError` |
| `ContentAuditInterface` | `audit_image` | `image_url: str, request_id: str` | `AuditResult` | `ParameterError`、`ExternalDependencyError` |
| `ImageGenInterface` | `generate` | `prompt: str, size: str, extra_params: Optional[Dict[str, Any]]` | `GenResult` | `ParameterError`、`ImageGenError`、`ExternalDependencyError` |
| `ImageProcessInterface` | `overlay_logo` | `raw_image_url: str, logo_config: LogoOverlayConfig` | `ProcessResult` | `ParameterError`、`ImageProcessError` |
| `InfraLayer` | `save_file` | `file_path: str, content: bytes` | `str（文件访问URL）` | `ExternalDependencyError` |
| `InfraLayer` | `get_file` | `file_url: str` | `bytes（文件二进制内容）` | `ExternalDependencyError` |
### 通用约束
1. 所有外部依赖调用必须添加超时控制（默认30s）、重试机制（最多3次指数退避重试）
2. 所有外部原生异常必须转换为契约定义的标准异常类型，禁止抛出第三方原生异常
3. 所有返回值必须符合`public/schema/`下的JSON Schema定义

---
## 3. 模块开发指南
### 环境准备
1. 预读取`public/schema/`下所有数据契约、`public/interface_stub/`下接口契约
2. 从`public/pre_generated_mock/`导入Shared Kernel的抽象接口定义
### 开发规范
1. **沙盒隔离**：仅允许读写`modules/模块3_基础设施层/`目录下的文件，禁止读取其他模块的实现代码
2. **依赖导入规则**：
```python
# 正确：从公共Mock目录导入抽象接口
from public.pre_generated_mock.mock_module0 import ContentAuditInterface, ImageGenInterface, ImageProcessInterface

# 错误：禁止直接导入其他模块代码
# from modules.模块0_核心共享层 import ContentAuditInterface
```
3. **路径规则**：禁止使用`../../`相对路径寻址，必须使用`os.path.dirname(os.path.abspath(__file__))`动态推导目录
4. **实现顺序**：优先实现Mock版本适配→再实现单厂商真实适配→最后支持多厂商切换
5. **推荐目录结构**：
```
modules/模块3_基础设施层/
├── content_audit/          # 内容审核适配包
│   ├── mock.py             # Mock实现
│   ├── baidu.py            # 百度审核实现
│   └── tencent.py          # 腾讯审核实现
├── image_gen/              # 生图API适配包
├── image_process/          # 图像处理适配包
├── storage/                # 存储适配包
├── __init__.py
└── infra_layer.py          # 统一入口类
```

---
## 4. 模块测试计划
### 测试分层与验收标准
| 测试类型 | 测试范围 | 验收标准 |
| --- | --- | --- |
| 单元测试 | 每个接口实现的独立逻辑 | 覆盖率100%，覆盖正常场景、异常场景、边界场景 |
| 契约测试 | 接口是否符合公共契约定义 | 所有接口通过`public/interface_stub/`的契约校验，无签名/返回值不匹配问题 |
| 集成测试 | 与Shared Kernel抽象接口的兼容性 | 上层业务通过抽象接口调用无感知，替换不同实现无需修改上层代码 |
| 异常测试 | 外部依赖异常场景 | 超时、报错、限流等场景下均抛出标准异常，无原生异常泄露 |
| 性能测试 | 外部依赖调用性能 | 接口耗时P99<500ms，重试机制生效，无雪崩风险 |
### 测试工具
- 单元测试：`pytest`
- 契约测试：`pact-python`
- 性能测试：`locust`

---
## 5. 原子化TODO执行清单
按优先级排序，每完成一项验证通过再执行下一项：
| 序号 | 任务内容 | 预估耗时 | 依赖任务 | 验收标准 |
| --- | --- | --- | --- | --- |
| 1 | 初始化模块目录结构，创建模块规则文件（`module_3_rules.md`、`module_3_rules.json`） | 30min | 无 | 目录符合标准架构，规则文件与AGENTS文档完全一致 |
| 2 | 实现`ContentAuditInterface`的Mock适配 | 1h | 1 | 单测覆盖通过，符合接口契约 |
| 3 | 实现`ImageGenInterface`的Mock适配 | 1h | 2 | 单测覆盖通过，符合接口契约 |
| 4 | 实现`ImageProcessInterface`的Mock适配 | 1h | 3 | 单测覆盖通过，符合接口契约 |
| 5 | 实现Storage接口的Mock适配 | 1h | 4 | 单测覆盖通过，符合接口契约 |
| 6 | 完成`InfraLayer`统一入口类开发 | 1h | 5 | 可通过入口类获取所有接口实例，支持Mock/真实实现切换 |
| 7 | 对接MinIO对象存储实现Storage接口 | 2h | 6 | 上传、下载功能正常，异常处理符合要求 |
| 8 | 对接百度内容审核实现`ContentAuditInterface` | 2h | 7 | 文本、图片审核功能正常，异常处理符合要求 |
| 9 | 对接Stable Diffusion实现`ImageGenInterface` | 2h | 8 | 生图功能正常，异常处理符合要求 |
| 10 | 实现多厂商适配切换逻辑 | 2h | 9 | 可通过配置切换不同厂商实现，上层无感知 |
| 11 | 完成全量单元测试、契约测试 | 2h | 10 | 测试覆盖率100%，所有用例通过 |
| 12 | 编写模块使用文档 | 1h | 11 | 文档清晰说明每个实现的配置方式、切换方法 |
| 13 | 提测、修复遗留问题 | 2h | 12 | 测试无阻塞问题，性能达标 |

---
## 6. IDE规则配置文件
### 6.1 Trae IDE规则（`.trae/rules/module_3_rule.json`）
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
      "id": "M3_001",
      "name": "沙盒隔离",
      "description": "仅允许读写当前模块目录，禁止读取/修改其他模块代码",
      "level": "error",
      "enforce": true
    },
    {
      "id": "M3_002",
      "name": "契约强制校验",
      "description": "所有接口实现必须严格匹配public下的契约定义，禁止修改签名/返回值",
      "level": "error",
      "enforce": true
    },
    {
      "id": "M3_003",
      "name": "依赖导入约束",
      "description": "仅允许从public/pre_generated_mock导入其他模块的抽象接口，禁止直接导入其他模块实现",
      "level": "error",
      "enforce": true
    },
    {
      "id": "M3_004",
      "name": "职责边界约束",
      "description": "仅允许实现Shared Kernel抽象接口，禁止编写业务流程逻辑",
      "level": "warning",
      "enforce": true
    }
  ],
  "auto_check": {
    "pre_commit": true,
    "pre_push": true
  }
}
```
### 6.2 Cursor IDE规则（`.cursor/rules/module_3_rule.md`）
```markdown
# Cursor IDE 基础设施层开发规则
> 🚨 本规则优先级最高，所有代码生成、修改必须严格遵守
## 基本约束
1. 仅可操作`modules/模块3_基础设施层/`目录下的文件，禁止修改其他任何目录的内容
2. 仅可读取`public/`目录下的契约、Mock资源，禁止读取其他模块的代码
3. 所有外部依赖的导入必须从`public/pre_generated_mock/`导入，禁止直接导入其他模块代码
## 代码生成规则
1. 所有接口实现必须严格匹配`public/interface_stub/`中的定义，不得修改方法签名、入参、出参、异常类型
2. 禁止编写任何业务流程逻辑，仅可做外部依赖的适配、异常转换、重试降级处理
3. 所有外部依赖的原生异常必须转换为契约定义的标准异常，不得抛出原生异常
4. 禁止使用相对路径寻址，必须使用`os.path.dirname(os.path.abspath(__file__))`动态推导路径
## 测试规则
1. 每个接口实现必须配套单元测试，覆盖正常、异常、边界场景
2. 所有修改必须通过契约校验，不得违反公共契约定义
```

---
## 7. 模块状态模板（`module_status.json`）
```json
{
  "module_id": "module_3",
  "module_name": "Infrastructure Layer（基础设施层）",
  "status": "planning",
  "progress": 0,
  "last_updated": "2024-XX-XXTXX:XX:XXZ",
  "dependencies": [
    {
      "module_id": "module_0",
      "module_name": "Shared Kernel（核心共享层）",
      "required_status": "ready_for_merge"
    }
  ],
  "issues": [],
  "current_todo_index": 1,
  "test_coverage": 0
}
```
### 字段说明
- `status`枚举：`planning`（规划中）、`developing`（开发中）、`testing`（测试中）、`ready_for_merge`（待合并）、`merged`（已合并）
- `progress`：0-100整数，对应TODO清单完成进度
- `issues`：记录开发过程中的问题，包含问题ID、描述、优先级、处理状态
- `current_todo_index`：当前正在执行的TODO序号

---
## 8. 异常上报标准化规则
### 8.1 异常分类
| 异常类型 | 定义 | 级别 |
| --- | --- | --- |
| `contract_violation` | 接口实现违反公共契约定义（签名不匹配、返回值不符合Schema等） | critical |
| `dependency_error` | 外部依赖调用失败（超时、报错、限流等，重试3次仍失败） | error |
| `test_failure` | 单元测试、契约测试、集成测试用例失败 | warning |
| `performance_degradation` | 接口性能低于阈值（P99耗时>500ms、成功率<99.9%） | warning |
### 8.2 上报格式标准化
所有上报事件必须包含以下字段：
```json
{
  "event_id": "uuid",
  "event_type": "contract_violation/dependency_error/test_failure/performance_degradation",
  "module_id": "module_3",
  "timestamp": "2024-XX-XXTXX:XX:XXZ",
  "trace_id": "全链路追踪ID",
  "level": "info/warning/error/critical",
  "details": {
    "interface_name": "触发异常的接口名",
    "error_message": "异常描述",
    "stack_trace": "异常堆栈（可选）"
  }
}
```
### 8.3 自动上报触发条件
1. 代码提交前预检查发现契约违反自动上报
2. 单元测试、契约测试执行失败自动上报
3. 外部依赖调用重试3次仍失败自动上报
4. 性能监控发现耗时、成功率低于阈值自动上报
### 8.4 异常处理流程
1. **contract_violation**：立即回滚代码修改，若确实需要变更契约必须先走公共契约审批流程，更新`public/`下的契约文件后再修改代码
2. **dependency_error**：触发降级逻辑，自动切换到Mock实现，上报运维人员排查外部依赖故障
3. **test_failure**：暂停开发，修复代码问题，测试通过后再继续后续开发
4. **performance_degradation**：排查性能瓶颈，优化适配逻辑（如添加缓存、调整超时时间、批量处理等）

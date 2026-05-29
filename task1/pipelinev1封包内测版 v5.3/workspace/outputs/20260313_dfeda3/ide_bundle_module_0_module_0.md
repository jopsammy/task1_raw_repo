# 领域核心层 IDE 引导包（模块ID：0）
---
## 1. 模块功能说明
### 基础信息
| 项 | 详情 |
| --- | --- |
| 模块名称 | 领域核心层 |
| 设计范式 | 边界防腐与高度解耦 |
| 核心定位 | 系统最底层纯业务内核，所有财务规则的唯一可信源 |
| 依赖 | 无任何外部组件/其他业务模块依赖 |

### 核心职责
1. 存放100%不变的纯财务业务规则：税率计算、公式校验、分摊逻辑、合并报表规则等
2. 核心计算逻辑：财务模型DAG依赖计算、行项数值校验、维度聚合计算
3. 基础定义：领域事件、权限规则、数据结构、验收规则的唯一标准定义
4. 抽象端口：定义所有对外交互的抽象接口，上层/外部组件必须实现该接口才能与核心层交互

### 设计目标
- 核心逻辑零耦合：完全不依赖Spring、数据库、中间件等任何外部组件，可独立运行、独立测试
- 规则绝对稳定：财务规则变更必须经过评审后才能修改核心层代码，杜绝业务逻辑散落在各层
- 可移植性：支持信创改造、框架替换时核心层零修改，仅需替换适配器层实现

### 禁止行为
❌ 禁止引入任何外部依赖（包括框架、中间件SDK、第三方工具库）
❌ 禁止写入任何与业务规则无关的技术实现代码
❌ 禁止直接调用其他模块的内部实现
---
## 2. 模块接口规范
> 所有接口必须100%匹配`public/interface_stub/`下的契约定义，所有数据必须符合`public/schema/`下的数据契约
### 核心接口
| 接口名称 | 签名 | 功能描述 | 异常抛出 |
| --- | --- | --- | --- |
| validate_command | `def validate_command(self, command: Command, permission: RolePermission) -> bool` | 校验命令合法性与操作者权限 | `ValidationError`（命令不符合业务规则）、`PermissionDeniedError`（无操作权限） |
| apply_event | `def apply_event(self, snapshot: FinancialModelSnapshot, event: DomainEvent) -> FinancialModelSnapshot` | 将领域事件应用到快照生成新的快照，所有状态变更仅能通过该方法实现 | `ValidationError`（事件不符合业务规则） |

### 抽象端口定义规范
1. 所有对外交互的端口必须定义为纯接口，无任何实现代码
2. 端口入参/出参必须使用核心层定义的标准数据结构，禁止使用外部组件的特有类型
3. 端口必须明确抛出的异常类型，禁止直接抛出外部组件异常

### 数据结构约束
所有内部数据结构必须与`public/schema/contract_snapshot_1.0.0.json`中定义的结构完全一致：
- DomainEvent、LineItemUpdatedEvent、CalculationBatchEvent
- FinancialModelSnapshot、RolePermission、RoleContext
---
## 3. 模块开发指南
### 沙盒约束
✅ 仅允许读写`modules/模块0_领域核心层/`目录下的文件
✅ 仅允许读取`public/`目录下的契约、Mock资源
❌ 禁止访问其他模块的任何文件
❌ 禁止使用相对路径寻址（如`../../`），必须使用`os.path.dirname(os.path.abspath(__file__))`动态推导路径

### 依赖规范
```python
# 正确：仅导入标准库、public下的契约与Mock
import uuid
from datetime import datetime
from public.schema.domain_event import DomainEvent
from public.pre_generated_mock.mock_utils import validate_schema

# 错误：禁止导入外部依赖/其他模块代码
# import springframework
# from modules.模块1_事件驱动核心层.service import xxx
```

### 代码规范
1. 所有业务逻辑必须为纯函数：相同输入永远返回相同输出，无任何副作用
2. 数值计算必须使用高精度类型（Java用BigDecimal、Python用Decimal），禁止使用浮点型
3. 所有业务规则必须写注释，标注对应的财务制度条款编号
4. 代码提交前必须通过契约校验工具检查接口/数据结构是否符合契约要求
---
## 4. 模块测试计划
| 测试类型 | 覆盖率要求 | 测试场景 | 验收标准 |
| --- | --- | --- | --- |
| 单元测试 | 100% | 1. 命令权限校验：合法/非法/越权命令校验<br>2. 事件应用测试：正常事件/冲突事件/非法事件应用<br>3. 计算逻辑测试：正常数值/边界数值/异常数值计算<br>4. 规则覆盖：每条财务规则至少3个用例（正常/边界/异常） | 所有用例100%通过，无漏测场景 |
| 契约测试 | 100% | 1. 接口签名与public契约一致性校验<br>2. 数据结构与public契约一致性校验 | 无契约冲突 |
| 性能测试 | - | 单次apply_event执行耗时<1ms，支持1万行项模型单次计算耗时<100ms | 满足性能指标 |
| 可移植性测试 | - | 剥离所有外部依赖后可独立运行测试 | 无外部依赖泄漏 |

### 测试工具
- 无需依赖外部测试环境，所有测试用例可本地直接运行
- 契约校验使用`public/pre_generated_mock/contract_validator.py`工具自动校验
---
## 5. 原子化TODO执行清单
| 序号 | 任务内容 | 预估工时 | 验收标准 | 责任人 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 1 | 初始化模块目录结构，导入模块专属规则文件 | 0.5h | 目录符合全局架构要求，rule文件已放置到对应位置 | 开发工程师 | pending |
| 2 | 实现核心数据结构：DomainEvent、RolePermission、LineItem、FinancialModelSnapshot等 | 2h | 所有结构与public/schema契约完全一致，无自定义字段 | 开发工程师 | pending |
| 3 | 实现权限规则校验逻辑：角色权限匹配、数据范围校验 | 4h | 覆盖所有角色的权限校验场景，越权场景100%拦截 | 开发工程师 | pending |
| 4 | 实现财务核心计算逻辑：行项公式校验、DAG依赖计算、维度聚合计算 | 16h | 所有财务规则均实现，单元测试覆盖率100% | 财务业务专家+开发工程师 | pending |
| 5 | 实现validate_command核心接口 | 2h | 命令合法性、权限校验逻辑覆盖所有场景 | 开发工程师 | pending |
| 6 | 实现apply_event核心接口 | 4h | 事件应用逻辑正确，无副作用，所有状态变更通过该方法实现 | 开发工程师 | pending |
| 7 | 定义所有对外抽象端口：存储端口、AI服务端口、消息端口等 | 2h | 所有端口为纯抽象接口，无实现代码，入参出参均为核心层标准结构 | 架构师 | pending |
| 8 | 编写单元测试，覆盖所有业务场景 | 8h | 单元测试覆盖率100%，所有用例通过 | 测试工程师 | pending |
| 9 | 性能测试与优化 | 2h | 满足性能指标要求 | 开发工程师 | pending |
| 10 | 文档补齐：接口文档、规则说明、变更记录 | 2h | 文档完整准确，无遗漏 | 开发工程师 | pending |
---
## 6. IDE规则配置文件
### 6.1 Trae IDE 规则：`.trae/rules/module_0_rule.json`
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
    "denied": ["modules/!(模块0_领域核心层)/**", "**/*.jar", "**/*.dll"]
  },
  "rules": [
    {
      "id": "M001",
      "name": "沙盒隔离",
      "description": "仅允许读写当前模块目录，禁止访问其他模块文件",
      "enforcement": "block"
    },
    {
      "id": "M002",
      "name": "无外部依赖约束",
      "description": "禁止引入任何外部组件依赖，仅允许使用标准库与public下的资源",
      "enforcement": "block",
      "check_patterns": ["import * from *", "require(*)", "implementation(*)"],
      "exclude_patterns": ["import * from public/**", "import 标准库"]
    },
    {
      "id": "M003",
      "name": "契约校验",
      "description": "所有接口、数据结构必须符合public下的契约定义",
      "enforcement": "check",
      "pre_commit_hook": "public/pre_generated_mock/contract_validator.py"
    },
    {
      "id": "M004",
      "name": "测试要求",
      "description": "提交代码前必须运行所有单元测试，覆盖率不低于100%",
      "enforcement": "check",
      "pre_commit_hook": "pytest --cov=modules/模块0_领域核心层 --cov-fail-under=100"
    }
  ]
}
```
### 6.2 Cursor IDE 规则：`.cursor/rules/module_0_rule.md`
```md
# Cursor 开发规则 - 领域核心层（模块0）
> 优先级最高，所有代码生成必须严格遵守以下规则

1. 【范围约束】仅能读写`modules/模块0_领域核心层/`目录下的文件，禁止访问其他模块的任何代码/资源
2. 【依赖约束】禁止引入任何外部依赖（框架、中间件SDK、第三方库），仅允许使用语言标准库和`public/`目录下的契约、Mock资源
3. 【契约约束】所有接口、数据结构必须100%匹配`public/schema/`和`public/interface_stub/`下的契约定义，禁止自定义字段/接口
4. 【逻辑约束】所有业务逻辑必须为纯函数，无副作用，相同输入永远返回相同输出
5. 【路径约束】禁止使用相对路径（如`../../`），必须使用动态路径推导
6. 【测试约束】生成代码时必须同步生成对应的单元测试用例，覆盖正常/边界/异常场景
7. 【异常约束】只能抛出核心层定义的标准异常，禁止抛出外部组件异常或通用RuntimeException
```
---
## 7. 模块状态模板（`module_status.json`）
```json
{
  "module_id": "0",
  "module_name": "领域核心层",
  "status": "planning",
  "progress": 0,
  "last_updated": "2024-xx-xxTxx:xx:xxZ",
  "dependencies": [],
  "issues": [
    {
      "issue_id": "",
      "type": "",
      "description": "",
      "status": "",
      "created_at": "",
      "resolved_at": ""
    }
  ],
  "owner": "",
  "version": "1.0.0"
}
```
> status枚举：planning/developing/testing/ready_for_merge/merged
---
## 8. 异常上报标准化规则
### 8.1 异常分类
| 异常类型 | 描述 |
| --- | --- |
| contract_violation | 接口/数据结构违反public契约定义 |
| dependency_error | 引入了外部依赖或其他模块内部代码 |
| test_failure | 单元测试/契约测试/性能测试不通过 |
| performance_degradation | 核心接口性能低于指标要求 |

### 8.2 上报格式
```json
{
  "exception_id": "uuid",
  "module_id": "0",
  "module_name": "领域核心层",
  "type": "contract_violation",
  "trigger_time": "2024-xx-xxTxx:xx:xxZ",
  "trigger_position": "文件路径+行号",
  "error_msg": "错误描述",
  "context": "上下文数据",
  "reporter": "上报人",
  "level": "critical/major/minor"
}
```

### 8.3 自动触发上报条件
1. 代码提交前pre-commit hook校验不通过时自动上报
2. CI流水线测试不通过时自动上报
3. 性能监控指标低于阈值时自动上报

### 8.4 处理流程
1. 异常上报后自动分配给模块负责人
2. 负责人必须在24小时内响应，定位问题根因
3. 修复后必须重新运行所有测试，确认问题解决后关闭异常
4. 所有异常处理记录必须归档到`.trae/documents/`目录下留存
---
> 本引导包所有规则优先级高于任何临时需求，修改必须经过架构评审后更新。
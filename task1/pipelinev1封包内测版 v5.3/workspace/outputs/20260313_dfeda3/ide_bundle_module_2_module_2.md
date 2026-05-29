# 垂直业务切片层IDE引导包
模块ID：2 | 关联范式：垂直内聚与直觉实用 | 依赖模块：领域核心层、事件驱动核心层

---

## 1. 模块功能说明
### 核心职责
按业务特性划分4个独立可迭代的业务切片，每个切片包含完整的请求处理、业务编排、单元测试能力，切片之间完全解耦：
| 切片名称 | 职责范围 |
|---------|---------|
| 财务计算切片 | 财务模型计算触发、计算范围控制、计算状态流转编排 |
| AI辅助切片 | AI建议请求转发、建议合规校验、用户确认逻辑编排 |
| 权限管控切片 | 用户权限查询、权限变更申请处理、数据范围校验 |
| 报表导出切片 | 导出参数校验、数据筛选、导出任务调度、进度通知 |

### 核心特性
- 切片独立迭代：新增/修改/下线功能仅需操作对应切片目录，不影响其他模块
- 物理隔离：切片数据独立存储，禁止跨切片直接读写内部数据
- 低认知成本：按业务域组织代码，开发者仅需关注对应切片的业务逻辑

---

## 2. 模块接口规范
所有接口严格匹配`public/interface_stub/`下的`VerticalFeatureModule`契约定义，禁止私自修改参数/返回值结构：
### 对外暴露接口
| 接口名称 | 入参 | 返回值 | 异常 |
|---------|------|--------|------|
| export_financial_report | model_id: str, report_type: str, filters: Optional[Dict] | Awaitable[bytes] | ResourceNotFoundError、PermissionDeniedError、ValidationError |
| get_ai_suggestion | feature_type: str, user_prompt: str, model_context: Dict | AISuggestion | ValidationError、RuntimeError |

### 内部切片交互规范
- 切片之间仅可通过领域事件或领域层抽象接口交互，禁止直接导入其他切片的内部实现
- 所有跨切片请求必须通过事件驱动核心层的`dispatch_command`接口发送命令触发

### 数据约束
所有读写数据必须符合`public/schema/`下的数据契约定义，禁止写入不符合契约格式的数据

---

## 3. 模块开发指南
### 目录结构
```
modules/模块2_垂直业务切片层/
├── financial-calc/          # 财务计算切片
│   ├── handler/             # 请求处理器
│   ├── orchestration/       # 用例编排逻辑
│   └── tests/               # 单元测试
├── ai-assist/               # AI辅助切片
│   ├── handler/
│   ├── orchestration/
│   └── tests/
├── access-control/          # 权限管控切片
│   ├── handler/
│   ├── orchestration/
│   └── tests/
├── report-export/           # 报表导出切片
│   ├── handler/
│   ├── orchestration/
│   └── tests/
├── module_2_rules.md        # 模块专属规则
├── module_2_rules.json
└── module_status.json       # 模块开发状态
```

### 编码规范
1. **依赖导入规则**：仅允许从`public/pre_generated_mock/`导入其他模块的Mock实现，禁止直接导入其他模块的内部代码
```python
# 正确示例
from public.pre_generated_mock.mock_module0 import DomainCoreModule
from public.pre_generated_mock.mock_module1 import EventStreamCoreModule

# 错误示例（禁止）
# from modules.模块0_领域核心层 import DomainCoreModule
```
2. **路径规则**：禁止使用相对路径寻址，必须用`os.path.dirname(os.path.abspath(__file__))`动态推导目录
3. **切片隔离规则**：每个切片的代码仅允许在自身目录下存在，禁止跨切片共享代码

---

## 4. 模块测试计划
| 测试类型 | 测试范围 | 要求 |
|---------|---------|------|
| 单元测试 | 每个切片的handler、编排逻辑 | 覆盖率≥90%，使用Mock依赖隔离下层模块，测试用例与业务场景一一对应 |
| 集成测试 | 切片与事件驱动核心层、领域核心层的交互 | 验证接口调用符合契约定义，事件流转正常 |
| 契约测试 | 对外暴露接口 | 100%匹配`public/interface_stub`的接口定义，所有参数/返回值/异常符合契约 |
| 隔离测试 | 切片之间的交互 | 验证切片之间不会直接调用内部实现，仅通过事件/领域接口交互 |

### 测试执行流程
1. 每个切片开发完成后先执行自身单元测试，通过后再提交
2. 模块整体提测前执行全量集成测试与契约测试
3. 禁止依赖其他切片的测试用例，每个切片的测试用例独立可执行

---

## 5. 原子化TODO执行清单
| 优先级 | 任务内容 | 依赖 | 预计耗时 | 验收标准 |
|-------|---------|------|----------|----------|
| P0 | 初始化模块目录结构，创建4个切片的子目录与handler/orchestration/tests目录 | 无 | 0.5h | 目录结构符合开发指南要求 |
| P0 | 实现权限管控切片的handler与编排逻辑，完成单元测试 | 领域核心层Mock、事件驱动核心层Mock | 8h | 单元测试覆盖率≥90%，权限校验逻辑符合业务规则 |
| P0 | 实现财务计算切片的handler与编排逻辑，完成单元测试 | 领域核心层Mock、事件驱动核心层Mock | 10h | 计算触发、状态流转逻辑正常，单元测试覆盖率≥90% |
| P1 | 实现报表导出切片的handler与编排逻辑，完成单元测试 | 领域核心层Mock、事件驱动核心层Mock | 8h | 导出参数校验、任务调度正常，单元测试覆盖率≥90% |
| P1 | 实现AI辅助切片的handler与编排逻辑，完成单元测试 | 领域核心层Mock、事件驱动核心层Mock | 12h | AI建议请求转发、合规校验逻辑正常，单元测试覆盖率≥90% |
| P2 | 完成模块集成测试与契约测试 | 4个切片功能开发完成 | 6h | 所有测试用例通过，接口完全符合契约定义 |
| P2 | 切片隔离性验证 | 4个切片功能开发完成 | 2h | 切片之间无直接内部调用，符合隔离要求 |

---

## 6. IDE规则配置文件
### 6.1 Trae IDE规则（.trae/rules/module_2_rule.json）
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
      "id": "M2001",
      "name": "沙盒隔离",
      "description": "仅允许读写当前模块目录，禁止访问其他模块的代码文件",
      "enforcement": "strict"
    },
    {
      "id": "M2002",
      "name": "Mock依赖约束",
      "description": "仅允许从public/pre_generated_mock导入其他模块的Mock实现，禁止直接导入其他模块的内部代码",
      "enforcement": "strict"
    },
    {
      "id": "M2003",
      "name": "切片隔离约束",
      "description": "切片之间禁止直接调用内部实现，仅可通过事件或领域层抽象接口交互",
      "enforcement": "strict"
    },
    {
      "id": "M2004",
      "name": "契约合规约束",
      "description": "所有接口、数据结构必须符合public目录下的契约定义，禁止私自修改契约",
      "enforcement": "strict"
    },
    {
      "id": "M2005",
      "name": "渐进式开发约束",
      "description": "禁止大批量生成代码，每完成一个切片的开发与测试后再进行下一个切片的开发",
      "enforcement": "warning"
    }
  ]
}
```

### 6.2 Cursor IDE规则（.cursor/rules/module_2_rule.md）
```md
# 垂直业务切片层开发规则（最高优先级）
## 可操作范围
✅ 仅允许修改 `modules/模块2_垂直业务切片层/` 目录下的文件
✅ 仅允许读取 `public/` 目录下的契约、Mock资源
❌ 禁止读取/修改其他模块的任何文件

## 编码规则
1. 依赖只能从 `public/pre_generated_mock/` 导入，禁止直接导入其他模块的内部代码
2. 切片之间禁止直接调用内部实现，跨切片交互必须通过事件或领域层接口
3. 所有接口、数据结构必须严格匹配public目录下的契约定义，禁止私自修改
4. 禁止使用相对路径寻址，必须用`os.path.dirname(os.path.abspath(__file__))`动态推导目录
5. 禁止大批量生成代码，每个切片开发完成并测试通过后再进行下一个切片的开发

## 测试规则
1. 每个切片必须包含对应的单元测试，覆盖率不低于90%
2. 所有测试用例必须使用Mock依赖，不依赖其他模块的真实实现
```

---

## 7. 模块状态模板（module_status.json）
```json
{
  "module_id": "2",
  "module_name": "垂直业务切片层",
  "status": "planning",
  "progress": 0,
  "last_updated": "2024-xx-xxTxx:xx:xxZ",
  "dependencies": [
    {
      "module_id": "0",
      "module_name": "领域核心层",
      "required_status": "ready_for_merge"
    },
    {
      "module_id": "1",
      "module_name": "事件驱动核心层",
      "required_status": "ready_for_merge"
    }
  ],
  "issues": []
}
```
### 字段说明
- status枚举：planning（规划中）、developing（开发中）、testing（测试中）、ready_for_merge（待合并）、merged（已合并）
- progress：0-100，按TODO完成进度计算
- issues：存储当前模块的问题、风险、待优化项

---

## 8. 异常上报标准化规则
### 异常分类
| 异常类型 | 定义 | 触发条件 |
|---------|------|----------|
| contract_violation | 契约违反 | 接口参数/返回值不符合契约、数据格式不符合schema定义 |
| dependency_error | 依赖错误 | 依赖的Mock/真实服务不可用、接口调用失败 |
| test_failure | 测试失败 | 单元测试/集成测试/契约测试用例未通过 |
| performance_degradation | 性能降级 | 接口响应超时、导出耗时超过阈值、并发处理能力不达标 |

### 上报格式
```json
{
  "exception_type": "contract_violation",
  "module_id": "2",
  "slice_name": "report-export",
  "timestamp": "2024-xx-xxTxx:xx:xxZ",
  "error_msg": "导出接口返回值不符合契约定义，缺少report_id字段",
  "trigger_scene": "调用export_financial_report接口，入参model_id=model_001，report_type=Excel",
  "stack_trace": "xxx",
  "contact": "开发者姓名"
}
```

### 异常处理流程
1. 上报异常后先检查`public`目录下的契约是否有更新，确认是代码问题还是契约变更
2. 契约违反异常优先修复代码适配契约，禁止私自修改契约
3. 依赖错误异常优先检查Mock配置，确认依赖模块是否已发布可用版本
4. 所有异常修复完成后必须补充对应的测试用例，避免重复出现
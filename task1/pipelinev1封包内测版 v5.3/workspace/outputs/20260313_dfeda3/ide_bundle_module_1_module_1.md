# 事件驱动核心层IDE引导包
> 模块ID：1 | 关联范式：数据流转与状态驱动 | 依赖模块：领域核心层

---

## 1. 模块功能说明
### 1.1 模块定位
事件驱动核心层是整个系统的数据流中枢，承接垂直业务切片层的命令请求，对接领域核心层的业务规则，负责全链路事件的生成、流转、计算、持久化，是实现单向数据流、不可变状态、并发安全的核心载体。
### 1.2 核心职责
| 职责项 | 说明 |
|--------|------|
| 命令校验 | 对接领域核心层规则，校验命令合法性、操作者权限 |
| 事件生成 | 基于合法命令生成符合契约的不可变领域事件 |
| DAG重算引擎 | 基于JGraphT实现依赖关系图计算，支持增量/全量重算 |
| 事件批处理 | 合并级联计算产生的事件，避免事件风暴 |
| 快照管理 | 定期生成模型快照，避免全量事件重放的性能损耗 |
| 冲突合并 | 处理并发操作的乐观锁冲突，保障数据一致性 |
| 事件向上转型 | 兼容历史版本事件Schema，支持平滑迭代 |
### 1.3 核心价值
- 从根源解决并发编辑冲突、数据溯源问题
- 保障所有状态变更可追溯、可回滚、可审计
- 实现数据流全链路可控，避免隐式状态变更

---

## 2. 模块接口规范
> 所有接口必须严格匹配`public/interface_stub/`中的契约定义，入参出参必须通过`public/schema/`的数据校验
### 2.1 接口列表
| 接口名称 | 签名 | 说明 | 抛出异常 |
|----------|------|------|----------|
| dispatch_command | `def dispatch_command(self, command: Command, jwt_token: str) -> Awaitable[CommandReceipt]` | 统一命令入口，包含鉴权、校验、事件生成、持久化、重算全流程 | AuthenticationError、PermissionDeniedError、ValidationError、OperationConflictError |
| stream_model_updates | `def stream_model_updates(self, model_id: str, client_version: int) -> AsyncGenerator[StatePatch, None]` | 建立长连接推送增量状态更新 | ResourceNotFoundError、PermissionDeniedError |
| calculate_model | `def calculate_model(self, model_id: str, calculation_scope: CalculationScopeEnum) -> Dict[str, Any]` | 触发模型重算，支持异步任务执行 | ResourceNotFoundError、ValidationError |
### 2.2 数据契约约束
- 所有事件必须继承`DomainEvent`基础结构，字段严格符合`public/schema/contract_snapshot_1.0.0.json`定义
- 快照版本号必须与事件版本号严格对齐，禁止出现版本断层
- 事件生成后不可修改，所有状态变更必须通过事件叠加生成

---

## 3. 模块开发指南
### 3.1 目录结构建议
```
modules/模块1_事件驱动核心层/
├── validator/          # 命令校验组件
├── event_generator/    # 事件生成组件
├── engine/             # DAG重算引擎
├── batch_processor/    # 事件批处理组件
├── snapshot_manager/   # 快照管理组件
├── conflict_resolver/  # 冲突合并组件
├── event_upcaster/     # 事件向上转型组件
├── impl/               # 对外接口实现
├── tests/              # 单元/集成测试用例
├── module_1_rules.md   # 模块专属规则（只读）
├── module_1_rules.json # 模块专属规则（只读）
└── module_status.json  # 模块开发状态
```
### 3.2 开发约束
1. **沙盒隔离**：仅允许读写当前模块目录下的文件，禁止访问其他模块的代码/规则文件
2. **依赖约束**：仅可从`public/pre_generated_mock/`导入领域核心层的Mock实现，禁止直接导入领域核心层的业务代码
3. **数据流约束**：所有状态变更必须由事件触发，禁止直接修改读模型快照
4. **路径约束**：禁止使用相对路径寻址（如`../../`），必须通过`os.path.dirname(os.path.abspath(__file__))`动态推导目录
5. **技术栈约束**：核心流处理使用Reactor Flux，DAG计算使用JGraphT，禁止引入额外的重型中间件
### 3.3 依赖导入规范
```python
# 正确示例
from public.pre_generated_mock.mock_module0 import DomainCoreModule
# 错误示例（禁止）
# from modules.模块0_领域核心层 import DomainCoreModule
```

---

## 4. 模块测试计划
| 测试类型 | 测试范围 | 验收标准 |
|----------|----------|----------|
| 单元测试 | 命令校验、事件生成、DAG重算、冲突合并、快照管理等原子组件 | 覆盖率≥90%，覆盖所有边界case、异常场景 |
| 集成测试 | 完整数据流：命令提交→事件生成→DAG重算→快照更新→增量推送 | 100%符合业务规则，无数据不一致、版本冲突问题 |
| 性能测试 | 并发吞吐量、重算耗时、快照生成耗时 | 单模型1000行项增量重算耗时≤100ms，支持1000QPS并发写入无异常 |
| 兼容性测试 | 事件向上转型能力 | 兼容3个历史版本的事件Schema，重放无异常 |

---

## 5. 原子化TODO执行清单
| 优先级 | 任务描述 | 依赖 | 预计工时 | 验收标准 |
|--------|----------|------|----------|----------|
| P0 | 创建模块标准目录结构，完成初始化配置 | 无 | 0.5天 | 目录结构符合规范，模块规则文件已放置 |
| P0 | 实现命令校验组件，对接领域核心层`validate_command`接口 | 任务1 | 1天 | 所有合法/非法命令校验结果符合预期，权限校验正确 |
| P0 | 实现事件生成组件，按契约生成不可变领域事件 | 任务2 | 1天 | 生成的事件100%符合数据契约要求，字段无缺失 |
| P0 | 集成JGraphT实现DAG重算引擎，支持增量/全量计算 | 任务3 | 2天 | 依赖计算正确，无漏算、错算问题 |
| P1 | 实现事件批处理组件，合并级联计算事件 | 任务4 | 1天 | 相同类型的级联事件合并率≥80%，无事件重复 |
| P1 | 实现快照管理组件，支持快照生成、加载、版本对齐 | 任务4 | 1.5天 | 快照版本与事件版本严格对齐，加载速度比全量重放快10倍以上 |
| P1 | 实现冲突合并组件，处理并发操作乐观锁冲突 | 任务6 | 1天 | 并发冲突场景下无数据覆盖，用户可选择合并版本 |
| P1 | 实现事件向上转型组件，兼容旧版本事件Schema | 任务3 | 0.5天 | 历史版本事件重放无异常，数据无丢失 |
| P0 | 实现三个对外接口，完成全流程串联 | 任务4-8 | 2天 | 接口符合契约定义，全流程跑通 |
| P0 | 补全单元/集成测试用例 | 任务9 | 2天 | 测试覆盖率≥90%，所有用例通过 |
| P1 | 性能调优，满足性能指标要求 | 任务10 | 1天 | 符合性能测试验收标准 |

---

## 6. IDE规则配置文件
### 6.1 Trae IDE规则：.trae/rules/module_1_rule.json
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
      "description": "仅允许读写当前模块目录，禁止访问其他模块代码",
      "enforcement": "strict"
    },
    {
      "id": "M002",
      "name": "Mock依赖",
      "description": "仅允许从public/pre_generated_mock导入其他模块Mock，禁止直接导入其他模块代码",
      "enforcement": "strict"
    },
    {
      "id": "M003",
      "name": "数据流约束",
      "description": "所有状态变更必须由事件触发，禁止直接修改读模型快照",
      "enforcement": "strict"
    },
    {
      "id": "M004",
      "name": "契约合规",
      "description": "所有接口、数据结构必须符合public下的契约定义",
      "enforcement": "strict"
    },
    {
      "id": "M005",
      "name": "测试要求",
      "description": "单元测试覆盖率必须≥90%，所有功能必须有对应的测试用例",
      "enforcement": "strict"
    }
  ]
}
```
### 6.2 Cursor IDE规则：.cursor/rules/module_1_rule.md
```md
# 事件驱动核心层Cursor开发规则
> 优先级最高，所有代码生成、修改必须严格遵守本规则

## 核心约束
1. **可操作范围**：仅允许修改`modules/模块1_事件驱动核心层/`下的文件，禁止修改其他模块、public目录下的任何内容
2. **依赖规则**：依赖其他模块只能从`public/pre_generated_mock/`导入，禁止直接导入其他模块的代码
3. **数据流规则**：所有状态变更必须通过事件触发，绝对禁止直接修改快照数据
4. **契约规则**：所有接口、数据结构必须严格匹配`public/schema/`和`public/interface_stub/`的定义，不得自定义字段、修改签名
5. **路径规则**：禁止使用相对路径寻址，必须用动态方式推导目录路径

## 编码要求
1. 核心流处理使用Reactor Flux实现，DAG计算使用JGraphT
2. 事件必须是不可变对象，生成后不得修改
3. 所有异常必须符合契约定义的异常类型，不得抛出自定义异常到上层
4. 单元测试必须覆盖所有分支、异常场景，覆盖率≥90%
```

---

## 7. 模块状态模板：module_status.json
```json
{
  "module_id": "1",
  "module_name": "事件驱动核心层",
  "status": "planning",
  "status_enum": ["planning", "developing", "testing", "ready_for_merge", "merged"],
  "progress": 0,
  "last_updated": "2024-xx-xxTxx:xx:xxZ",
  "dependencies": [
    {
      "module_id": "0",
      "module_name": "领域核心层",
      "required_status": "ready_for_merge"
    }
  ],
  "issues": [],
  "owner": "",
  "version": "1.0.0"
}
```

---

## 8. 异常上报标准化规则
### 8.1 异常分类
| 异常类型 | 说明 | 优先级 |
|----------|------|--------|
| contract_violation | 违反数据契约/接口契约定义 | P0 |
| dependency_error | 依赖加载失败、依赖返回异常 | P0 |
| test_failure | 测试用例不通过、覆盖率不达标 | P1 |
| performance_degradation | 性能指标低于阈值 | P1 |
### 8.2 上报格式
```json
{
  "report_id": "uuid",
  "module_id": "1",
  "module_name": "事件驱动核心层",
  "exception_type": "contract_violation|dependency_error|test_failure|performance_degradation",
  "timestamp": "ISO8601格式时间",
  "detail": "异常详情描述",
  "context": "相关上下文（堆栈、参数、性能指标等）",
  "reporter": "上报人/系统标识"
}
```
### 8.3 自动上报触发条件
1. 契约校验失败（入参/出参不符合public下的契约定义）
2. 单元测试通过率<90%
3. DAG重算耗时超过100ms/1000行项
4. 依赖加载失败（无法获取领域核心层Mock实例）
5. 检测到直接修改快照的代码
### 8.4 异常处理流程
1. 异常触发后自动写入`.trae/issues/`目录，生成唯一issue编号
2. P0异常自动分配给模块负责人，1小时内响应
3. 负责人修复后提交验证，验证通过后关闭issue，更新`module_status.json`
4. 所有issue记录永久归档，作为迭代历史追溯依据
5. 同一异常出现3次以上必须输出根因分析报告，更新模块规则避免重复发生

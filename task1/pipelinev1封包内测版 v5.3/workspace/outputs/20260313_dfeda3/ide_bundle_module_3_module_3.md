# 防腐适配器层 IDE 引导包
## 1. 模块功能说明
### 基础信息
| 项 | 值 |
| --- | --- |
| 模块ID | 3 |
| 模块名称 | 防腐适配器层 |
| 关联架构范式 | 边界防腐与高度解耦 |
| 依赖模块 | 领域核心层（模块0） |
| 上层调用方 | 事件驱动核心层、垂直业务切片层 |

### 核心职责
实现领域核心层定义的所有抽象端口，对接外部组件（大模型、存储、消息队列、Excel工具、权限组件），完全屏蔽外部组件的差异、异常、结构变更，上层业务模块无需感知外部组件的替换/升级。
### 架构价值
- 降低外部组件变更对核心业务的影响：替换大模型厂商、存储组件仅需修改对应适配器，上层代码零改动
- 统一外部异常处理：所有外部组件的异常统一转换为上层约定的标准异常，避免异常泄漏
- 支撑信创改造、组件替换需求：无需重构核心业务即可完成外部组件的国产化替换
---
## 2. 模块接口规范
所有接口必须100%匹配`public/interface_stub/`下的契约定义，禁止私自修改接口签名、参数、返回值。
### 接口列表
| 接口名称 | 签名 | 功能描述 | 异常抛出 |
| --- | --- | --- | --- |
| ai_service_port | `def ai_service_port(self, feature_type: str, user_prompt: str, model_context: Dict[str, Any]) -> AISuggestion` | 统一AI能力接口，屏蔽OpenAI/豆包等厂商差异 | RuntimeError（第三方大模型调用失败） |
| financial_model_repository_port | `def financial_model_repository_port(self, query_condition: Dict[str, Any]) -> Any` | 财务模型存储查询接口，屏蔽PostgreSQL/Redis等存储差异 | ResourceNotFoundError（资源不存在）、IOError（存储读写失败） |
| save_events | `def save_events(self, events: List[DomainEvent]) -> bool` | 批量保存领域事件到持久化存储 | IOError（存储写入失败） |
| save_snapshot | `def save_snapshot(self, snapshot: FinancialModelSnapshot) -> bool` | 保存财务模型快照 | IOError（存储写入失败） |
### 数据契约约束
所有输入输出数据必须符合`public/schema/contract_snapshot_1.0.0.json`中定义的结构，禁止传递未定义的字段、枚举值。
---
## 3. 模块开发指南
### 沙盒约束
✅ 仅允许读写`modules/模块3_防腐适配器层/`目录下的文件<br>
✅ 依赖其他模块仅可导入`public/pre_generated_mock/`下的Mock实现<br>
❌ 禁止读取其他模块的内部代码、规则文件<br>
❌ 禁止直接调用其他模块的内部实现
### 开发边界要求
1. **差异收敛规则**：所有外部组件的参数差异、异常类型、返回结构必须在本层完全转换，禁止将外部组件的原生结构、异常泄漏到上层业务
2. **子模块划分**：按对接的外部组件划分独立子目录，每个子目录对应一类适配器：
   ```
   模块3_防腐适配器层/
   ├── llm/ # 大模型适配：OpenAI、豆包等厂商对接
   ├── persistence/ # 存储适配：PostgreSQL、Redis对接
   ├── excel/ # Excel适配：EasyExcel导入导出对接
   ├── mq/ # 消息队列适配：Kafka对接
   └── permission/ # 权限组件适配：内部权限系统对接
   ```
3. **路径规范**：禁止使用相对路径寻址（如`../../`），必须使用`os.path.dirname(os.path.abspath(__file__))`动态推导目录
### 依赖引入规范
```python
# 正确示例：从公共区导入契约、Mock
from public.interface_stub.anti_corruption_adapter import AntiCorruptionAdapterModule
from public.pre_generated_mock.mock_module0 import DomainCoreModuleMock
# 错误示例（禁止）：直接导入其他模块内部实现
# from modules.模块0_领域核心层 import DomainCoreModule
```
---
## 4. 模块测试计划
### 测试分层
| 测试类型 | 测试范围 | 验收标准 |
| --- | --- | --- |
| 单元测试 | 每个适配器的内部逻辑 | 100%分支覆盖率，mock所有外部依赖，所有异常场景覆盖 |
| 集成测试 | 适配器与外部真实组件的对接 | 所有接口在真实外部组件环境下跑通，成功率100% |
| 契约测试 | 接口与公共契约的一致性 | 所有接口签名、参数、返回值完全匹配public下的契约定义 |
| 替换测试 | 组件切换验证 | 替换同类型外部组件（如从OpenAI切换到豆包）时，上层调用无需修改 |
### 核心测试用例
1. 大模型多厂商适配测试：验证不同厂商的返回结果统一转换为标准AISuggestion结构
2. 存储切换测试：验证切换存储组件时，上层查询接口返回结构完全一致
3. 异常转换测试：验证外部组件抛出的原生异常全部转换为上层约定的标准异常
---
## 5. 原子化TODO执行清单
| 序号 | 任务内容 | 产出物 | 依赖 | 预估耗时 |
| --- | --- | --- | --- | --- |
| 0 | 前置检查：确认领域核心层抽象端口已发布到public/interface_stub | 无 | 模块0状态为ready_for_merge | 0.5h |
| 1 | 搭建模块目录结构，创建各适配器子目录 | 目录结构符合规范 | 0 | 0.5h |
| 2 | 实现适配器基类，统一异常转换逻辑，封装外部异常为标准异常 | adapter_base.py | 1 | 2h |
| 3 | 实现LLM适配器，对接OpenAI、豆包SDK，完成ai_service_port接口 | llm/llm_adapter.py | 2 | 8h |
| 4 | 实现持久化适配器，对接PostgreSQL、Redis，完成存储相关接口 | persistence/pg_adapter.py、persistence/redis_adapter.py | 2 | 12h |
| 5 | 实现Excel适配器，对接EasyExcel，完成导入导出端口 | excel/excel_adapter.py | 2 | 6h |
| 6 | 实现消息适配器，对接Kafka，完成事件发布/订阅端口 | mq/kafka_adapter.py | 2 | 4h |
| 7 | 实现权限适配器，对接内部权限系统，完成权限查询端口 | permission/permission_adapter.py | 2 | 4h |
| 8 | 编写单元测试，覆盖所有适配器的分支场景、异常场景 | tests/unit/目录下测试用例 | 3-7 | 8h |
| 9 | 编写集成测试，验证与真实外部组件的对接 | tests/integration/目录下测试用例 | 8 | 6h |
| 10 | 契约一致性校验，验证所有实现完全匹配公共契约 | 契约校验报告 | 9 | 2h |
| 11 | 性能测试，验证适配器层耗时占比不超过总请求耗时的5% | 性能测试报告 | 10 | 4h |
| 12 | 编写适配器配置说明、组件替换指引 | docs/目录下文档 | 11 | 2h |
---
## 6. IDE规则配置文件
### 6.1 Trae IDE 规则（.trae/rules/module_3_rule.json）
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
      "description": "仅允许读写当前模块目录下的文件，禁止访问其他模块内部资源"
    },
    {
      "id": "M002",
      "name": "Mock依赖",
      "description": "仅允许从public/pre_generated_mock导入其他模块的Mock实现，禁止直接导入其他模块内部代码"
    },
    {
      "id": "M003",
      "name": "差异收敛约束",
      "description": "外部组件的差异、异常、结构必须在本层完全消化，禁止泄漏到上层业务模块"
    },
    {
      "id": "M004",
      "name": "契约校验",
      "description": "所有接口实现必须100%匹配public下的接口、数据契约"
    }
  ]
}
```
### 6.2 Cursor IDE 规则（.cursor/rules/module_3_rule.md）
```md
> 🚨 最高优先级规则，所有代码生成必须100%符合本要求，违反规则的内容自动修正后再输出
# 防腐适配器层开发规则
## 约束范围
仅允许修改`modules/模块3_防腐适配器层/`目录下的文件，禁止修改其他模块的任何内容，禁止读取其他模块的内部代码。
## 依赖规范
1. 依赖其他模块仅可从`public/pre_generated_mock/`导入Mock实现，禁止直接导入其他模块的内部代码
2. 所有接口、数据结构必须从`public/interface_stub/`、`public/schema/`导入，禁止自定义契约
## 开发要求
1. 所有外部组件的参数差异、异常类型、返回结构必须在本层完全转换，禁止将外部原生结构、异常传递到上层
2. 禁止使用相对路径寻址，必须用`os.path.dirname(os.path.abspath(__file__))`动态推导目录
3. 替换外部组件时仅修改对应适配器的实现，禁止修改接口定义
## 测试要求
所有代码提交前必须通过单元测试、契约测试，禁止提交不符合契约的代码。
```
---
## 7. 模块状态模板（module_status.json）
```json
{
  "module_id": "3",
  "module_name": "防腐适配器层",
  "status": "planning",
  "progress": 0,
  "last_updated": "2024-01-01T00:00:00Z",
  "dependencies": [
    {
      "module_id": "0",
      "module_name": "领域核心层",
      "required_status": "ready_for_merge",
      "current_status": "planning"
    }
  ],
  "issues": []
}
```
### 字段说明
| 字段 | 枚举值/说明 |
| --- | --- |
| status | planning（规划中）、developing（开发中）、testing（测试中）、ready_for_merge（待合并）、merged（已合并） |
| progress | 0-100的整数，对应TODO清单的完成进度 |
| issues | 记录当前模块的阻塞问题、待修复缺陷 |
---
## 8. 异常上报标准化规则
### 异常分类
| 异常类型 | 触发场景 | 严重程度 |
| --- | --- | --- |
| contract_violation | 接口签名/返回值不符合契约、数据结构不符合数据契约 | P0 |
| dependency_error | 外部组件调用超时、连接失败、返回未知异常 | P1 |
| test_failure | 单元/集成/契约测试用例执行失败 | P1 |
| performance_degradation | 适配器平均耗时超过100ms、并发吞吐量低于阈值 | P2 |
### 上报格式
```json
{
  "event_id": "UUID",
  "module_id": "3",
  "error_type": "contract_violation",
  "timestamp": "2024-01-01T00:00:00Z",
  "severity": "P0",
  "context": {
    "interface_name": "ai_service_port",
    "params": {},
    "external_component": "openai"
  },
  "stack_trace": "异常堆栈信息",
  "description": "返回值缺少compliance_flag字段，违反契约要求"
}
```
### 自动上报触发条件
1. 接口返回值与契约校验不通过时自动上报
2. 外部组件调用失败率超过1%时自动上报
3. 测试流水线执行失败时自动上报
4. 监控指标超过阈值时自动上报
### 异常处理流程
1. 自动上报到监控平台，P0级异常立即触发告警通知模块负责人
2. 阻断非幂等操作的执行，避免脏数据产生
3. 开发人员24h内排查根因，修复后重新走测试流程
4. 修复完成后更新module_status.json的issues字段，记录问题原因、解决方案
5. 若涉及契约变更，必须先提交架构组评审，更新public下的契约后再修改代码

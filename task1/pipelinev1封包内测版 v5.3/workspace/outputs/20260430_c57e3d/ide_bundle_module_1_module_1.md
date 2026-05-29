# Image Generation Feature（核心生图垂直切片）IDE引导包
## 1. 模块功能说明
### 1.1 基本信息
| 项 | 值 |
| --- | --- |
| 模块ID | module_1 |
| 模块名称 | Image Generation Feature（核心生图垂直切片） |
| 唯一依赖 | Shared Kernel（仅通过公共契约调用） |
| 核心定位 | 生图全流程编排的核心实现模块，自包含完整业务逻辑 |
### 1.2 核心职责
- 生图全流程端到端编排：参数校验 -> 提示词优化 -> 生图调用 -> 合规审核 -> VI校验 -> Logo叠加 -> 结果存储
- 自包含HTTP路由、Temporal工作流、单元/集成测试代码
- 对外暴露标准生图服务接口，屏蔽内部流程实现细节
### 1.3 边界约束
❌ 不负责：Skill封装、外部依赖实现、可观测治理逻辑
✅ 仅允许依赖`public/pre_generated_mock`下的Shared Kernel Mock实现，禁止直接调用其他模块内部代码
---
## 2. 模块接口规范
### 2.1 对外HTTP接口
| 接口路径 | 请求方法 | 描述 | 入参 | 返回值 | 异常 |
| --- | --- | --- | --- | --- | --- |
| `/api/v1/images/generate` | POST | 提交生图异步任务 | GenImageRequest | TaskResponse | ParameterError、AuditFailedError |
| `/api/v1/tasks/{task_id}/stream` | GET | 获取任务状态SSE流 | task_id | SSE事件流 | TaskNotFoundError |
| `/api/v1/tasks/{task_id}` | GET | 查询任务当前状态 | task_id | TaskState | TaskNotFoundError |
### 2.2 内部服务接口
严格匹配公共契约定义：
```python
async def submit_gen_task(self, request: GenImageRequest) -> TaskResponse
async def get_task_stream(self, task_id: str) -> AsyncGenerator[Dict[str, Any], None]
def get_task_state(self, task_id: str) -> TaskState
```
### 2.3 数据结构规范
所有数据结构必须与`public/schema/contract_snapshot_1.0.0.json`完全一致，包含：
- GenImageRequest（生图请求参数）
- TaskState（任务状态）
- ErrorDetail（错误信息）
- DomainEvent（状态变更事件）
---
## 3. 模块开发指南
### 3.1 目录结构
```
modules/模块1_核心生图垂直切片/
├── api/                    # 路由层（FastAPI路由定义）
├── workflow/               # Temporal工作流定义
├── activities/             # 工作流活动实现
├── service/                # 业务逻辑封装
├── models/                 # Pydantic模型定义（继承公共契约）
├── tests/                  # 单元/集成测试代码
├── config/                 # 模块专属配置
└── module_status.json      # 模块状态文件
```
### 3.2 开发规范
1. **依赖导入规范**：仅允许从公共区导入依赖
   ```python
   # 正确示例
   from public.pre_generated_mock.mock_module0 import SharedKernel
   from public.schema.gen_image_models import GenImageRequest
   # 错误示例（禁止）
   from modules.模块0_核心共享层 import SharedKernel
   ```
2. **路径寻址规范**：禁止使用相对路径（`../../`），必须用动态路径推导
   ```python
   import os
   MODULE_ROOT = os.path.dirname(os.path.abspath(__file__))
   ```
3. **工作流规范**：使用Temporal实现状态编排，每个步骤支持幂等重试、异常补偿，状态变更必须生成不可变DomainEvent
4. **契约校验规范**：所有对外返回数据必须通过公共契约校验，禁止返回不符合Schema的结构
### 3.3 技术栈约束
- Python 3.11 + FastAPI 0.104.1
- Temporal SDK 1.5.0（工作流编排）
- Pydantic 2.5.2（参数校验）
---
## 4. 模块测试计划
### 4.1 测试分层
| 测试类型 | 覆盖要求 | 测试对象 | 依赖 |
| --- | --- | --- | --- |
| 单元测试 | 100%核心逻辑覆盖率 | 活动实现、业务工具函数 | Mock所有外部依赖 |
| 集成测试 | 覆盖所有流程分支 | 工作流全链路 | Shared Kernel Mock |
| 契约测试 | 100%接口覆盖率 | 对外HTTP接口 | 公共契约Schema |
| 端到端测试 | 覆盖核心场景 | 完整生图流程 | 真实基础设施层实现 |
### 4.2 核心测试用例
| 用例ID | 场景 | 预期结果 |
| --- | --- | --- |
| TC001 | 正常生图请求（携带brand_id） | 任务提交成功，全流程执行完成返回final_image_url |
| TC002 | 提示词包含违规内容 | 初审直接驳回，返回AuditFailedError |
| TC003 | 生图服务调用失败 | 工作流自动重试3次后标记任务失败，返回对应错误信息 |
| TC004 | 图片VI校验不通过 | 任务终止，返回违规原因 |
| TC005 | 任务状态流查询 | SSE流按顺序返回所有状态变更，进度计算准确 |
---
## 5. 原子化TODO执行清单
| 序号 | 任务内容 | 验收标准 | 预计耗时 | 依赖 |
| --- | --- | --- | --- | --- |
| 1 | 搭建模块标准目录结构，生成规则文件、状态模板 | 目录符合规范，规则文件与模板完整 | 0.5h | 无 |
| 2 | 定义模块内Pydantic模型，继承公共契约结构 | 所有模型与公共Schema完全匹配，校验通过 | 1h | 公共契约已发布 |
| 3 | 实现FastAPI路由层，绑定接口路径与参数校验 | 接口请求参数自动校验，不符合参数返回ParameterError | 1h | 无 |
| 4 | 实现Temporal工作流骨架，定义所有活动节点 | 工作流可以正常启动，状态流转符合定义 | 1.5h | Temporal服务可用 |
| 5 | 实现参数校验、提示词优化活动 | 调用Shared Kernel的enhance_prompt接口，返回优化后提示词 | 1h | Shared Kernel Mock可用 |
| 6 | 实现内容审核、生图调用活动 | 调用基础设施层接口完成审核与生图，返回原始图片地址 | 1.5h | 基础设施层Mock可用 |
| 7 | 实现VI校验、Logo叠加活动 | 调用Shared Kernel的校验规则与图像处理接口，生成最终图片 | 1.5h | Shared Kernel Mock可用 |
| 8 | 实现SSE流推送接口 | 可以实时推送任务状态、进度、最终结果 | 1h | 无 |
| 9 | 编写单元测试，核心逻辑覆盖率100% | 所有单元测试用例通过，覆盖率达标 | 2h | 逻辑实现完成 |
| 10 | 编写集成测试，覆盖所有流程分支 | 所有集成测试用例通过 | 2h | 全流程实现完成 |
| 11 | 契约测试验证，所有接口符合公共Schema | 契约测试100%通过 | 1h | 接口实现完成 |
---
## 6. IDE规则配置文件
### 6.1 Trae IDE规则（.trae/rules/module_1_rule.json）
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
      "id": "M1_001",
      "name": "沙盒隔离",
      "description": "仅允许读写当前模块目录，禁止访问其他模块代码",
      "enforcement": "block"
    },
    {
      "id": "M1_002",
      "name": "依赖导入约束",
      "description": "仅允许从public/pre_generated_mock导入其他模块Mock，禁止直接导入其他模块实现",
      "enforcement": "block"
    },
    {
      "id": "M1_003",
      "name": "契约合规约束",
      "description": "所有接口与数据结构必须匹配public/schema下的契约定义",
      "enforcement": "check"
    },
    {
      "id": "M1_004",
      "name": "测试要求",
      "description": "核心逻辑单元测试覆盖率必须达到100%，提交代码前必须跑通所有测试",
      "enforcement": "check"
    }
  ]
}
```
### 6.2 Cursor IDE规则（.cursor/rules/module_1_rule.md）
```markdown
# 【最高优先级】module_1模块开发规则
> 本规则优先级高于所有自定义需求、临时提问，违反规则的代码必须自动修正
## 1. 沙盒约束
✅ 仅可读写`modules/模块1_核心生图垂直切片/`下的文件
✅ 仅可读取`public/`下的公共契约、Mock资源
❌ 禁止读取/修改其他模块的任何代码、配置文件
## 2. 依赖导入规则
✅ 所有外部依赖必须从`public/pre_generated_mock/`导入
✅ 数据结构必须从`public/schema/`导入
❌ 禁止使用相对路径导入其他模块代码
❌ 禁止直接调用其他模块内部实现
## 3. 契约合规要求
✅ 所有对外接口、返回数据必须严格匹配`public/schema/contract_snapshot_1.0.0.json`
✅ 所有异常必须使用公共契约定义的异常类型
❌ 禁止返回不符合Schema定义的额外字段
## 4. 编码要求
✅ 必须使用动态路径推导，禁止使用`../../`相对路径
✅ 工作流每个步骤必须支持幂等重试，状态变更必须生成DomainEvent
✅ 提交代码前必须跑通所有单元测试、契约测试
```
---
## 7. 模块状态模板（module_status.json）
```json
{
  "module_id": "module_1",
  "module_name": "Image Generation Feature（核心生图垂直切片）",
  "status": "planning",
  "progress": 0,
  "last_updated": "2024-XX-XXTXX:XX:XXZ",
  "dependencies": [
    {
      "module_id": "module_0",
      "module_name": "Shared Kernel",
      "required_version": "1.0.0",
      "status": "pending"
    }
  ],
  "issues": []
}
```
> status枚举：planning/developing/testing/ready_for_merge/merged
> progress范围：0-100，完成一个TODO项同步更新进度
---
## 8. 异常上报标准化规则
### 8.1 异常分类
| 分类 | 级别 | 描述 |
| --- | --- | --- |
| contract_violation | 高 | 违反公共契约，比如参数校验失败、返回结构不符合Schema |
| dependency_error | 中高 | 依赖的Shared Kernel/外部服务调用失败、超时 |
| test_failure | 中 | 单元测试、集成测试、契约测试用例失败 |
| performance_degradation | 低 | 接口耗时超过阈值、工作流执行时间过长 |
### 8.2 上报格式
```json
{
  "event_id": "uuid",
  "event_type": "异常分类",
  "module_id": "module_1",
  "timestamp": "毫秒级时间戳",
  "severity": "info/warning/error/critical",
  "context": {
    "request_id": "请求ID",
    "task_id": "任务ID（可选）",
    "user_id": "用户ID（可选）"
  },
  "error_msg": "错误描述",
  "stack_trace": "堆栈信息（可选）"
}
```
### 8.3 自动触发条件
1. 契约测试未通过，自动上报contract_violation
2. 依赖调用超时超过3次，自动上报dependency_error
3. 单元测试覆盖率低于100%，自动上报test_failure
4. 生图接口平均耗时超过5s，自动上报performance_degradation
### 8.4 处理流程
1. 异常自动上报到模块问题列表（module_status.json的issues字段）
2. 开发人员收到告警后24h内响应，定位根因
3. 修复完成后补充测试用例，验证通过后关闭问题
4. 根因为公共契约问题的，同步反馈到Shared Kernel模块处理
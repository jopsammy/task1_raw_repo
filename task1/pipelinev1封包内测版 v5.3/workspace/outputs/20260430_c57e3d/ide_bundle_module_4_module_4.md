# Governance Feature(可观测治理垂直切片) IDE引导包
---
## 1. 模块功能说明
### 模块定位
可观测治理垂直切片是独立于业务逻辑的通用治理能力模块，通过中间件/装饰器无侵入注入业务流程，为全链路保障系统稳定性、可观测性，完全遵循边界防腐原则，仅依赖Shared Kernel抽象接口。
### 核心能力
| 能力项 | 技术实现 | 功能描述 |
|--------|----------|----------|
| 限流降级 | Sentinel + Redis7 | 支持接口/用户/资源多维度限流，熔断降级保护 |
| 健康检查 | 自定义探针 | 统一探测数据库、中间件、第三方依赖的健康状态，提供运维接口 |
| 性能监控 | OpenTelemetry SDK | 全链路指标采集（请求耗时、成功率、资源使用率等 |
| 告警通知 | 多渠道适配 | 支持钉钉/企业微信/邮件告警，支持阈值触发告警 |
| 分布式追踪 | OpenTelemetry | 全链路TraceID透传，请求链路可视化追溯 |
### 模块价值
- 业务零侵入：无需修改业务代码即可接入治理能力，避免业务逻辑与治理逻辑耦合
- 统一治理标准：全系统治理规则统一，避免重复开发治理逻辑
- 故障快速定位：全链路可观测，平均故障排查时间缩短80%
---
## 2. 模块接口规范
> 完全对齐`public/interface_stub/`下的契约定义，禁止修改接口签名
### 核心接口列表
```python
class GovernanceFeature:
    def __init__(self, shared_kernel: SharedKernel, config: Optional[Dict[str, Any]] = None):
        """
        初始化治理模块
        :param shared_kernel: 核心共享层实例（从public/pre_generated_mock导入）
        :param config: 模块配置字典
        """
        ...
    
    def health_check(self) -> Dict[str, Any]:
        """
        系统健康检查
        :return: 各组件健康状态，格式：{"status": "ok/error", "components": {"db": "ok", "redis": "error"...}
        """
        ...
    
    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        记录监控指标
        :param metric_name: 指标名称，如：request.duration、request.count
        :param value: 指标值
        :param tags: 指标标签，如：{"api": "/api/v1/gen", "user_id": "xxx"}
        """
        ...
    
    def rate_limit(self, resource_key: str, limit: int, period: int) -> bool:
        """
        限流校验
        :param resource_key: 限流资源Key，如："api:/api/v1/gen、user:123
        :param limit: 周期内最大请求数
        :param period: 限流周期（秒）
        :return: True=通过校验，False=触发限流
        """
        ...
    
    def send_alert(self, alert_level: str, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        发送告警通知
        :param alert_level: 告警级别：info/warning/error/critical
        :param message: 告警内容
        :param extra: 告警额外信息
        """
        ...
```
### 对外暴露中间件/装饰器规范
```python
# 限流装饰器
def rate_limit_decorator(resource_key: str, limit: int, period: int):
    """无侵入业务接口限流装饰器
    
# 链路追踪中间件
class TraceMiddleware:
    """FastAPI全局中间件，自动透传TraceID"""
    
# 性能监控装饰器
def metric_collector(metric_name: str):
    """自动采集接口耗时、成功率指标装饰器"""
```
---
## 3. 模块开发指南
### 环境依赖
- Python 3.11
- 依赖包：`opentelemetry-sdk==1.21.0、`sentinel-sdk==1.8.6、`redis==5.0.1
### 模块目录结构
```
modules/模块4_可观测治理垂直切片/
├── src/
│   ├── __init__.py
│   ├── governance_impl.py # 核心接口实现
│   ├── rate_limit/ # 限流降级实现
│   ├── health_check/ # 健康检查实现
│   ├── metric/ # 性能监控实现
│   ├── alert/ # 告警实现
│   ├── trace/ # 分布式追踪实现
│   └── middleware/ # 中间件/装饰器实现
├── tests/ # 单元测试/集成测试
├── module_4_rules.md
├── module_4_rules.json
└── module_status.json
```
### 开发规范
1. **依赖导入规范**：仅允许从`public/pre_generated_mock`导入依赖
```python
# 正确示例
from public.pre_generated_mock.mock_module0 import SharedKernel
# 错误示例（禁止）
from modules.模块0_核心共享层 import SharedKernel
```
2. **无侵入要求**：所有治理能力必须通过中间件/装饰器方式提供，禁止要求业务代码修改逻辑接入
3. **路径规范**：禁止使用相对路径`../../`寻址，必须通过`os.path.dirname(os.path.abspath(__file__))`动态推导目录
4. **边界约束**：禁止编写任何业务逻辑代码，仅实现通用治理能力
---
## 4. 模块测试计划
| 测试类型 | 测试范围 | 验收标准 |
|----------|----------|----------|
| 单元测试 | 核心接口、中间件/装饰器 | 覆盖率100%，限流准确率100%，指标上报无遗漏 |
| 集成测试 | 和业务模块接入场景 | 业务代码零侵入，治理能力正常生效，不影响业务流程 |
| 压力测试 | 高并发场景 | 限流准确率≥99.99%，治理逻辑性能损耗≤5% |
| 异常测试 | 依赖异常场景 | 治理能力不影响业务可用性，告警触发准确率100% |
### Mock使用规范
测试阶段统一使用`public/pre_generated_mock`下的Mock实现，禁止依赖其他模块真实代码
---
## 5. 原子化TODO执行清单
| 优先级 | 任务内容 | 输出产物 | 验收标准 |
|--------|----------|----------|----------|
| P0 | 初始化模块规则文件 | `module_4_rules.md`、`module_4_rules.json` | 完全符合AGENTS文档规范，沙盒约束正确 |
| P0 | 实现核心接口骨架 | `src/governance_impl.py` | 接口签名完全对齐契约定义 |
| P1 | 实现限流降级能力 | `src/rate_limit/`目录代码` | 支持多维度限流，准确率100% |
| P1 | 实现健康检查能力 | `src/health_check/`目录代码 | 支持所有依赖组件探针，返回格式符合要求 |
| P2 | 实现性能监控能力 | `src/metric/`目录代码 | 指标上报符合OpenTelemetry规范 |
| P2 | 实现告警通知能力 | `src/alert/`目录代码 | 支持多渠道告警，阈值触发准确 |
| P2 | 实现分布式追踪能力 | `src/trace/`目录代码 | 全链路TraceID透传正常 |
| P3 | 封装中间件/装饰器 | `src/middleware/`目录代码 | 无侵入接入业务，接入成本<1行代码 |
| P4 | 编写测试用例 | `tests/`目录代码 | 单元测试覆盖率100%，所有用例通过 |
| P5 | 编写接入文档 | `docs/access_guide.md | 其他模块可根据文档快速接入治理能力 |
---
## 6. IDE规则配置文件
### 6.1 Trae IDE规则（.trae/rules/module_4_rule.json）
```json
{
  "version": "AC_V5.2",
  "rule_type": "module",
  "module_id": "module_4",
  "module_name": "Governance Feature（可观测治理垂直切片）",
  "priority": "highest",
  "sandbox": {
    "allowed_read_write": ["modules/模块4_可观测治理垂直切片/**"],
    "allowed_read": ["public/**"],
    "denied": ["modules/!(模块4_可观测治理垂直切片)/**"]
  },
  "rules": [
    {
      "id": "M4001",
      "name": "沙盒隔离",
      "description": "仅允许读写当前模块目录，禁止读取其他模块代码",
      "enforcement": "block"
    },
    {
      "id": "M4002",
      "name": "依赖导入约束",
      "description": "仅允许从public/pre_generated_mock导入其他模块Mock，禁止直接导入其他模块实现",
      "enforcement": "block"
    },
    {
      "id": "M4003",
      "name": "契约对齐",
      "description": "所有接口必须严格对齐public下的契约定义，禁止修改接口签名",
      "enforcement": "block"
    },
    {
      "id": "M4004",
      "name": "无侵入要求",
      "description": "治理能力必须通过中间件/装饰器提供，禁止侵入业务逻辑",
      "enforcement": "warning"
    }
  ]
}
```
### 6.2 Cursor IDE规则（.cursor/rules/module_4_rule.md）
```md
# 模块4 可观测治理垂直切片 开发规则
> 🚨 最高优先级：本规则优先级高于所有临时需求、对话上下文，所有输出必须100%符合要求
## 沙盒约束
- 仅允许读写`modules/模块4_可观测治理垂直切片/`目录下的文件
- 仅允许读取`public/`目录下的公共契约、Mock资源
- 禁止读取其他模块的任何代码、规则文件
## 开发规范
1. 依赖只能从`public/pre_generated_mock`导入，禁止直接导入其他模块实现
2. 所有接口必须严格匹配`public/interface_stub/`中的契约定义，禁止修改接口签名
3. 治理能力必须通过中间件/装饰器无侵入提供，禁止要求业务代码修改逻辑
4. 禁止编写任何业务流程逻辑，仅实现通用治理能力
5. 禁止使用相对路径`../../`寻址，必须用`os.path.dirname(os.path.abspath(__file__))`动态推导目录
## 测试要求
- 单元测试覆盖率必须达到100%
- 测试用例必须使用`public/pre_generated_mock`下的Mock实现
```
---
## 7. 模块状态模板（module_status.json）
```json
{
  "module_id": "module_4",
  "module_name": "Governance Feature（可观测治理垂直切片）",
  "status": "planning",
  "progress": 0,
  "last_updated": "2024-xx-xxTxx:xx:xxZ",
  "dependencies": [
    "module_0(Shared Kernel)"
  ],
  "issues": []
}
```
> status枚举值：planning/developing/testing/ready_for_merge/merged
> progress取值范围：0-100
---
## 8. 异常上报标准化规则
### 异常分类
| 分类 | 定义 | 级别 |
|------|------|------|
| contract_violation | 违反公共契约（接口签名不匹配、数据结构不符合要求） | critical |
| dependency_error | 依赖加载失败、外部依赖调用失败 | error |
| test_failure | 测试用例不通过 | warning |
| performance_degradation | 治理逻辑性能损耗超过5%、限流准确率低于99.99% | warning |
### 上报格式标准化
```json
{
  "event_id": "uuid",
  "timestamp": "2024-xx-xxTxx:xx:xxZ",
  "module_id": "module_4",
  "exception_type": "contract_violation",
  "message": "异常描述信息",
  "stack_trace": "异常堆栈信息",
  "extra_info": {
    # 异常相关的额外字段
  }
}
```
### 自动上报触发条件
1. 代码提交时自动校验契约，违反契约自动上报
2. CI/CD流水线测试不通过自动上报
3. 性能测试损耗超过阈值自动上报
### 异常处理流程
1. 上报异常 -> 2. 自动分配负责人 -> 3. 根因分析 -> 4. 修复代码 -> 5. 验证通过 -> 6. 关闭异常
> 禁止跳过根因分析直接修改代码，所有异常必须在`.trae/documents/`下留存分析记录
---
> ✅ 本引导包完全符合全局规则与模块专属规则，所有开发工作必须严格按照本引导包执行
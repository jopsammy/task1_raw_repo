# Shared Kernel（核心共享层）IDE引导包
> 模块ID：module_0 | 依赖：无外部依赖 | 定位：唯一全局共享核心资产

---

## 1. 模块功能说明
### 核心定位
作为系统唯一全局共享核心层，严格遵循边界防腐原则，完全隔离核心业务资产与外部框架/中间件/服务依赖，保障核心规则不被外部变化侵蚀，是所有业务模块的唯一公共依赖。
### 核心职责
| 职责分类 | 具体内容 |
|---------|---------|
| 核心业务实体定义 | 全局统一的业务数据结构，100%匹配`public/schema`下的数据契约 |
| 通用业务规则 | VI合规校验规则、Logo叠加规则、提示词优化通用逻辑 |
| 外部依赖抽象接口 | 定义内容审核、生图服务、图像处理等外部依赖的抽象标准，屏蔽外部差异 |
### 边界约束
✅ 仅允许编写纯业务规则、实体定义、抽象接口代码
✅ 仅依赖Python 3.11标准库，无任何第三方框架/服务依赖
❌ 禁止编写任何业务流程编排代码
❌ 禁止导入其他模块的实现代码
❌ 禁止引入任何外部依赖

---

## 2. 模块接口规范
> 所有接口100%匹配`public/interface_stub`下的接口契约，禁止私自修改
### 2.1 核心数据结构（完全匹配数据契约）
| 结构名称 | 说明 |
|---------|---------|
| ErrorDetail | 全局统一错误详情结构 |
| GenImageRequest | 生图请求入参结构 |
| TaskState | 任务状态全链路结构 |
| DomainEvent | 领域事件结构 |
| LogoOverlayConfig | Logo叠加配置结构 |
### 2.2 核心业务方法
```python
from abc import ABC, abstractmethod
from typing import Optional

class SharedKernel(ABC):
    @abstractmethod
    def validate_vi_rule(self, image_url: str, brand_id: str) -> bool:
        """校验图片是否符合品牌VI规则"""
        pass

    @abstractmethod
    def get_logo_config(self, brand_id: str) -> LogoOverlayConfig:
        """获取品牌对应的Logo叠加配置"""
        pass

    @abstractmethod
    def enhance_prompt(self, raw_prompt: str, skill_id: Optional[str] = None) -> str:
        """优化用户输入的生图提示词"""
        pass
```
### 2.3 外部依赖抽象接口
| 接口名称 | 说明 |
|---------|---------|
| ContentAuditInterface | 内容审核服务抽象接口 |
| ImageGenInterface | 生图服务抽象接口 |
| ImageProcessInterface | 图像处理抽象接口 |

---

## 3. 模块开发指南
### 3.1 标准目录结构
```
modules/模块0_核心共享层/
├── entities/               # 核心业务实体实现（基于dataclass，无外部依赖）
│   ├── __init__.py
│   ├── error_detail.py
│   ├── gen_image_request.py
│   ├── task_state.py
│   ├── domain_event.py
│   └── logo_overlay_config.py
├── rules/                  # 通用业务规则实现
│   ├── __init__.py
│   ├── vi_rule_validator.py
│   └── logo_rule.py
├── interfaces/             # 抽象接口定义（基于abc.ABC）
│   ├── __init__.py
│   ├── content_audit.py
│   ├── image_gen.py
│   └── image_process.py
├── tests/                  # 单元测试代码
│   ├── test_entities.py
│   ├── test_rules.py
│   └── test_interfaces.py
├── module_0_rules.md       # 模块专属规则（自动生成，禁止修改）
├── module_0_rules.json     # 模块专属规则（自动生成，禁止修改）
└── module_status.json      # 模块状态追踪文件
```
### 3.2 开发约束
1. **依赖约束**：所有生产代码仅允许导入Python 3.11标准库，禁止引入任何第三方包（包括Pydantic、FastAPI等），实体使用`dataclasses`实现
2. **沙盒约束**：仅允许读写当前模块目录下的文件，仅可读取`public/`下的公共契约资源，禁止访问其他模块目录
3. **路径约束**：禁止使用相对路径寻址（如`../../`），必须使用`os.path.dirname(os.path.abspath(__file__))`动态推导目录
4. **契约约束**：所有实体、接口必须100%匹配`public/`下的契约定义，变更必须先走契约审批流程

---

## 4. 模块测试计划
| 测试类型 | 测试范围 | 验收标准 | 覆盖率要求 |
|---------|---------|---------|---------|
| 实体校验测试 | 所有核心业务实体 | 字段类型、必填项、约束完全匹配数据契约 | 100% |
| 业务规则测试 | VI校验规则、Logo叠加规则、提示词优化规则 | 覆盖所有正常、边界、异常场景，规则输出符合预期 | 100% |
| 接口一致性测试 | 所有抽象接口 | 接口签名、参数、返回值、抛出异常完全匹配接口契约 | 100% |
| 依赖合规测试 | 全模块生产代码 | 无任何第三方依赖导入、无其他模块代码导入 | 100% |
| 性能测试 | 核心规则校验方法 | 单次校验耗时≤10ms，无内存泄漏 | - |
> 测试工具仅允许使用Python标准库`unittest`，禁止引入外部测试框架依赖

---

## 5. 原子化TODO执行清单
| 序号 | 任务内容 | 预估耗时 | 验收标准 | 依赖 |
|---------|---------|---------|---------|---------|
| 1 | 搭建模块标准目录结构 | 0.5h | 符合3.1节目录规范，所有目录和规则文件齐全 | 全局规则已落地 |
| 2 | 实现核心业务实体 | 1h | 基于`dataclasses`实现所有契约定义的实体，字段、约束完全匹配 | 任务1完成 |
| 3 | 实现通用业务规则 | 2h | 完成VI校验、Logo规则、提示词优化逻辑，覆盖所有边界场景 | 任务2完成 |
| 4 | 定义外部依赖抽象接口 | 1h | 基于`abc.ABC`实现所有契约定义的抽象接口，签名完全匹配 | 任务2完成 |
| 5 | 编写单元测试 | 2h | 覆盖所有实体、规则、接口，测试用例通过率100% | 任务3、4完成 |
| 6 | 契约一致性校验 | 0.5h | 通过`public/schema`和`public/interface_stub`的自动校验，无违规提示 | 任务5完成 |
| 7 | 代码评审 | 1h | 符合模块所有规则，无外部依赖，无业务流程代码 | 任务6完成 |
| 8 | 提交验收 | 0.5h | 模块状态更新为`ready_for_merge`，无遗留问题 | 任务7完成 |

---

## 6. IDE规则配置文件
### 6.1 Trae IDE规则：.trae/rules/module_0_rule.json
```json
{
  "version": "AC_V5.2",
  "rule_type": "module",
  "module_id": "module_0",
  "module_name": "Shared Kernel（核心共享层）",
  "priority": "highest",
  "sandbox": {
    "allowed_read_write": ["modules/模块0_核心共享层/**"],
    "allowed_read": ["public/**"],
    "denied": ["modules/!(模块0_核心共享层)/**", "*.pyc", "__pycache__/**"]
  },
  "rules": [
    {
      "id": "M001",
      "name": "沙盒隔离",
      "description": "仅允许读写当前模块目录，禁止访问其他模块资源",
      "level": "error",
      "trigger": "file_access"
    },
    {
      "id": "M002",
      "name": "无外部依赖",
      "description": "禁止导入任何第三方库或其他模块的实现代码",
      "level": "error",
      "trigger": "code_import"
    },
    {
      "id": "M003",
      "name": "职责边界",
      "description": "仅允许定义实体、规则、抽象接口，禁止编写业务流程代码",
      "level": "error",
      "trigger": "code_check"
    },
    {
      "id": "M004",
      "name": "契约合规",
      "description": "所有实体、接口必须匹配public下的契约定义",
      "level": "error",
      "trigger": "pre_commit"
    }
  ]
}
```
### 6.2 Cursor IDE规则：.cursor/rules/module_0_rule.md
```markdown
# 🚨 最高优先级：Shared Kernel模块专属规则
> 所有代码输出必须100%符合本规则，违反规则的内容必须自动修正后再输出

## 1. 沙盒隔离约束
✅ 仅允许读写`modules/模块0_核心共享层/`目录下的文件
✅ 仅允许读取`public/`下的公共契约资源
❌ 禁止读取/修改其他任何模块的代码、规则、配置文件
❌ 禁止直接调用其他模块的内部实现

## 2. 开发边界约束
✅ 仅允许编写核心实体、通用业务规则、抽象接口代码
✅ 生产代码仅依赖Python 3.11标准库，禁止引入任何第三方包
❌ 禁止编写任何业务流程编排、外部依赖实现代码
❌ 禁止导入其他模块的任何代码（包括Mock实现）

## 3. 契约约束
✅ 所有实体、接口必须100%匹配`public/schema`和`public/interface_stub`下的契约定义
✅ 禁止私自修改接口签名、字段类型、约束规则
❌ 禁止输出不符合契约的数据结构

## 4. 路径约束
✅ 必须使用`os.path.dirname(os.path.abspath(__file__))`动态推导目录
❌ 禁止使用相对路径寻址（如`../../`）
```

---

## 7. 模块状态模板（module_status.json）
```json
{
  "module_id": "module_0",
  "module_name": "Shared Kernel（核心共享层）",
  "status": "planning",
  "progress": 0,
  "last_updated": "{{current_timestamp}}",
  "dependencies": [],
  "issues": [],
  "owner": "{{developer_name}}",
  "version": "1.0.0"
}
```
### 字段说明
| 字段 | 枚举/格式 | 说明 |
|---------|---------|---------|
| status | planning/developing/testing/ready_for_merge/merged | 模块当前开发阶段 |
| progress | 0-100整数 | 开发进度百分比 |
| dependencies | 数组 | 本模块依赖的其他模块ID，本模块固定为空数组 |
| issues | 数组 | 当前遗留问题列表 |

---

## 8. 异常上报标准化规则
### 8.1 异常分类
| 异常类型 | 说明 | 优先级 |
|---------|---------|---------|
| contract_violation | 实体/接口不符合公共契约定义 | 最高 |
| dependency_error | 导入了第三方库或其他模块的代码，违反无依赖约束 | 最高 |
| test_failure | 单元测试用例失败 | 高 |
| performance_degradation | 核心规则校验耗时超过10ms基线 | 中 |
### 8.2 标准化上报格式
```json
{
  "exception_type": "contract_violation",
  "module_id": "module_0",
  "file_path": "modules/模块0_核心共享层/entities/gen_image_request.py",
  "error_detail": "字段size的类型不符合契约定义，契约为str，实际为int",
  "trigger_time": "{{timestamp}}",
  "trigger_source": "pre_commit_check",
  "handler": "{{developer_name}}"
}
```
### 8.3 自动上报触发条件
1. 代码提交前的预检查阶段发现契约违规、依赖违规
2. CI/CD流水线测试阶段发现用例失败
3. 性能监控发现核心方法耗时超过阈值
### 8.4 异常处理流程
1. 收到异常上报后，2小时内由模块负责人确认问题
2. 修复问题后重新触发校验，校验通过后关闭异常
3. 所有异常处理过程必须记录在`.trae/documents/`下的问题追踪文档中
4. 无法快速修复的问题必须降级处理，同步到模块状态的issues列表中
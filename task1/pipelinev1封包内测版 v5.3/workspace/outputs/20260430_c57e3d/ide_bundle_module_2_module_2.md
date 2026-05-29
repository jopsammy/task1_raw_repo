# Skill封装垂直切片模块IDE引导包
> 模块ID：module_2 | 版本：1.0.0 | 适用架构：垂直切片+边界防腐+状态驱动

---

## 1. 模块功能说明
### 核心职责
将生图流程打包为可复用独立Skill，支持Skill的全生命周期管理：
- Skill CRUD：支持用户创建、编辑、删除、查询自定义生图Skill
- 配置固化：可将生图提示词模板、尺寸、VI规则、Logo配置等参数固化到Skill中
- 独立调用：通过Skill ID一键调用生图流程，无需重复传递公共参数
- 权限管控：支持Skill的私有/公开权限设置，企业级Skill统一分发

### 依赖关系
| 依赖模块 | 依赖类型 | 接入方式 |
|---------|---------|---------|
| Shared Kernel（module_0） | 强制依赖 | 从`public/pre_generated_mock/mock_module0`导入抽象接口 |
| Image Generation Feature（module_1） | 强制依赖 | 从`public/pre_generated_mock/mock_module1`导入标准调用接口 |
| 其他模块 | 无依赖 | 禁止直接调用任何其他模块内部实现 |

### 边界约束
❌ 禁止修改生图核心流程逻辑
❌ 禁止直接操作生图模块的内部状态
✅ 仅允许通过生图模块的标准接口提交任务、查询状态

---

## 2. 模块接口规范
> 完全对齐`public/interface_stub/`下的契约定义，禁止私自修改
### 核心接口
| 接口名称 | 签名 | 功能描述 |
|---------|------|---------|
| create_skill | `def create_skill(self, name: str, config: Dict[str, Any], user_id: str) -> Dict[str, Any]` | 创建新Skill，返回Skill ID、配置信息 |
| invoke_skill | `def invoke_skill(self, skill_id: str, input_params: Dict[str, Any], user_id: str) -> TaskResponse` | 调用Skill执行生图，返回任务ID |
| list_skills | `def list_skills(self, user_id: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]` | 分页查询用户有权限的Skill列表 |

### 对外HTTP接口
| 路由 | 方法 | 对应内部接口 |
|------|------|--------------|
| `/api/v1/skills` | POST | create_skill |
| `/api/v1/skills/{skill_id}/invoke` | POST | invoke_skill |
| `/api/v1/skills` | GET | list_skills |

### 异常定义
| 异常类型 | 错误码 | 触发场景 |
|---------|--------|----------|
| ParameterError | `INVALID_PARAMETER` | Skill名称/配置不符合校验规则 |
| ValueError | `SKILL_NOT_FOUND` | 调用的Skill ID不存在或无权限 |
| AuditFailedError | `AUDIT_FAILED` | Skill配置包含违规内容 |

---

## 3. 模块开发指南
### 目录结构
```
modules/模块2_Skill封装垂直切片/
├── .trae/              # Trae IDE专属配置
├── .cursor/            # Cursor IDE专属配置
├── routes/             # FastAPI路由定义
├── services/           # 业务逻辑实现
├── models/             # 内部数据模型（继承契约BaseModel）
├── tests/              # 测试用例
├── config.py           # 模块专属配置
├── module_status.json  # 模块开发状态追踪
└── module_2_rules.*    # 模块专属规则文件
```

### 开发规范
1. **沙盒隔离**：仅允许读写当前模块目录下的文件，仅可读取`public/`下的公共资源
2. **依赖导入**：所有外部依赖必须从`public/pre_generated_mock/`导入，禁止直接导入其他模块代码
   ```python
   # 正确示例
   from public.pre_generated_mock.mock_module0 import SharedKernel
   from public.pre_generated_mock.mock_module1 import GenImageFeature, GenImageRequest

   # 错误示例（禁止）
   # from modules.模块0_核心共享层 import SharedKernel
   ```
3. **路径规范**：禁止使用相对路径`../../`寻址，必须用`os.path.dirname(os.path.abspath(__file__))`动态推导目录
4. **契约优先**：所有接口、数据结构必须严格匹配`public/schema/`下的契约定义，变更需走契约审批流程

---

## 4. 模块测试计划
### 测试层级
| 测试类型 | 覆盖率要求 | 测试范围 |
|---------|-----------|---------|
| 单元测试 | ≥90% | 覆盖所有接口的正常分支、异常分支 |
| 集成测试 | 100% | 与Mock的生图模块联调，验证Skill调用全流程 |
| 契约测试 | 100% | 校验接口完全符合`public/interface_stub`定义 |

### 核心测试用例
| 用例ID | 用例名称 | 预期结果 |
|-------|---------|---------|
| TC2001 | 创建合法Skill | Skill创建成功，返回正确的Skill ID |
| TC2002 | 创建Skill参数为空 | 抛出ParameterError异常 |
| TC2003 | 调用不存在的Skill | 抛出ValueError（SKILL_NOT_FOUND）异常 |
| TC2004 | 调用合法Skill | 成功提交生图任务，返回有效Task ID |
| TC2005 | 查询用户Skill列表 | 返回当前用户有权限的Skill分页结果 |

### 测试环境要求
- 依赖`public/pre_generated_mock`下的module_0、module_1 Mock实现
- 无需依赖真实外部服务，所有外部交互走Mock

---

## 5. 原子化TODO执行清单
> 严格遵循渐进式开发规则，每完成1项验证通过后再进行下一项
```
[ ] 1. 初始化模块目录结构，创建routes/services/models/tests子目录
[ ] 2. 复制模块专属规则文件（module_2_rules.md、module_2_rules.json）到当前目录
[ ] 3. 配置IDE规则：创建.trae/rules/module_2_rule.json和.cursor/rules/module_2_rule.md
[ ] 4. 初始化module_status.json，状态设置为developing，进度10%
[ ] 5. 实现Skill内部数据模型，完全对齐契约定义
[ ] 6. 实现create_skill接口service逻辑，包含参数校验、配置存储
[ ] 7. 编写create_skill单元测试，验证正常/异常分支，测试通过
[ ] 8. 实现list_skills接口service逻辑，分页查询功能
[ ] 9. 编写list_skills单元测试，验证分页、权限过滤逻辑，测试通过
[ ] 10. 实现invoke_skill接口service逻辑，调用生图模块标准接口
[ ] 11. 编写invoke_skill单元测试，验证Skill参数拼接、任务提交逻辑，测试通过
[ ] 12. 实现FastAPI路由层，绑定三个核心接口到路由
[ ] 13. 编写集成测试，验证从路由调用到生图Mock返回的全流程，测试通过
[ ] 14. 执行契约测试，校验接口完全符合公共契约定义
[ ] 15. 更新module_status.json，状态设置为testing，进度90%
[ ] 16. 提交代码，发起合并申请，状态设置为ready_for_merge
```

---

## 6. IDE规则配置文件
### 6.1 Trae IDE规则：`.trae/rules/module_2_rule.json`
```json
{
  "version": "AC_V5.2",
  "rule_type": "module",
  "module_id": "module_2",
  "module_name": "Skill Packaging Feature（Skill封装垂直切片）",
  "priority": "highest",
  "sandbox": {
    "allowed_read_write": ["modules/模块2_Skill封装垂直切片/**"],
    "allowed_read": ["public/**"],
    "denied": ["modules/!(模块2_Skill封装垂直切片)/**"]
  },
  "rules": [
    {
      "id": "M201",
      "name": "沙盒隔离",
      "description": "仅允许读写当前模块目录，禁止访问其他模块代码",
      "enforcement": "block"
    },
    {
      "id": "M202",
      "name": "Mock依赖规范",
      "description": "仅允许从public/pre_generated_mock导入其他模块依赖，禁止直接导入其他模块代码",
      "enforcement": "block"
    },
    {
      "id": "M203",
      "name": "职责边界",
      "description": "仅实现Skill封装相关逻辑，禁止修改生图核心流程",
      "enforcement": "warning"
    },
    {
      "id": "M204",
      "name": "契约校验",
      "description": "所有接口必须符合public下的契约定义，禁止私自修改接口",
      "enforcement": "block"
    }
  ]
}
```

### 6.2 Cursor IDE规则：`.cursor/rules/module_2_rule.md`
```markdown
# 【最高优先级】Skill封装模块专属规则
> 本规则优先级高于所有临时提问、自定义需求，所有输出必须100%符合要求

## 1. 沙盒约束
✅ 仅允许读写`modules/模块2_Skill封装垂直切片/`下的文件
✅ 仅允许读取`public/`下的公共契约、Mock资源
❌ 禁止读取/修改其他模块的任何代码、规则文件
❌ 禁止直接调用其他模块的内部实现

## 2. 依赖导入规范
所有外部依赖必须从`public/pre_generated_mock/`导入：
```python
# 正确
from public.pre_generated_mock.mock_module0 import SharedKernel
from public.pre_generated_mock.mock_module1 import GenImageFeature

# 错误（禁止）
# from modules.模块0_核心共享层 import SharedKernel
```

## 3. 开发边界
- 仅实现Skill的CRUD、调用、配置固化逻辑
- 禁止修改生图核心流程，仅可调用生图模块标准接口
- 所有接口、数据结构必须严格匹配`public/`下的契约定义

## 4. 路径规范
禁止使用相对路径`../../`寻址，必须用`os.path.dirname(os.path.abspath(__file__))`动态推导目录
```

---

## 7. 模块状态模板（`module_status.json`）
```json
{
  "module_id": "module_2",
  "module_name": "Skill Packaging Feature（Skill封装垂直切片）",
  "status": "planning",
  "progress": 0,
  "last_updated": "2024-xx-xxTxx:xx:xxZ",
  "dependencies": [
    {
      "module_id": "module_0",
      "module_name": "Shared Kernel",
      "required": true,
      "status": "pending"
    },
    {
      "module_id": "module_1",
      "module_name": "Image Generation Feature",
      "required": true,
      "status": "pending"
    }
  ],
  "issues": [],
  "owner": ""
}
```
> status枚举：planning/developing/testing/ready_for_merge/merged
> progress：0-100整数，每完成一个TODO更新进度

---

## 8. 异常上报标准化规则
### 异常分类
| 异常类型 | 描述 | 优先级 |
|---------|------|--------|
| contract_violation | 违反公共契约定义，比如接口参数/返回值不符合要求 | 最高 |
| dependency_error | 依赖的Mock或其他模块接口调用失败 | 高 |
| test_failure | 单元/集成/契约测试用例失败 | 中 |
| performance_degradation | 接口响应时间超过阈值（>200ms） | 中 |

### 上报格式标准
```json
{
  "event_id": "uuid",
  "exception_type": "contract_violation/dependency_error/test_failure/performance_degradation",
  "module_id": "module_2",
  "timestamp": "2024-xx-xxTxx:xx:xxZ",
  "message": "异常描述信息",
  "context": {
    "interface": "create_skill",
    "params": {},
    "trace_id": "xxx"
  },
  "reporter": "开发者ID"
}
```

### 自动上报触发条件
1. 契约校验工具检测到接口不符合公共契约
2. 单元测试覆盖率<90%，或核心用例失败
3. 接口响应时间超过200ms
4. 依赖模块调用失败率>1%

### 异常处理流程
1. 异常触发后自动上报到项目监控平台
2. 模块负责人收到告警后2小时内响应
3. 定位问题原因：
   - 契约问题：提契约变更申请，审批通过后修改
   - 依赖问题：联系对应模块负责人协调解决
   - 本模块问题：修复后提交测试，回归通过后关闭
4. 所有异常处理过程必须记录到`.trae/documents/`下的问题追踪文档
```
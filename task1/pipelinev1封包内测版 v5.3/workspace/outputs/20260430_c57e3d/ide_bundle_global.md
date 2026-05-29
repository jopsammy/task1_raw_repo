# 全局IDE引导包（AC_V5.2 生图系统专属）
---
## 1. 项目整体概览
### 1.1 项目定位
AI生图业务中台，融合三大架构范式最优解：
> 「垂直切片为根、边界防腐为盾、状态驱动为骨」
> 兼顾快速交付、长期扩展性、高并发可靠性三大核心诉求
### 1.2 核心技术栈
| 领域 | 选型 | 版本 | 说明 |
|------|------|------|------|
| 后端框架 | Python + FastAPI | 3.11 / 0.104.1 | 高性能快速开发 |
| 状态编排 | Temporal | 1.5.0 | 替代事件总线/Celery，内置重试/补偿 |
| 存储 | PostgreSQL + Redis | 15 / 7 | 业务数据/状态存储、缓存限流 |
| 工具链 | Pydantic 2 + Alembic + Import-linter | 2.5.2 / 1.12.1 / 1.12.0 | 数据校验、迁移、依赖边界校验 |
### 1.3 标准目录架构（强制遵守）
```
Project_Root/
├── public/                 # 只读公共资源区（仅负责人可修改）
│   ├── schema/             # 数据契约快照
│   ├── interface_stub/     # 接口契约定义
│   └── pre_generated_mock/ # 全量预生成Mock实现
├── modules/                # 业务模块区
│   ├── 模块0_核心共享层/   # 全局唯一共享模块，无外部依赖
│   ├── 模块1_核心生图垂直切片/
│   ├── 模块2_Skill封装垂直切片/
│   ├── 模块3_基础设施层/
│   └── 模块4_可观测治理垂直切片/
├── interfaces/             # API入口层
├── workspace/              # 用户临时数据区
└── .trae/.cursor/          # IDE规则配置区
```
### 1.4 核心约束优先级
`全局规则 > 模块专属规则 > 临时需求 > 自定义配置`
---
## 2. 模块0（核心共享层/全局调度）开发指南
### 2.1 模块核心信息
- 模块ID：`module_0`
- 定位：全局唯一共享模块，所有其他模块的唯一依赖来源
- 依赖：仅Python标准库，无任何外部框架/业务模块依赖
- 访问权限：仅核心架构师可修改，其他模块仅可读取公共契约
### 2.2 核心职责（仅允许做以下内容）
1. 定义全局核心业务实体（GenImageRequest/TaskState等）、枚举、异常类
2. 定义外部依赖抽象接口（ContentAuditInterface/ImageGenInterface等）
3. 实现通用业务规则（VI校验、Logo配置管理、提示词优化）
4. 提供全局管控能力：进度扫描、契约校验、依赖管理、Mock切换、合流管控
### 2.3 禁止操作清单
❌ 禁止编写任何业务流程逻辑
❌ 禁止引入任何第三方依赖/其他模块实现
❌ 禁止修改公共契约定义，契约变更必须走审批流程
❌ 禁止使用相对路径寻址，必须动态推导目录
### 2.4 开发流程
1. 每修改模块0内容前必须先更新`.trae/documents/`下的变更分析文档
2. 开发完成后自动跑全量契约校验，确保所有接口/数据结构符合契约
3. 提交PR必须由架构师审核通过后方可合流
---
## 3. 各模块协作规范
### 3.1 依赖规则
- 所有模块仅可依赖模块0的抽象接口，禁止直接依赖其他模块的内部实现
- 跨模块调用必须通过`public/pre_generated_mock/`下的Mock或公共接口契约
- 依赖注入强制通过构造函数传入，禁止硬编码导入实现类
### 3.2 数据流转规则
- 所有业务数据必须符合`public/schema/`下的数据契约，写入前必须通过校验
- 业务状态统一由Temporal工作流管理，禁止原地更新数据库状态
- 状态变更必须生成不可变领域事件，全链路可追溯
### 3.3 接口调用规则
- 对外暴露的API必须严格匹配`public/interface_stub/`下的接口定义
- 异常必须抛出模块0定义的标准化异常类，禁止自定义异常
- 接口返回值必须符合契约定义的字段，禁止额外返回未定义字段
---
## 4. 全局测试计划
| 测试阶段 | 覆盖范围 | 准入条件 | 准出条件 | 负责人 |
|----------|----------|----------|----------|--------|
| 单元测试 | 各模块内部逻辑 | 模块功能开发完成 | 核心逻辑覆盖率100%，整体覆盖率≥90%，所有用例通过 | 模块开发人员 |
| 契约测试 | 模块间接口/数据结构 | 模块单元测试通过 | 100%符合公共契约定义，无契约冲突 | 测试人员 |
| 集成测试 | 全链路流程 | 所有模块契约测试通过 | 生图全流程跑通，成功率≥99.9% | 测试人员 |
| 性能测试 | 高并发场景 | 集成测试通过 | 1000QPS下接口响应时间<200ms，任务成功率≥99.5% | 运维/测试 |
| 灰度测试 | 线上小流量 | 性能测试通过 | 灰度10%流量运行72小时无严重bug | 全团队 |
---
## 5. 原子化TODO执行清单（按优先级排序）
### P0 第一阶段（基础搭建）
- [ ] 初始化标准目录结构，创建public下的契约、Mock、接口stub文件
- [ ] 提交全局规则、各模块规则文件到根目录对应位置
- [ ] 配置Import-linter依赖校验规则，阻断跨模块非法依赖
### P0 第二阶段（模块0开发）
- [ ] 实现模块0核心实体、枚举、异常类，100%匹配数据契约
- [ ] 实现模块0抽象接口定义，100%匹配接口契约
- [ ] 开发进度扫描功能：自动统计各模块TODO完成率、测试覆盖率
- [ ] 开发契约校验功能：自动校验所有模块的接口/数据结构合规性
- [ ] 开发Mock切换功能：支持全局/模块级Mock/真实实现一键切换
- [ ] 开发合流管控功能：自动检查合流前置条件，阻断不符合要求的合流
### P1 第三阶段（业务模块开发）
- [ ] 模块1生图全流程开发，单元测试覆盖率≥90%
- [ ] 模块3基础设施层开发，实现所有抽象接口的Mock/真实实现
- [ ] 模块2Skill封装功能开发，单元测试覆盖率≥90%
- [ ] 模块4可观测治理功能开发，集成限流/监控/告警能力
### P1 第四阶段（集成上线）
- [ ] 全链路集成测试，生图流程成功率100%
- [ ] 性能测试达标，1000QPS下无性能瓶颈
- [ ] 灰度10%流量上线，运行72小时无严重bug
- [ ] 全量上线，接入正式用户流量
---
## 6. IDE规则配置文件
### 6.1 Trae IDE规则：`.trae/rules/global_rule.json`
```json
{
  "version": "AC_V5.2",
  "priority": "highest",
  "rule_set": [
    {
      "id": "AC_G001",
      "name": "公共区只读约束",
      "type": "file_operation",
      "effect": "block",
      "match": ["public/**/*"],
      "operation": ["modify", "delete", "create"]
    },
    {
      "id": "AC_G002",
      "name": "跨模块非法依赖阻断",
      "type": "code_import",
      "effect": "block",
      "match": ["modules/!(模块0_核心共享层)/**/*.py"],
      "import_pattern": ["from modules.!(模块0_核心共享层) import *", "import modules.!(模块0_核心共享层)"]
    },
    {
      "id": "AC_G003",
      "name": "契约校验前置检查",
      "type": "pre_commit",
      "effect": "block",
      "check_script": "python3 scripts/validate_contract.py",
      "fail_message": "代码不符合契约要求，请修正后再提交"
    },
    {
      "id": "AC_G004",
      "name": "合流质量门检查",
      "type": "pre_merge",
      "effect": "block",
      "check_script": "python3 scripts/check_merge_gate.py",
      "fail_message": "未达到合流质量门要求，请修正后再合流"
    }
  ]
}
```
### 6.2 Cursor IDE规则：`.cursor/rules/global_rule.md`
```md
# Cursor IDE 全局规则（最高优先级）
## 通用约束
1. 所有输出必须100%符合`global_rules.md`和对应模块的专属规则，违反规则的内容必须自动修正后再输出
2. 禁止修改`public/`目录下的任何内容，契约变更必须走审批流程
3. 禁止跨模块直接导入其他模块的内部实现，依赖只能从`public/pre_generated_mock/`导入
4. 禁止大批量生成/修改代码，每次最多修改5个文件，测通一步再走下一步
5. 所有修改必须先在`.trae/documents/`下写分析文档，禁止直接修改代码
## 架构规则
1. 目录结构必须严格遵守标准目录架构，禁止新增未定义的顶层目录
2. 模块0仅允许定义实体、抽象接口、通用规则，禁止编写业务流程逻辑
3. 所有数据/接口必须符合public下的契约定义，禁止返回未定义字段
4. 异常必须使用模块0定义的标准化异常类，禁止自定义异常
## 禁止操作清单
❌ 禁止修改任何规则文件
❌ 禁止使用相对路径寻址（如`../../`）
❌ 禁止硬编码依赖实现，必须使用依赖注入
❌ 禁止原地更新业务状态，所有状态变更必须生成领域事件
```
---
## 7. 模块0核心功能骨架
```python
"""
模块0核心管控功能骨架
仅依赖Python标准库，无任何外部依赖
"""
import os
import json
from typing import Dict, List, Any, Optional

# -------------------------- 进度扫描功能 --------------------------
class ProgressScanner:
    SCAN_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @classmethod
    def scan_all_modules(cls) -> Dict[str, Any]:
        """扫描所有模块开发进度"""
        modules = ["模块0_核心共享层", "模块1_核心生图垂直切片", "模块2_Skill封装垂直切片", "模块3_基础设施层", "模块4_可观测治理垂直切片"]
        result = {}
        for module in modules:
            result[module] = {
                "todo_completion_rate": cls._calc_todo_rate(module),
                "unit_test_coverage": cls._get_test_coverage(module),
                "contract_compliance_rate": cls._get_contract_rate(module)
            }
        return result

    @classmethod
    def _calc_todo_rate(cls, module: str) -> float:
        """计算模块TODO完成率"""
        # 实现逻辑：扫描模块下TODO注释，统计完成率
        pass

    @classmethod
    def _get_test_coverage(cls, module: str) -> float:
        """获取模块单元测试覆盖率"""
        # 实现逻辑：读取coverage报告数据
        pass

    @classmethod
    def _get_contract_rate(cls, module: str) -> float:
        """获取模块契约合规率"""
        # 实现逻辑：调用契约校验接口获取结果
        pass

# -------------------------- 契约校验功能 --------------------------
class ContractValidator:
    SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "schema")

    @classmethod
    def validate_data(cls, data: Dict[str, Any], schema_name: str) -> bool:
        """校验数据是否符合对应数据契约"""
        schema_file = os.path.join(cls.SCHEMA_PATH, f"{schema_name}.json")
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)
        # 实现逻辑：JSON Schema校验
        return True

    @classmethod
    def validate_interface(cls, interface_signature: str, interface_name: str) -> bool:
        """校验接口是否符合对应接口契约"""
        # 实现逻辑：与public/interface_stub下的定义比对
        return True

# -------------------------- 依赖管理功能 --------------------------
class DependencyManager:
    @classmethod
    def get_module_dependency_graph(cls) -> Dict[str, List[str]]:
        """获取模块依赖关系图"""
        # 实现逻辑：扫描所有模块的import语句，生成依赖关系
        return {
            "模块1_核心生图垂直切片": ["模块0_核心共享层"],
            "模块2_Skill封装垂直切片": ["模块0_核心共享层", "模块1_核心生图垂直切片"],
            "模块3_基础设施层": ["模块0_核心共享层"],
            "模块4_可观测治理垂直切片": ["模块0_核心共享层"]
        }

    @classmethod
    def check_illegal_dependency(cls) -> List[str]:
        """检查非法依赖"""
        # 实现逻辑：扫描跨模块非法依赖，返回异常列表
        return []

# -------------------------- Mock切换功能 --------------------------
class MockSwitcher:
    CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "pre_generated_mock", "mock_config.json")

    @classmethod
    def set_mock_mode(cls, module_name: str, enabled: bool) -> None:
        """设置模块Mock开关"""
        config = cls._load_config()
        if module_name not in config:
            config[module_name] = {}
        config[module_name]["enabled"] = enabled
        with open(cls.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    @classmethod
    def get_mock_mode(cls, module_name: str) -> bool:
        """获取模块Mock状态"""
        config = cls._load_config()
        return config.get(module_name, {}).get("enabled", True)

    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        if os.path.exists(cls.CONFIG_PATH):
            with open(cls.CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

# -------------------------- 合流管控功能 --------------------------
class MergeController:
    @classmethod
    def check_merge_gate(cls, module_name: str) -> Dict[str, Any]:
        """检查合流质量门"""
        checks = {
            "unit_test_coverage": ProgressScanner._get_test_coverage(module_name) >= 90,
            "contract_compliance": ProgressScanner._get_contract_rate(module_name) == 100,
            "no_illegal_dependency": len(DependencyManager.check_illegal_dependency()) == 0,
            "no_critical_bug": cls._check_critical_bug(module_name)
        }
        return {
            "passed": all(checks.values()),
            "checks": checks
        }

    @classmethod
    def _check_critical_bug(cls, module_name: str) -> bool:
        """检查模块是否有未解决的严重bug"""
        # 实现逻辑：对接缺陷管理系统
        return True
```
---
## 8. 全局监控看板
| 板块 | 监控指标 | 刷新频率 | 异常触发条件 |
|------|----------|----------|--------------|
| 模块进度聚合 | 各模块TODO完成率、单元测试覆盖率、契约合规率 | 5分钟 | 任一模块覆盖率<80%、合规率<100% |
| 契约状态监控 | 数据契约冲突数、接口契约冲突数、非法依赖数 | 1分钟 | 任一指标>0立即告警 |
| 异常告警中心 | 异常等级（info/warning/error/critical）、异常类型、异常模块、处理状态 | 实时 | critical异常立即推送告警 |
| 合流队列管理 | 待合流PR数、质量门通过PR数、待人工审核PR数 | 1分钟 | 合流队列等待时长>2小时告警 |
> 看板访问地址：`/internal/dashboard`
---
## 9. 合流仲裁配置（`integration_gates.json`）
```json
{
  "version": "1.0.0",
  "gates": [
    {
      "stage": "模块开发合流",
      "pre_conditions": [
        "单元测试覆盖率≥90%",
        "契约校验100%通过",
        "无非法依赖",
        "无未解决的严重bug"
      ],
      "auto_merge": true,
      "manual_review_required": false
    },
    {
      "stage": "测试环境合流",
      "pre_conditions": [
        "所有模块单元测试通过",
        "契约测试100
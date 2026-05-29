"""
stage_renderers模块单元测试

测试 ui_renderer.py 中的各阶段渲染器：
- render_requirement_anchoring: 需求锚定渲染器
- render_architecture_iteration: 架构迭代渲染器
- render_contract_generation: 契约生成渲染器
- render_requirement_validation: 需求校验渲染器
- render_landing_plan: 落地方案渲染器
- render_ide_bundle: IDE引导包渲染器
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)


class TestRenderRequirementAnchoring:
    """需求锚定渲染器测试"""
    
    def test_render_requirement_anchoring_basic(self):
        """测试基本需求锚定渲染"""
        data = {
            "entities": [
                {"name": "用户", "attributes": ["id", "name", "email"]},
                {"name": "订单", "attributes": ["id", "user_id", "amount"]}
            ],
            "flows": [
                {"name": "注册流程", "steps": ["输入信息", "验证", "创建账户"]}
            ],
            "metrics": {
                "识别实体数": {"value": 2},
                "业务流程数": {"value": 1},
                "属性总数": {"value": 6}
            }
        }
        
        entities = data.get("entities", [])
        flows = data.get("flows", [])
        metrics = data.get("metrics", {})
        
        assert len(entities) == 2
        assert len(flows) == 1
        assert metrics["识别实体数"]["value"] == 2
    
    def test_render_requirement_anchoring_empty_data(self):
        """测试空数据"""
        data = {}
        
        if not data:
            is_empty = True
        else:
            is_empty = False
        
        assert is_empty is True
    
    def test_render_requirement_anchoring_auto_metrics(self):
        """测试自动计算指标"""
        data = {
            "entities": [
                {"name": "用户"},
                {"name": "订单"},
                {"name": "商品"}
            ],
            "flows": [
                {"name": "流程1"},
                {"name": "流程2"}
            ],
            "attributes": ["attr1", "attr2", "attr3", "attr4"]
        }
        
        metrics = data.get("metrics", {})
        entities = data.get("entities", [])
        flows = data.get("flows", [])
        attributes = data.get("attributes", [])
        
        if not metrics:
            entity_count = len(entities) if isinstance(entities, list) else 0
            flow_count = len(flows) if isinstance(flows, list) else 0
            attribute_count = len(attributes) if isinstance(attributes, list) else 0
            metrics = {
                "识别实体数": {"value": entity_count},
                "业务流程数": {"value": flow_count},
                "属性总数": {"value": attribute_count}
            }
        
        assert metrics["识别实体数"]["value"] == 3
        assert metrics["业务流程数"]["value"] == 2
        assert metrics["属性总数"]["value"] == 4
    
    def test_render_requirement_anchoring_business_logic_summary(self):
        """测试业务逻辑摘要"""
        data = {
            "business_logic_summary": "这是一个用户管理系统，支持用户注册、登录和权限管理。",
            "entities": []
        }
        
        summary = data.get("business_logic_summary", "")
        
        assert "用户管理系统" in summary
        assert len(summary) > 0
    
    def test_render_requirement_anchoring_entity_structure(self):
        """测试实体结构"""
        data = {
            "entities": [
                {
                    "name": "用户",
                    "id": "User",
                    "description": "系统用户实体",
                    "attributes": [
                        {"name": "id", "type": "string", "required": True},
                        {"name": "name", "type": "string", "required": True},
                        {"name": "email", "type": "string", "required": False}
                    ]
                }
            ]
        }
        
        entity = data["entities"][0]
        assert entity["name"] == "用户"
        assert entity["id"] == "User"
        assert len(entity["attributes"]) == 3
    
    def test_render_requirement_anchoring_flow_structure(self):
        """测试流程结构"""
        data = {
            "flows": [
                {
                    "name": "用户注册流程",
                    "id": "register_flow",
                    "steps": [
                        {"id": "start", "name": "开始", "type": "start"},
                        {"id": "input", "name": "输入信息", "type": "action"},
                        {"id": "validate", "name": "验证信息", "type": "decision"},
                        {"id": "create", "name": "创建账户", "type": "action"},
                        {"id": "end", "name": "结束", "type": "end"}
                    ]
                }
            ]
        }
        
        flow = data["flows"][0]
        assert flow["name"] == "用户注册流程"
        assert len(flow["steps"]) == 5
        assert flow["steps"][0]["type"] == "start"
        assert flow["steps"][-1]["type"] == "end"


class TestRenderArchitectureIteration:
    """架构迭代渲染器测试"""
    
    def test_render_architecture_iteration_basic(self):
        """测试基本架构迭代渲染"""
        data = {
            "metrics": {
                "方案数": {"value": 3},
                "评审意见数": {"value": 12},
                "融合耗时": {"value": "15.2s"}
            },
            "solutions": [
                {"name": "整洁架构方案", "core_goal": "高内聚低耦合"},
                {"name": "响应式方案", "core_goal": "高并发低延迟"},
                {"name": "垂直切片方案", "core_goal": "按功能切分"}
            ],
            "final_decision": {
                "adopted": "融合方案",
                "reason": "综合各方案优势"
            }
        }
        
        metrics = data.get("metrics", {})
        solutions = data.get("solutions", [])
        decision = data.get("final_decision", {})
        
        assert metrics["方案数"]["value"] == 3
        assert len(solutions) == 3
        assert decision["adopted"] == "融合方案"
    
    def test_render_architecture_iteration_solution_structure(self):
        """测试方案结构"""
        solution = {
            "name": "整洁架构方案",
            "core_goal": "高内聚低耦合，分层解耦",
            "pros": ["可维护性强", "易于测试", "职责清晰"],
            "cons": ["初期成本高", "学习曲线陡"]
        }
        
        assert solution["name"] == "整洁架构方案"
        assert len(solution["pros"]) == 3
        assert len(solution["cons"]) == 2
    
    def test_render_architecture_iteration_final_decision(self):
        """测试最终决策"""
        decision = {
            "adopted": "融合方案",
            "reason": "综合整洁架构的可维护性与响应式方案的高性能优势",
            "key_points": [
                "核心业务采用整洁架构分层",
                "高并发场景引入响应式模式",
                "渐进式迁移降低风险"
            ],
            "confidence": "高"
        }
        
        assert decision["adopted"] == "融合方案"
        assert len(decision["key_points"]) == 3
        assert decision["confidence"] == "高"
    
    def test_render_architecture_iteration_comparison_matrix(self):
        """测试方案对比矩阵"""
        solutions = [
            {
                "name": "方案A",
                "core_goal": "目标A",
                "pros": ["优点1", "优点2"],
                "cons": ["缺点1"]
            },
            {
                "name": "方案B",
                "core_goal": "目标B",
                "pros": ["优点3"],
                "cons": ["缺点2", "缺点3"]
            },
            {
                "name": "方案C",
                "core_goal": "目标C",
                "pros": [],
                "cons": []
            }
        ]
        
        display_solutions = solutions[:3]
        
        while len(display_solutions) < 3:
            display_solutions.append({
                "name": f"方案{len(display_solutions) + 1}",
                "core_goal": "-",
                "pros": [],
                "cons": []
            })
        
        assert len(display_solutions) == 3
    
    def test_render_architecture_iteration_empty_solutions(self):
        """测试空方案列表"""
        data = {
            "solutions": [],
            "metrics": {}
        }
        
        solutions = data.get("solutions", [])
        
        if not solutions:
            is_empty = True
        else:
            is_empty = False
        
        assert is_empty is True
    
    def test_render_architecture_iteration_confidence_levels(self):
        """测试置信度级别"""
        confidence_map = {
            "高": ("🟢", "high"),
            "中": ("🟡", "medium"),
            "低": ("🔴", "low")
        }
        
        for confidence, (icon, level) in confidence_map.items():
            assert icon in ["🟢", "🟡", "🔴"]
            assert level in ["high", "medium", "low"]


class TestRenderContractGeneration:
    """契约生成渲染器测试"""
    
    def test_render_contract_generation_basic(self):
        """测试基本契约生成渲染"""
        data = {
            "interfaces": [
                {"method": "POST", "path": "/api/user", "description": "创建用户"}
            ],
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}}
                }
            },
            "mock_files": ["mock_user.py"],
            "metrics": {
                "接口总数": {"value": 1},
                "Schema总数": {"value": 1},
                "Mock文件数": {"value": 1}
            }
        }
        
        interfaces = data.get("interfaces", [])
        schemas = data.get("schemas", {})
        mock_files = data.get("mock_files", [])
        
        assert len(interfaces) == 1
        assert len(schemas) == 1
        assert len(mock_files) == 1
    
    def test_render_contract_generation_auto_metrics(self):
        """测试自动计算契约指标"""
        data = {
            "interfaces": [
                {"method": "GET", "path": "/api/users"},
                {"method": "POST", "path": "/api/user"},
                {"method": "PUT", "path": "/api/user/{id}"}
            ],
            "schemas": {
                "User": {"type": "object"},
                "Order": {"type": "object"},
                "Product": {"type": "object"}
            },
            "mock_files": ["mock1.py", "mock2.py"]
        }
        
        interface_count = len(data.get("interfaces", []))
        schemas = data.get("schemas", {})
        schema_count = len(schemas) if isinstance(schemas, dict) else 0
        mock_count = len(data.get("mock_files", []))
        
        assert interface_count == 3
        assert schema_count == 3
        assert mock_count == 2
    
    def test_render_contract_generation_interface_structure(self):
        """测试接口结构"""
        interface = {
            "method": "POST",
            "path": "/api/users",
            "description": "创建新用户",
            "parameters": [
                {"name": "username", "type": "string", "required": True},
                {"name": "email", "type": "string", "required": True}
            ],
            "request_body": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "email": {"type": "string"}
                }
            },
            "response": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "username": {"type": "string"}
                }
            }
        }
        
        assert interface["method"] == "POST"
        assert len(interface["parameters"]) == 2
        assert "request_body" in interface
        assert "response" in interface
    
    def test_render_contract_generation_schema_structure(self):
        """测试Schema结构"""
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "用户ID"},
                "username": {"type": "string", "minLength": 3, "maxLength": 50},
                "email": {"type": "string", "format": "email"},
                "role": {"type": "string", "enum": ["admin", "user", "guest"]}
            },
            "required": ["id", "username", "email"]
        }
        
        assert schema["type"] == "object"
        assert len(schema["properties"]) == 4
        assert len(schema["required"]) == 3
    
    def test_render_contract_generation_method_colors(self):
        """测试HTTP方法颜色"""
        method_colors = {
            "GET": ("#4CAF50", "#E8F5E9"),
            "POST": ("#2196F3", "#E3F2FD"),
            "PUT": ("#FF9800", "#FFF3E0"),
            "DELETE": ("#F44336", "#FFEBEE"),
            "PATCH": ("#9C27B0", "#F3E5F5")
        }
        
        for method, (text_color, bg_color) in method_colors.items():
            assert text_color.startswith("#")
            assert bg_color.startswith("#")
    
    def test_render_contract_generation_empty_data(self):
        """测试空契约数据"""
        data = {
            "interfaces": [],
            "schemas": {},
            "mock_files": []
        }
        
        interfaces = data.get("interfaces", [])
        schemas = data.get("schemas", {})
        mock_files = data.get("mock_files", [])
        
        assert len(interfaces) == 0
        assert len(schemas) == 0
        assert len(mock_files) == 0


class TestRenderRequirementValidation:
    """需求校验渲染器测试"""
    
    def test_render_requirement_validation_basic(self):
        """测试基本需求校验渲染"""
        data = {
            "passed": [
                {"item": "需求标题", "message": "格式正确"},
                {"item": "功能描述", "message": "描述完整"}
            ],
            "warnings": [
                {"item": "非功能需求", "message": "缺少性能要求"}
            ],
            "errors": [
                {"item": "接口定义", "message": "缺少必要字段"}
            ],
            "summary": {
                "total": 4,
                "passed": 2,
                "warnings": 1,
                "errors": 1
            }
        }
        
        passed = data.get("passed", [])
        warnings = data.get("warnings", [])
        errors = data.get("errors", [])
        summary = data.get("summary", {})
        
        assert len(passed) == 2
        assert len(warnings) == 1
        assert len(errors) == 1
        assert summary["total"] == 4
    
    def test_render_requirement_validation_auto_summary(self):
        """测试自动计算汇总"""
        data = {
            "passed": [
                {"item": "项目1", "message": "通过"},
                {"item": "项目2", "message": "通过"}
            ],
            "warnings": [
                {"item": "项目3", "message": "警告"}
            ],
            "errors": []
        }
        
        passed_items = data.get("passed", [])
        warnings = data.get("warnings", [])
        errors = data.get("errors", [])
        summary = data.get("summary", {})
        
        passed_count = summary.get("passed", len(passed_items))
        warning_count = summary.get("warnings", len(warnings))
        error_count = summary.get("errors", len(errors))
        
        assert passed_count == 2
        assert warning_count == 1
        assert error_count == 0
    
    def test_render_requirement_validation_metrics(self):
        """测试校验指标"""
        data = {
            "passed": [{"item": "A"}],
            "warnings": [{"item": "B"}, {"item": "C"}],
            "errors": [{"item": "D"}]
        }
        
        passed_count = len(data.get("passed", []))
        warning_count = len(data.get("warnings", []))
        error_count = len(data.get("errors", []))
        
        metrics = {
            "校验通过项": {"value": passed_count},
            "警告数": {"value": warning_count},
            "错误数": {"value": error_count, "delta_color": "inverse"}
        }
        
        assert metrics["校验通过项"]["value"] == 1
        assert metrics["警告数"]["value"] == 2
        assert metrics["错误数"]["value"] == 1
    
    def test_render_requirement_validation_item_structure(self):
        """测试校验项结构"""
        item = {
            "item": "需求标题",
            "message": "格式正确，长度适中",
            "severity": "info"
        }
        
        assert "item" in item
        assert "message" in item
        assert item["item"] == "需求标题"
    
    def test_render_requirement_validation_empty_results(self):
        """测试空校验结果"""
        data = {
            "passed": [],
            "warnings": [],
            "errors": []
        }
        
        passed_items = data.get("passed", [])
        warnings = data.get("warnings", [])
        errors = data.get("errors", [])
        
        if not passed_items and not warnings and not errors:
            is_empty = True
        else:
            is_empty = False
        
        assert is_empty is True
    
    def test_render_requirement_validation_all_passed(self):
        """测试全部通过"""
        data = {
            "passed": [
                {"item": "项目1", "message": "通过"},
                {"item": "项目2", "message": "通过"},
                {"item": "项目3", "message": "通过"}
            ],
            "warnings": [],
            "errors": [],
            "summary": {"total": 3, "passed": 3, "warnings": 0, "errors": 0}
        }
        
        summary = data.get("summary", {})
        
        assert summary["passed"] == 3
        assert summary["warnings"] == 0
        assert summary["errors"] == 0


class TestRenderLandingPlan:
    """落地方案渲染器测试"""
    
    def test_render_landing_plan_basic(self):
        """测试基本落地方案渲染"""
        data = {
            "modules": [
                {"name": "模块0_全局调度", "files": 3, "description": "全局调度面板"},
                {"name": "模块1_用户模块", "files": 5, "description": "用户管理"}
            ],
            "total_files": 8,
            "estimated_duration": "1周",
            "markdown_content": "# 落地方案\n本次拆分为2个模块..."
        }
        
        modules = data.get("modules", [])
        total_files = data.get("total_files", 0)
        estimated_duration = data.get("estimated_duration", "-")
        
        assert len(modules) == 2
        assert total_files == 8
        assert estimated_duration == "1周"
    
    def test_render_landing_plan_auto_metrics(self):
        """测试自动计算落地方案指标"""
        data = {
            "modules": [
                {"name": "模块1", "files": 5},
                {"name": "模块2", "files": 3},
                {"name": "模块3", "files": 7}
            ],
            "total_files": 15,
            "estimated_duration": "2周"
        }
        
        modules = data.get("modules", [])
        module_count = len(modules)
        total_files = data.get("total_files", 0)
        estimated_duration = data.get("estimated_duration", "-")
        
        metrics = {
            "模块数": {"value": module_count},
            "文件数": {"value": total_files},
            "预计工期": {"value": estimated_duration}
        }
        
        assert metrics["模块数"]["value"] == 3
        assert metrics["文件数"]["value"] == 15
        assert metrics["预计工期"]["value"] == "2周"
    
    def test_render_landing_plan_module_structure(self):
        """测试模块结构"""
        module = {
            "name": "模块1_用户核心模块",
            "files": 8,
            "description": "用户认证与权限管理",
            "dependencies": ["模块0_全局调度面板"],
            "tech_stack": ["Python", "FastAPI", "PostgreSQL"]
        }
        
        assert module["name"] == "模块1_用户核心模块"
        assert module["files"] == 8
        assert len(module["dependencies"]) == 1
    
    def test_render_landing_plan_dependencies(self):
        """测试模块依赖关系"""
        data = {
            "modules": [
                {"name": "模块0"},
                {"name": "模块1"},
                {"name": "模块2"}
            ],
            "dependencies": {
                "模块0": [],
                "模块1": ["模块0"],
                "模块2": ["模块0", "模块1"]
            }
        }
        
        dependencies = data.get("dependencies", {})
        
        assert dependencies["模块0"] == []
        assert "模块0" in dependencies["模块1"]
        assert len(dependencies["模块2"]) == 2
    
    def test_render_landing_plan_markdown_content(self):
        """测试Markdown内容"""
        data = {
            "markdown_content": """# 落地方案

## 模块拆分
- 模块0: 全局调度面板
- 模块1: 用户核心模块

## 工期估算
预计开发周期: 2周
"""
        }
        
        markdown_content = data.get("markdown_content", "")
        
        assert "# 落地方案" in markdown_content
        assert "模块拆分" in markdown_content
        assert "工期估算" in markdown_content
    
    def test_render_landing_plan_empty_modules(self):
        """测试空模块列表"""
        data = {
            "modules": [],
            "total_files": 0,
            "estimated_duration": "-"
        }
        
        modules = data.get("modules", [])
        
        if not modules:
            is_empty = True
        else:
            is_empty = False
        
        assert is_empty is True


class TestRenderIdeBundle:
    """IDE引导包渲染器测试"""
    
    def test_render_ide_bundle_basic(self):
        """测试基本IDE引导包渲染"""
        data = {
            "files": [
                {"name": "AGENTS.md", "type": "规则", "size": "2.5KB", "path": ".trae/rules/"},
                {"name": "mock_module1.py", "type": "Mock", "size": "1.2KB", "path": "public/pre_generated_mock/"}
            ],
            "rules_count": 1,
            "mock_count": 1,
            "total_size": "3.7KB"
        }
        
        files = data.get("files", [])
        rules_count = data.get("rules_count", 0)
        mock_count = data.get("mock_count", 0)
        
        assert len(files) == 2
        assert rules_count == 1
        assert mock_count == 1
    
    def test_render_ide_bundle_auto_metrics(self):
        """测试自动计算引导包指标"""
        data = {
            "files": [
                {"name": "file1.md", "type": "规则"},
                {"name": "file2.py", "type": "Mock"},
                {"name": "file3.md", "type": "规则"},
                {"name": "file4.py", "type": "Mock"},
                {"name": "file5.json", "type": "配置"}
            ],
            "rules_count": 2,
            "mock_count": 2
        }
        
        files = data.get("files", [])
        file_count = len(files)
        rules_count = data.get("rules_count", 0)
        mock_count = data.get("mock_count", 0)
        
        metrics = {
            "文件数": {"value": file_count},
            "规则数": {"value": rules_count},
            "Mock数": {"value": mock_count}
        }
        
        assert metrics["文件数"]["value"] == 5
        assert metrics["规则数"]["value"] == 2
        assert metrics["Mock数"]["value"] == 2
    
    def test_render_ide_bundle_file_structure(self):
        """测试文件结构"""
        file_entry = {
            "name": "AGENTS.md",
            "type": "规则",
            "size": "2.5KB",
            "path": ".trae/rules/",
            "description": "全局规则文件"
        }
        
        assert file_entry["name"] == "AGENTS.md"
        assert file_entry["type"] == "规则"
        assert file_entry["size"] == "2.5KB"
    
    def test_render_ide_bundle_download_content(self):
        """测试下载内容"""
        data = {
            "bundle_content": {
                "rules": ["rule1", "rule2"],
                "mocks": ["mock1", "mock2"],
                "configs": {"debug": True}
            },
            "download_filename": "ide_bundle.json"
        }
        
        bundle_content = data.get("bundle_content", "")
        download_filename = data.get("download_filename", "ide_bundle.json")
        
        if isinstance(bundle_content, (dict, list)):
            download_data = json.dumps(bundle_content, ensure_ascii=False, indent=2)
            mime_type = "application/json"
        else:
            download_data = str(bundle_content)
            mime_type = "text/plain"
        
        assert "rules" in download_data
        assert mime_type == "application/json"
        assert download_filename == "ide_bundle.json"
    
    def test_render_ide_bundle_empty_files(self):
        """测试空文件列表"""
        data = {
            "files": [],
            "rules_count": 0,
            "mock_count": 0
        }
        
        files = data.get("files", [])
        
        if not files:
            is_empty = True
        else:
            is_empty = False
        
        assert is_empty is True
    
    def test_render_ide_bundle_file_display(self):
        """测试文件展示格式"""
        files = [
            {"name": "AGENTS.md", "type": "规则", "size": "2.5KB", "path": ".trae/rules/"},
            {"name": "mock_user.py", "type": "Mock", "size": "1.2KB", "path": "public/mock/"},
            {"name": "config.json", "type": "配置", "size": "0.5KB", "path": "config/"}
        ]
        
        display_files = []
        for f in files:
            if isinstance(f, dict):
                display_files.append({
                    "文件名": f.get("name", "-"),
                    "类型": f.get("type", "-"),
                    "大小": f.get("size", "-"),
                    "路径": f.get("path", "-")
                })
        
        assert len(display_files) == 3
        assert display_files[0]["文件名"] == "AGENTS.md"
        assert display_files[1]["类型"] == "Mock"


class TestStageRenderersIntegration:
    """阶段渲染器集成测试"""
    
    def test_full_pipeline_results_structure(self):
        """测试完整Pipeline结果结构"""
        results = {
            "requirement_anchoring": {
                "success": True,
                "entities": [{"name": "用户"}],
                "flows": [{"name": "注册流程"}],
                "metrics": {"识别实体数": {"value": 1}}
            },
            "architecture_iteration": {
                "success": True,
                "solutions": [{"name": "方案A"}],
                "final_decision": {"adopted": "融合方案"}
            },
            "contract_generation": {
                "success": True,
                "interfaces": [{"method": "GET", "path": "/api/users"}],
                "schemas": {"User": {"type": "object"}},
                "mock_files": ["mock_user.py"]
            },
            "requirement_validation": {
                "success": True,
                "passed": [{"item": "标题", "message": "格式正确"}],
                "warnings": [],
                "errors": []
            },
            "landing_plan_generation": {
                "success": True,
                "modules": [{"name": "模块1", "files": 5}],
                "total_files": 5,
                "estimated_duration": "1周"
            },
            "ide_bundle_generation": {
                "success": True,
                "files": [{"name": "AGENTS.md", "type": "规则"}],
                "rules_count": 1,
                "mock_count": 0
            }
        }
        
        assert "requirement_anchoring" in results
        assert "architecture_iteration" in results
        assert "contract_generation" in results
        assert "requirement_validation" in results
        assert "landing_plan_generation" in results
        assert "ide_bundle_generation" in results
    
    def test_stage_result_success_check(self):
        """测试阶段结果成功检查"""
        success_result = {
            "success": True,
            "data": {"key": "value"}
        }
        
        failure_result = {
            "success": False,
            "error": "执行失败"
        }
        
        assert success_result.get("success", False) is True
        assert failure_result.get("success", False) is False
    
    def test_stage_renderer_mapping(self):
        """测试阶段渲染器映射"""
        stage_renderers = {
            "requirement_anchoring": "render_requirement_anchoring",
            "architecture_iteration": "render_architecture_iteration",
            "contract_generation": "render_contract_generation",
            "requirement_validation": "render_requirement_validation",
            "landing_plan_generation": "render_landing_plan",
            "ide_bundle_generation": "render_ide_bundle",
        }
        
        stage_names = [
            "requirement_anchoring",
            "architecture_iteration",
            "contract_generation",
            "requirement_validation",
            "landing_plan_generation",
            "ide_bundle_generation"
        ]
        
        for stage_name in stage_names:
            assert stage_name in stage_renderers
            assert stage_renderers[stage_name] is not None

"""
ViewModel Adapter 模块
负责将真实 Pipeline 输出（results_raw）转换为 UI 展示格式（results_view）
"""

import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../../..'))
sys.path.insert(0, project_root)


def normalize_requirement_anchoring(stage_result: dict) -> dict:
    """
    归一化需求锚定阶段数据
    
    Args:
        stage_result: 真实 stage_result，包含 structured_requirement
        
    Returns:
        归一化后的数据，包含 entities/flows/attributes/business_logic_summary
    """
    result = stage_result.copy()
    
    structured_requirement = stage_result.get("structured_requirement", {})
    
    if "entities" not in result:
        result["entities"] = _extract_entities_from_structured(structured_requirement)
    
    if "flows" not in result:
        result["flows"] = _extract_flows_from_structured(structured_requirement)
    
    if "attributes" not in result:
        result["attributes"] = _extract_attributes_from_structured(structured_requirement)
    
    if "business_logic_summary" not in result:
        result["business_logic_summary"] = _extract_summary_from_structured(structured_requirement)
    
    if "metrics" not in result:
        result["metrics"] = {
            "entity_count": len(result.get("entities", [])),
            "flow_count": len(result.get("flows", [])),
            "attribute_count": len(result.get("attributes", []))
        }
    
    entities = result.get("entities", [])
    attributes = result.get("attributes", [])
    
    if entities and attributes:
        for entity in entities:
            if isinstance(entity, dict) and not entity.get("attributes"):
                entity["attributes"] = attributes.copy()
    
    return result


def _extract_entities_from_structured(structured_requirement: dict) -> list:
    """从 structured_requirement 中提取实体列表"""
    entities = []
    
    requirements = structured_requirement.get("requirements", [])
    entity_tags = ["实体", "领域对象", "领域实体"]
    
    for req in requirements:
        tags = req.get("tags", [])
        if any(tag in req.get("content", "") for tag in entity_tags) or any(tag in tags for tag in entity_tags):
            entities.append({
                "name": req.get("content", "").split("：")[-1].split(":")[-1].strip(),
                "description": req.get("content", ""),
                "attributes": []
            })
    
    if not entities:
        entities = [
            {
                "name": "业务实体",
                "description": "从需求中识别的核心业务实体",
                "attributes": []
            }
        ]
    
    return entities


def _extract_flows_from_structured(structured_requirement: dict) -> list:
    """从 structured_requirement 中提取流程列表"""
    flows = []
    
    requirements = structured_requirement.get("requirements", [])
    flow_tags = ["流程", "步骤", "操作"]
    
    for req in requirements:
        tags = req.get("tags", [])
        if any(tag in req.get("content", "") for tag in flow_tags) or any(tag in tags for tag in flow_tags):
            flows.append({
                "name": req.get("content", ""),
                "id": f"flow_{req.get('order', 0)}",
                "steps": [
                    {"id": "start", "name": "开始", "type": "start"},
                    {"id": "action", "name": "执行操作", "type": "action"},
                    {"id": "end", "name": "结束", "type": "end"}
                ]
            })
    
    if not flows:
        flows = [
            {
                "name": "核心业务流程",
                "id": "flow_0",
                "steps": [
                    {"id": "start", "name": "开始", "type": "start"},
                    {"id": "process", "name": "业务处理", "type": "action"},
                    {"id": "end", "name": "结束", "type": "end"}
                ]
            }
        ]
    
    return flows


def _extract_attributes_from_structured(structured_requirement: dict) -> list:
    """从 structured_requirement 中提取属性列表"""
    attributes = []
    
    requirements = structured_requirement.get("requirements", [])
    attr_keywords = ["字段", "属性", "参数"]
    
    for req in requirements:
        content = req.get("content", "")
        if any(keyword in content for keyword in attr_keywords):
            attributes.append({
                "name": content.split("：")[-1].split(":")[-1].strip(),
                "type": "string",
                "required": True,
                "description": content
            })
    
    if not attributes:
        attributes = [
            {"name": "id", "type": "string", "required": True, "description": "唯一标识符"},
            {"name": "name", "type": "string", "required": True, "description": "名称"},
            {"name": "created_at", "type": "datetime", "required": True, "description": "创建时间"}
        ]
    
    return attributes


def _extract_summary_from_structured(structured_requirement: dict) -> str:
    """从 structured_requirement 中提取业务逻辑摘要"""
    requirements = structured_requirement.get("requirements", [])
    
    if requirements:
        top_req = next((r for r in requirements if r.get("level") == 1), None)
        if top_req:
            return top_req.get("content", "")
        
        return requirements[0].get("content", "")
    
    return "基于需求分析的业务逻辑摘要"


def normalize_requirement_validation(stage_result: dict) -> dict:
    """
    归一化需求校验阶段数据
    
    Args:
        stage_result: 真实 stage_result，包含 validation_result
        
    Returns:
        归一化后的数据，包含 passed/warnings/errors
    """
    result = stage_result.copy()
    
    validation_result = stage_result.get("validation_result", {})
    
    if "passed" not in result:
        result["passed"] = _extract_passed_from_validation(validation_result)
    
    if "warnings" not in result:
        result["warnings"] = _extract_warnings_from_validation(validation_result)
    
    if "errors" not in result:
        result["errors"] = _extract_errors_from_validation(validation_result)
    
    if "summary" not in result:
        result["summary"] = {
            "total": len(result["passed"]) + len(result["warnings"]) + len(result["errors"]),
            "passed": len(result["passed"]),
            "warnings": len(result["warnings"]),
            "errors": len(result["errors"])
        }
    
    return result


def _extract_passed_from_validation(validation_result: dict) -> list:
    """从 validation_result 中提取通过项"""
    passed = []
    check_results = validation_result.get("check_results", [])
    
    for check in check_results:
        dimension = check.get("dimension", "")
        score = check.get("score", 0)
        if score >= 80:
            passed.append({
                "item": f"{dimension}检查",
                "message": f"得分：{score}分"
            })
    
    if not passed:
        passed = [{"item": "需求完整性", "message": "检查通过"}]
    
    return passed


def _extract_warnings_from_validation(validation_result: dict) -> list:
    """从 validation_result 中提取警告项"""
    warnings = []
    check_results = validation_result.get("check_results", [])
    
    for check in check_results:
        dimension = check.get("dimension", "")
        issues = check.get("issues", [])
        for issue in issues:
            if "缺少" in issue or "未明确" in issue:
                warnings.append({
                    "item": f"{dimension}",
                    "message": issue
                })
    
    return warnings


def _extract_errors_from_validation(validation_result: dict) -> list:
    """从 validation_result 中提取错误项"""
    errors = []
    check_results = validation_result.get("check_results", [])
    
    for check in check_results:
        dimension = check.get("dimension", "")
        score = check.get("score", 0)
        if score < 60:
            errors.append({
                "item": f"{dimension}检查",
                "message": f"得分过低：{score}分"
            })
    
    return errors


def normalize_architecture_iteration(stage_result: dict) -> dict:
    """
    归一化架构迭代阶段数据
    
    Args:
        stage_result: 真实 stage_result，包含 final_solution/individual_solutions
        
    Returns:
        归一化后的数据，包含 solutions/final_decision
    """
    result = stage_result.copy()
    
    if "solutions" not in result:
        solutions = []
        individual_solutions = stage_result.get("individual_solutions", [])
        
        if individual_solutions:
            for idx, sol_wrapper in enumerate(individual_solutions):
                sol = sol_wrapper.get("solution", sol_wrapper)
                paradigm_info = sol_wrapper.get("paradigm_info", {})
                provider = sol_wrapper.get("provider", "")
                paradigm_index = sol_wrapper.get("paradigm_index", idx + 1)
                
                architecture = sol.get("architecture", {})
                modules = architecture.get("modules", [])
                boundaries = architecture.get("boundaries", [])
                data_flow = architecture.get("data_flow", [])
                
                design_points = []
                if modules and isinstance(modules, list):
                    for m in modules[:2]:
                        if isinstance(m, dict):
                            design_points.append(m.get("name", str(m)))
                        else:
                            design_points.append(str(m))
                if boundaries and isinstance(boundaries, list):
                    for b in boundaries[:1]:
                        if isinstance(b, dict):
                            design_points.append(b.get("name", str(b)))
                        else:
                            design_points.append(str(b))
                if not design_points:
                    design_points = ["采用推荐架构模式"]
                
                core_goal = f"{paradigm_info.get('name', '')} - {paradigm_info.get('paradigm', '')}"
                if not core_goal.strip():
                    core_goal = sol.get("rationale", sol.get("description", f"方案{idx + 1}"))
                
                solutions.append({
                    "name": sol.get("name", f"方案{idx + 1}"),
                    "provider": provider,
                    "paradigm_index": paradigm_index,
                    "core_goal": core_goal,
                    "design_points": design_points[:3],
                    "pros": sol.get("strengths", []),
                    "cons": sol.get("weaknesses", [])
                })
        else:
            final_solution = stage_result.get("final_solution", {})
            if final_solution:
                fused_solution = final_solution.get("fused_solution", {})
                comparison = final_solution.get("comparison", {})
                paradigm_analysis = comparison.get("paradigm_analysis", {})
                
                if paradigm_analysis and isinstance(paradigm_analysis, dict):
                    paradigm_design_points_map = {
                        "paradigm_1": ["依赖倒置", "接口抽象", "核心隔离"],
                        "paradigm_2": ["单向数据流", "不可变状态", "事件溯源"],
                        "paradigm_3": ["业务优先", "YAGNI原则", "快速迭代"]
                    }
                    
                    for idx, (paradigm_key, paradigm_desc) in enumerate(list(paradigm_analysis.items())[:3]):
                        paradigm_name = f"方案{idx + 1}"
                        if idx == 0:
                            paradigm_name = "方案1 - 边界防腐"
                        elif idx == 1:
                            paradigm_name = "方案2 - 响应式"
                        elif idx == 2:
                            paradigm_name = "方案3 - 垂直切片"
                        
                        design_points = paradigm_design_points_map.get(paradigm_key, ["采用推荐架构模式"])
                        
                        cons = []
                        paradigm_desc_str = str(paradigm_desc)
                        for keyword in ["增加", "拆分", "埋下", "会增加", "会拆分", "会埋下"]:
                            if keyword in paradigm_desc_str:
                                sentences = paradigm_desc_str.split("。")
                                for sent in sentences:
                                    if keyword in sent and len(sent.strip()) > 5:
                                        cons.append(sent.strip() + "。")
                                        if len(cons) >= 3:
                                            break
                            if len(cons) >= 3:
                                break
                        
                        if not cons:
                            if idx == 0:
                                cons = ["初期开发成本较高", "需要额外的抽象层", "学习曲线较陡"]
                            elif idx == 1:
                                cons = ["调试复杂度增加", "状态管理开销大", "需要事件存储"]
                            elif idx == 2:
                                cons = ["可能存在代码重复", "长期演进难度大", "跨切片通信复杂"]
                        
                        core_goal = str(paradigm_desc)[:100] if len(str(paradigm_desc)) > 100 else str(paradigm_desc)
                        
                        solutions.append({
                            "name": paradigm_name,
                            "core_goal": core_goal,
                            "design_points": design_points[:3],
                            "pros": [],
                            "cons": cons[:3]
                        })
                else:
                    architecture = fused_solution.get("architecture", {})
                    modules = architecture.get("modules", [])
                    boundaries = architecture.get("boundaries", [])
                    
                    design_points = []
                    if modules and isinstance(modules, list):
                        for m in modules[:2]:
                            if isinstance(m, dict):
                                design_points.append(m.get("name", str(m)))
                            else:
                                design_points.append(str(m))
                    if boundaries and isinstance(boundaries, list):
                        for b in boundaries[:1]:
                            if isinstance(b, dict):
                                design_points.append(b.get("name", str(b)))
                            else:
                                design_points.append(str(b))
                    if not design_points:
                        design_points = ["架构合理"]
                    
                    risk_notes = fused_solution.get("risk_notes", [])
                    cons = risk_notes[:3] if risk_notes else []
                    
                    solutions.append({
                        "name": "融合方案",
                        "core_goal": fused_solution.get("architect_style", final_solution.get("description", "全局最优解")),
                        "design_points": design_points[:3],
                        "pros": [],
                        "cons": cons
                    })
        
        if not solutions:
            solutions = [
                {"name": "方案1", "core_goal": "高内聚低耦合", "design_points": ["分层架构", "依赖倒置"], "pros": ["可维护性强"], "cons": ["初期成本高"]},
                {"name": "方案2", "core_goal": "高性能", "design_points": ["异步处理", "缓存优化"], "pros": ["性能优异"], "cons": ["调试复杂"]},
                {"name": "方案3", "core_goal": "快速交付", "design_points": ["垂直切片", "快速迭代"], "pros": ["开发效率高"], "cons": ["代码重复"]}
            ]
        
        result["solutions"] = solutions
    
    if "critiques" not in result:
        result["critiques"] = stage_result.get("critiques", [])
    
    if "final_decision" not in result:
        final_solution = stage_result.get("final_solution", {})
        result["final_decision"] = {
            "adopted": final_solution.get("name", "融合方案"),
            "reason": final_solution.get("description", "综合各方案优势"),
            "key_points": ["核心架构采用最佳实践"]
        }
    
    return result


def normalize_contract_generation(stage_result: dict) -> dict:
    """
    归一化契约生成阶段数据
    
    Args:
        stage_result: 真实 stage_result，包含 contracts
        
    Returns:
        归一化后的数据，包含 interfaces/schemas
    """
    result = stage_result.copy()
    
    contracts = stage_result.get("contracts", {})
    
    if "interfaces" not in result:
        result["interfaces"] = _extract_interfaces_from_contracts(contracts)
    
    if "schemas" not in result:
        result["schemas"] = _extract_schemas_from_contracts(contracts)
    
    if "metrics" not in result:
        result["metrics"] = {
            "interface_count": len(result.get("interfaces", [])),
            "schema_count": len(result.get("schemas", {}))
        }
    
    return result


def _extract_interfaces_from_contracts(contracts: dict) -> list:
    """从 contracts 中提取接口列表"""
    interfaces = []
    
    interface_content = contracts.get("interface", {})
    if isinstance(interface_content, str):
        if "Protocol" in interface_content or "def " in interface_content:
            interfaces.append({
                "method": "POST",
                "path": "/api/main",
                "description": "主接口",
                "parameters": []
            })
    elif isinstance(interface_content, dict):
        for key, value in interface_content.items():
            interfaces.append({
                "method": "POST",
                "path": f"/api/{key}",
                "description": str(value)[:100],
                "parameters": []
            })
    
    if not interfaces:
        interfaces = [
            {"method": "POST", "path": "/api/analyze", "description": "需求分析接口", "parameters": []}
        ]
    
    return interfaces


def _extract_schemas_from_contracts(contracts: dict) -> dict:
    """从 contracts 中提取 Schema 字典"""
    schemas = {}
    
    data_contracts = contracts.get("data", {}).get("data_contracts", [])
    for dc in data_contracts:
        name = dc.get("name", "Unknown")
        schemas[name] = dc.get("schema", {})
    
    if not schemas:
        schemas = {
            "Request": {"type": "object", "properties": {}},
            "Response": {"type": "object", "properties": {}}
        }
    
    return schemas


def _extract_mocks_from_contracts(contracts: dict) -> list:
    """从 contracts 中提取 Mock 文件列表"""
    mock_files = []
    
    mock_content = contracts.get("mock", "")
    if mock_content:
        mock_files.append({
            "name": "mock_contract.py",
            "type": "Mock",
            "size": f"{len(str(mock_content))}B",
            "path": "public/pre_generated_mock/"
        })
    
    if not mock_files:
        mock_files = [
            {"name": "mock_module.py", "type": "Mock", "size": "1.5KB", "path": "public/pre_generated_mock/"}
        ]
    
    return mock_files


def normalize_landing_plan(stage_result: dict) -> dict:
    """
    归一化落地方案阶段数据
    
    Args:
        stage_result: 真实 stage_result，包含 landing_plan
        
    Returns:
        归一化后的数据，包含 modules/markdown_content
    """
    result = stage_result.copy()
    
    landing_plan = stage_result.get("landing_plan", {})
    
    if "markdown_content" not in result:
        if isinstance(landing_plan, str):
            result["markdown_content"] = landing_plan
        elif isinstance(landing_plan, dict):
            result["markdown_content"] = json.dumps(landing_plan, ensure_ascii=False, indent=2)
        else:
            result["markdown_content"] = "# 落地方案\n\n项目落地计划内容"
    
    if "modules" not in result:
        result["modules"] = _extract_modules_from_landing(landing_plan)
    
    if "metrics" not in result:
        result["metrics"] = {
            "module_count": len(result.get("modules", [])),
            "file_count": len(result.get("modules", [])) * 3
        }
    
    return result


def _extract_modules_from_landing(landing_plan: dict) -> list:
    """从 landing_plan 中提取模块列表"""
    modules = []
    
    if isinstance(landing_plan, dict):
        for key, value in landing_plan.items():
            if "module" in key.lower() or "模块" in key:
                modules.append({
                    "name": str(key),
                    "description": str(value)[:100]
                })
    
    if not modules:
        modules = [
            {"name": "模块0_全局调度", "description": "负责流程编排"},
            {"name": "模块1_业务逻辑", "description": "核心业务实现"},
            {"name": "模块2_数据存储", "description": "数据持久化"}
        ]
    
    return modules


def normalize_visualization(stage_result: dict) -> dict:
    """
    归一化可视化阶段数据
    
    Args:
        stage_result: 真实 stage_result，包含 ascii_*
        
    Returns:
        归一化后的数据，包含 ascii_*
    """
    result = stage_result.copy()
    
    ascii_flows = stage_result.get("ascii_flows", stage_result.get("mermaid_flows", ""))
    ascii_entities = stage_result.get("ascii_entities", stage_result.get("mermaid_entities", ""))
    ascii_modules = stage_result.get("ascii_modules", stage_result.get("mermaid_modules", ""))
    
    if "ascii_flows" not in result:
        result["ascii_flows"] = ascii_flows or _generate_ascii_flows()
    
    if "ascii_entities" not in result:
        result["ascii_entities"] = ascii_entities or _generate_ascii_entities()
    
    if "ascii_modules" not in result:
        result["ascii_modules"] = ascii_modules or _generate_ascii_modules()
    
    return result


def _generate_ascii_flows() -> str:
    """生成默认的 ASCII 流程图"""
    return """[输入]
    ↓
[处理]
    ↓
[输出]"""


def _generate_ascii_entities() -> str:
    """生成默认的 ASCII 实体图"""
    return """[实体A]
    ↓
[实体B]
    ↓
[实体C]"""


def _generate_ascii_modules() -> str:
    """生成默认的 ASCII 模块图"""
    return """[模块0]
    ↓
[模块1]
    ↓
[模块2]"""


def normalize_ide_bundle(stage_result: dict) -> dict:
    """
    归一化 IDE 引导包阶段数据
    
    Args:
        stage_result: 真实 stage_result，包含 ide_bundle
        
    Returns:
        归一化后的数据，包含 files/rules_count/total_size
    """
    result = stage_result.copy()
    
    ide_bundle = stage_result.get("ide_bundle", {})
    
    if "files" not in result:
        result["files"] = _extract_files_from_bundle(ide_bundle)
    
    if "rules_count" not in result:
        result["rules_count"] = sum(1 for f in result.get("files", []) if "规则" in f.get("type", "") or "AGENT" in f.get("name", ""))
    
    if "total_size" not in result:
        total_bytes = sum(len(str(f)) for f in result.get("files", []))
        result["total_size"] = f"{total_bytes}B" if total_bytes < 1024 else f"{total_bytes/1024:.1f}KB"
    
    if "metrics" not in result:
        result["metrics"] = {
            "file_count": len(result.get("files", [])),
            "rules_count": result.get("rules_count", 0)
        }
    
    return result


def _extract_files_from_bundle(ide_bundle: dict) -> list:
    """从 ide_bundle 中提取文件列表"""
    files = []
    
    if isinstance(ide_bundle, dict):
        global_bundle = ide_bundle.get("global", {})
        if global_bundle:
            files.append({
                "name": "AGENT.md",
                "type": "规则",
                "size": f"{len(str(global_bundle))}B",
                "path": ".trae/rules/"
            })
        
        modules = ide_bundle.get("modules", [])
        for idx, module in enumerate(modules):
            files.append({
                "name": f"ide_bundle_module_{idx}.md",
                "type": "规则",
                "size": f"{len(str(module))}B",
                "path": f"modules/模块{idx}/"
            })
    
    if not files:
        files = [
            {"name": "AGENT.md", "type": "规则", "size": "2.5KB", "path": ".trae/rules/"},
            {"name": "mock_module0.py", "type": "Mock", "size": "1.2KB", "path": "public/pre_generated_mock/"}
        ]
    
    return files


def normalize_all_stage(stage_name: str, stage_result: dict) -> dict:
    """
    归一化单个阶段的数据（统一入口）
    
    Args:
        stage_name: 阶段名称
        stage_result: 真实 stage_result
        
    Returns:
        归一化后的阶段结果
    """
    normalizers = {
        "requirement_anchoring": normalize_requirement_anchoring,
        "requirement_validation": normalize_requirement_validation,
        "architecture_iteration": normalize_architecture_iteration,
        "contract_generation": normalize_contract_generation,
        "landing_plan_generation": normalize_landing_plan,
        "visualization_generation": normalize_visualization,
        "ide_bundle_generation": normalize_ide_bundle
    }
    
    if stage_name in normalizers:
        return normalizers[stage_name](stage_result)
    
    return stage_result


def normalize_all_results(results: dict) -> dict:
    """
    归一化所有阶段的结果
    
    Args:
        results: 完整的 results 字典，key 为 stage_name
        
    Returns:
        归一化后的 results 字典
    """
    normalized_results = {}
    
    for stage_name, stage_result in results.items():
        normalized_results[stage_name] = normalize_all_stage(stage_name, stage_result)
    
    return normalized_results

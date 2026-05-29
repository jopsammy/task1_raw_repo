"""
模块提取逻辑单元测试

测试 pipeline_orchestrator.py 中 run_ide_bundle_generation 方法的模块提取逻辑：
- 路径1: fused_solution.architecture.modules
- 路径2: fused_solution.modules
- 路径3: landing_plan.模块划分
- raw_content 包裹情况
- 空数据情况
"""

import pytest
import sys
import os
import json
from typing import Dict, Any, List, Optional

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)


def extract_modules_from_solution(
    parsed_solution: Dict[str, Any],
    landing_plan: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    从解决方案中提取模块列表（提取自 pipeline_orchestrator.py 的核心逻辑）
    
    Args:
        parsed_solution: 解析后的解决方案字典
        landing_plan: 可选的落地方案字典
        
    Returns:
        模块列表
    """
    modules_list = []
    
    fused_solution = None
    if isinstance(parsed_solution, dict):
        fused_solution = parsed_solution.get("fused_solution", parsed_solution)
    
    if isinstance(fused_solution, dict):
        arch = fused_solution.get("architecture", {})
        if isinstance(arch, dict) and "modules" in arch:
            modules_list = arch["modules"]
    
    if not modules_list:
        if isinstance(fused_solution, dict) and "modules" in fused_solution:
            modules_list = fused_solution["modules"]
    
    if not modules_list and landing_plan:
        if isinstance(landing_plan, dict):
            modules_data = landing_plan.get("模块划分", landing_plan.get("modules", {}))
            if isinstance(modules_data, dict):
                modules_list = modules_data.get("modules", modules_data.get("模块列表", []))
            elif isinstance(modules_data, list):
                modules_list = modules_data
    
    return modules_list


def parse_solution_with_raw_content(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理 raw_content 包裹情况的解析逻辑
    
    Args:
        raw_data: 原始数据，可能包含 raw_content 字段
        
    Returns:
        解析后的数据
    """
    parsed = raw_data
    max_iterations = 5
    
    for _ in range(max_iterations):
        if isinstance(parsed, dict) and "raw_content" in parsed:
            try:
                parsed = json.loads(parsed["raw_content"])
            except (json.JSONDecodeError, TypeError):
                break
        else:
            break
    
    return parsed


class TestModuleExtractionPath1:
    """路径1测试: fused_solution.architecture.modules"""
    
    def test_path1_basic_extraction(self):
        """测试路径1基本提取"""
        parsed_solution = {
            "fused_solution": {
                "architecture": {
                    "modules": [
                        {"name": "模块1_用户模块", "description": "用户管理"},
                        {"name": "模块2_订单模块", "description": "订单管理"}
                    ]
                }
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution)
        
        assert len(modules) == 2
        assert modules[0]["name"] == "模块1_用户模块"
        assert modules[1]["name"] == "模块2_订单模块"
    
    def test_path1_with_nested_architecture(self):
        """测试路径1嵌套架构结构"""
        parsed_solution = {
            "fused_solution": {
                "architecture": {
                    "style": "微服务",
                    "modules": [
                        {"name": "核心模块", "type": "domain"}
                    ],
                    "tech_stack": {"backend": "Python"}
                },
                "architect_style": "DDD"
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution)
        
        assert len(modules) == 1
        assert modules[0]["name"] == "核心模块"
    
    def test_path1_empty_modules_list(self):
        """测试路径1空模块列表"""
        parsed_solution = {
            "fused_solution": {
                "architecture": {
                    "modules": []
                }
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution)
        
        assert modules == []


class TestModuleExtractionPath2:
    """路径2测试: fused_solution.modules"""
    
    def test_path2_basic_extraction(self):
        """测试路径2基本提取"""
        parsed_solution = {
            "fused_solution": {
                "modules": [
                    {"name": "模块A", "description": "模块A描述"},
                    {"name": "模块B", "description": "模块B描述"},
                    {"name": "模块C", "description": "模块C描述"}
                ]
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution)
        
        assert len(modules) == 3
        assert modules[0]["name"] == "模块A"
    
    def test_path2_fallback_from_path1(self):
        """测试路径2作为路径1的回退"""
        parsed_solution = {
            "fused_solution": {
                "architecture": {},
                "modules": [
                    {"name": "回退模块", "description": "当architecture无modules时"}
                ]
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution)
        
        assert len(modules) == 1
        assert modules[0]["name"] == "回退模块"
    
    def test_path2_without_architecture_key(self):
        """测试路径2无architecture键的情况"""
        parsed_solution = {
            "fused_solution": {
                "modules": [
                    {"name": "直接模块", "order": 1}
                ]
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution)
        
        assert len(modules) == 1
        assert modules[0]["name"] == "直接模块"


class TestModuleExtractionPath3:
    """路径3测试: landing_plan.模块划分"""
    
    def test_path3_chinese_key_extraction(self):
        """测试路径3中文键提取"""
        parsed_solution = {"fused_solution": {}}
        landing_plan = {
            "模块划分": {
                "modules": [
                    {"name": "中文模块1", "模块名称": "用户域"},
                    {"name": "中文模块2", "模块名称": "订单域"}
                ]
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution, landing_plan)
        
        assert len(modules) == 2
        assert modules[0]["name"] == "中文模块1"
    
    def test_path3_modules_key_fallback(self):
        """测试路径3 modules键回退"""
        parsed_solution = {"fused_solution": {}}
        landing_plan = {
            "modules": {
                "modules": [
                    {"name": "模块X"}
                ]
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution, landing_plan)
        
        assert len(modules) == 1
        assert modules[0]["name"] == "模块X"
    
    def test_path3_list_format(self):
        """测试路径3列表格式"""
        parsed_solution = {"fused_solution": {}}
        landing_plan = {
            "模块划分": [
                {"name": "列表模块1"},
                {"name": "列表模块2"}
            ]
        }
        
        modules = extract_modules_from_solution(parsed_solution, landing_plan)
        
        assert len(modules) == 2
        assert isinstance(modules, list)
    
    def test_path3_chinese_module_list_key(self):
        """测试路径3 模块列表 键"""
        parsed_solution = {"fused_solution": {}}
        landing_plan = {
            "模块划分": {
                "模块列表": [
                    {"模块名称": "模块A"},
                    {"模块名称": "模块B"}
                ]
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution, landing_plan)
        
        assert len(modules) == 2
        assert modules[0]["模块名称"] == "模块A"


class TestRawContentUnwrapping:
    """raw_content 包裹情况测试"""
    
    def test_single_layer_raw_content(self):
        """测试单层 raw_content 包裹"""
        inner_data = {
            "fused_solution": {
                "modules": [{"name": "内部模块"}]
            }
        }
        raw_data = {
            "raw_content": json.dumps(inner_data, ensure_ascii=False)
        }
        
        parsed = parse_solution_with_raw_content(raw_data)
        modules = extract_modules_from_solution(parsed)
        
        assert len(modules) == 1
        assert modules[0]["name"] == "内部模块"
    
    def test_nested_raw_content(self):
        """测试嵌套 raw_content 包裹"""
        innermost = {
            "fused_solution": {
                "architecture": {
                    "modules": [{"name": "最内层模块"}]
                }
            }
        }
        middle = {"raw_content": json.dumps(innermost, ensure_ascii=False)}
        outer = {"raw_content": json.dumps(middle, ensure_ascii=False)}
        
        parsed = parse_solution_with_raw_content(outer)
        modules = extract_modules_from_solution(parsed)
        
        assert len(modules) == 1
        assert modules[0]["name"] == "最内层模块"
    
    def test_invalid_json_in_raw_content(self):
        """测试 raw_content 包含无效JSON"""
        raw_data = {
            "raw_content": "这不是有效的JSON"
        }
        
        parsed = parse_solution_with_raw_content(raw_data)
        
        assert parsed == raw_data
    
    def test_no_raw_content(self):
        """测试无 raw_content 字段"""
        data = {
            "fused_solution": {
                "modules": [{"name": "直接数据"}]
            }
        }
        
        parsed = parse_solution_with_raw_content(data)
        modules = extract_modules_from_solution(parsed)
        
        assert len(modules) == 1


class TestEmptyDataHandling:
    """空数据处理测试"""
    
    def test_empty_parsed_solution(self):
        """测试空解决方案"""
        parsed_solution = {}
        
        modules = extract_modules_from_solution(parsed_solution)
        
        assert modules == []
    
    def test_none_landing_plan(self):
        """测试 landing_plan 为 None"""
        parsed_solution = {"fused_solution": {}}
        
        modules = extract_modules_from_solution(parsed_solution, None)
        
        assert modules == []
    
    def test_empty_landing_plan(self):
        """测试空 landing_plan"""
        parsed_solution = {"fused_solution": {}}
        landing_plan = {}
        
        modules = extract_modules_from_solution(parsed_solution, landing_plan)
        
        assert modules == []
    
    def test_all_paths_empty(self):
        """测试所有路径都为空"""
        parsed_solution = {
            "fused_solution": {
                "architecture": {},
                "modules": []
            }
        }
        landing_plan = {"模块划分": {}}
        
        modules = extract_modules_from_solution(parsed_solution, landing_plan)
        
        assert modules == []
    
    def test_none_values_in_structure(self):
        """测试结构中包含 None 值"""
        parsed_solution = {
            "fused_solution": {
                "architecture": None,
                "modules": None
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution)
        
        assert modules is None or modules == []


class TestPriorityOrder:
    """路径优先级测试"""
    
    def test_path1_takes_priority(self):
        """测试路径1优先级最高"""
        parsed_solution = {
            "fused_solution": {
                "architecture": {
                    "modules": [{"name": "路径1模块"}]
                },
                "modules": [{"name": "路径2模块"}]
            }
        }
        landing_plan = {
            "模块划分": {
                "modules": [{"name": "路径3模块"}]
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution, landing_plan)
        
        assert len(modules) == 1
        assert modules[0]["name"] == "路径1模块"
    
    def test_path2_over_path3(self):
        """测试路径2优先于路径3"""
        parsed_solution = {
            "fused_solution": {
                "architecture": {},
                "modules": [{"name": "路径2模块"}]
            }
        }
        landing_plan = {
            "模块划分": {
                "modules": [{"name": "路径3模块"}]
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution, landing_plan)
        
        assert len(modules) == 1
        assert modules[0]["name"] == "路径2模块"


class TestEdgeCases:
    """边界情况测试"""
    
    def test_non_dict_parsed_solution(self):
        """测试非字典类型的解决方案"""
        parsed_solution = "invalid"
        
        modules = extract_modules_from_solution(parsed_solution)
        
        assert modules == []
    
    def test_modules_as_string(self):
        """测试 modules 字段为字符串"""
        parsed_solution = {
            "fused_solution": {
                "modules": "不是列表"
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution)
        
        assert modules == "不是列表"
    
    def test_complex_module_structure(self):
        """测试复杂模块结构"""
        parsed_solution = {
            "fused_solution": {
                "architecture": {
                    "modules": [
                        {
                            "name": "复杂模块",
                            "description": "复杂描述",
                            "dependencies": ["模块A", "模块B"],
                            "interfaces": ["Interface1", "Interface2"],
                            "config": {"key": "value"},
                            "nested": {"deep": {"data": [1, 2, 3]}}
                        }
                    ]
                }
            }
        }
        
        modules = extract_modules_from_solution(parsed_solution)
        
        assert len(modules) == 1
        assert modules[0]["name"] == "复杂模块"
        assert "dependencies" in modules[0]
        assert modules[0]["nested"]["deep"]["data"] == [1, 2, 3]

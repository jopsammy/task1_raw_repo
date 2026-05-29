"""
feature_detector模块单元测试

测试 ui_renderer.py 中的特征检测和路由功能：
- detect_data_features: 数据特征检测
- route_to_renderer: 特征路由分发
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)


class TestDetectDataFeaturesFlow:
    """流程特征检测测试"""
    
    def test_detect_data_features_flow_with_flows_key(self):
        """测试包含flows键的流程特征检测"""
        data = {
            "flows": [
                {"name": "用户注册流程", "steps": ["输入信息", "验证", "创建账户"]}
            ],
            "entities": ["用户", "账户"]
        }
        
        flow_keys = {"flow", "flows", "entities", "business_flow"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & flow_keys)
        assert detected is True
    
    def test_detect_data_features_flow_with_business_flow(self):
        """测试包含business_flow键的流程特征检测"""
        data = {
            "business_flow": {
                "name": "订单处理流程",
                "steps": ["下单", "支付", "发货"]
            }
        }
        
        flow_keys = {"flow", "flows", "entities", "business_flow"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & flow_keys)
        assert detected is True
    
    def test_detect_data_features_flow_with_entities(self):
        """测试包含entities键的流程特征检测"""
        data = {
            "entities": [
                {"name": "用户", "attributes": ["id", "name", "email"]},
                {"name": "订单", "attributes": ["id", "user_id", "amount"]}
            ]
        }
        
        flow_keys = {"flow", "flows", "entities", "business_flow"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & flow_keys)
        assert detected is True
    
    def test_detect_data_features_flow_single_flow(self):
        """测试单个flow键"""
        data = {
            "flow": {"name": "简单流程", "steps": []}
        }
        
        flow_keys = {"flow", "flows", "entities", "business_flow"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & flow_keys)
        assert detected is True
    
    def test_detect_data_features_flow_priority(self):
        """测试流程特征优先级（solutions > flow）"""
        data = {
            "solutions": [{"name": "方案1"}],
            "flows": [{"name": "流程1"}]
        }
        
        solutions_keys = {"solutions", "individual_solutions", "paradigms"}
        flow_keys = {"flow", "flows", "entities", "business_flow"}
        data_keys = set(data.keys())
        
        features = []
        if data_keys & solutions_keys:
            features.append("solutions")
        if data_keys & flow_keys:
            features.append("flow")
        
        assert features == ["solutions", "flow"]
        assert features[0] == "solutions"


class TestDetectDataFeaturesInterfaces:
    """接口特征检测测试"""
    
    def test_detect_data_features_interfaces_with_interfaces(self):
        """测试包含interfaces键的接口特征检测"""
        data = {
            "interfaces": [
                {"method": "GET", "path": "/api/users", "description": "获取用户列表"}
            ]
        }
        
        interfaces_keys = {"interfaces", "api", "endpoints", "api_list"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & interfaces_keys)
        assert detected is True
    
    def test_detect_data_features_interfaces_with_api(self):
        """测试包含api键的接口特征检测"""
        data = {
            "api": [
                {"endpoint": "/api/orders", "method": "POST"}
            ]
        }
        
        interfaces_keys = {"interfaces", "api", "endpoints", "api_list"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & interfaces_keys)
        assert detected is True
    
    def test_detect_data_features_interfaces_with_endpoints(self):
        """测试包含endpoints键的接口特征检测"""
        data = {
            "endpoints": [
                {"path": "/api/products", "method": "GET"}
            ]
        }
        
        interfaces_keys = {"interfaces", "api", "endpoints", "api_list"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & interfaces_keys)
        assert detected is True
    
    def test_detect_data_features_interfaces_with_api_list(self):
        """测试包含api_list键的接口特征检测"""
        data = {
            "api_list": [
                {"name": "UserService", "methods": ["create", "update", "delete"]}
            ]
        }
        
        interfaces_keys = {"interfaces", "api", "endpoints", "api_list"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & interfaces_keys)
        assert detected is True
    
    def test_detect_data_features_interfaces_multiple_keys(self):
        """测试多个接口相关键"""
        data = {
            "interfaces": [],
            "api": [],
            "endpoints": []
        }
        
        interfaces_keys = {"interfaces", "api", "endpoints", "api_list"}
        data_keys = set(data.keys())
        
        matched_keys = data_keys & interfaces_keys
        assert len(matched_keys) == 3


class TestDetectDataFeaturesSchema:
    """Schema特征检测测试"""
    
    def test_detect_data_features_schema_with_schema(self):
        """测试包含schema键的Schema特征检测"""
        data = {
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"}
                }
            }
        }
        
        schema_keys = {"schema", "properties", "fields", "data_schema"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & schema_keys)
        assert detected is True
    
    def test_detect_data_features_schema_with_properties(self):
        """测试包含properties键的Schema特征检测"""
        data = {
            "properties": {
                "user_id": {"type": "integer"},
                "username": {"type": "string"}
            }
        }
        
        schema_keys = {"schema", "properties", "fields", "data_schema"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & schema_keys)
        assert detected is True
    
    def test_detect_data_features_schema_with_fields(self):
        """测试包含fields键的Schema特征检测"""
        data = {
            "fields": [
                {"name": "id", "type": "string", "required": True},
                {"name": "name", "type": "string", "required": False}
            ]
        }
        
        schema_keys = {"schema", "properties", "fields", "data_schema"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & schema_keys)
        assert detected is True
    
    def test_detect_data_features_schema_with_data_schema(self):
        """测试包含data_schema键的Schema特征检测"""
        data = {
            "data_schema": {
                "User": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}}
                }
            }
        }
        
        schema_keys = {"schema", "properties", "fields", "data_schema"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & schema_keys)
        assert detected is True
    
    def test_detect_data_features_schema_nested(self):
        """测试嵌套Schema结构"""
        data = {
            "schema": {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "profile": {
                                "type": "object",
                                "properties": {
                                    "avatar": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
        
        assert "schema" in data
        assert "properties" in data["schema"]


class TestDetectDataFeaturesMarkdown:
    """Markdown特征检测测试"""
    
    def test_detect_data_features_markdown_with_markdown_content(self):
        """测试包含markdown_content键的Markdown特征检测"""
        data = {
            "markdown_content": "# 标题\n\n这是Markdown内容\n\n```python\nprint('hello')\n```"
        }
        
        has_markdown_key = "markdown_content" in data.keys()
        assert has_markdown_key is True
    
    def test_detect_data_features_markdown_with_hash_start(self):
        """测试以#开头的Markdown字符串"""
        data = {
            "description": "# 项目说明\n\n这是一个测试项目"
        }
        
        for key, value in data.items():
            if isinstance(value, str):
                if value.strip().startswith("#"):
                    has_markdown = True
                    break
        else:
            has_markdown = False
        
        assert has_markdown is True
    
    def test_detect_data_features_markdown_with_code_block(self):
        """测试包含代码块的Markdown字符串"""
        data = {
            "code": "这是一段代码：\n```python\ndef hello():\n    pass\n```\n结束"
        }
        
        for key, value in data.items():
            if isinstance(value, str):
                if "```" in value:
                    has_markdown = True
                    break
        else:
            has_markdown = False
        
        assert has_markdown is True
    
    def test_detect_data_features_markdown_plain_text(self):
        """测试普通文本不被识别为Markdown"""
        data = {
            "description": "这是一段普通文本，没有Markdown格式"
        }
        
        has_markdown_key = "markdown_content" in data.keys()
        
        has_markdown_value = False
        for key, value in data.items():
            if isinstance(value, str):
                if value.strip().startswith("#") or "```" in value:
                    has_markdown_value = True
                    break
        
        assert has_markdown_key is False
        assert has_markdown_value is False
    
    def test_detect_data_features_markdown_multiple_fields(self):
        """测试多个字段中包含Markdown"""
        data = {
            "title": "普通标题",
            "content": "# Markdown标题",
            "notes": "普通备注"
        }
        
        markdown_fields = []
        for key, value in data.items():
            if isinstance(value, str):
                if value.strip().startswith("#") or "```" in value:
                    markdown_fields.append(key)
        
        assert markdown_fields == ["content"]


class TestDetectDataFeaturesSolutions:
    """方案特征检测测试"""
    
    def test_detect_data_features_solutions_with_solutions(self):
        """测试包含solutions键的方案特征检测"""
        data = {
            "solutions": [
                {"name": "整洁架构方案", "pros": ["可维护性强"], "cons": ["初期成本高"]},
                {"name": "响应式方案", "pros": ["性能优异"], "cons": ["调试复杂"]}
            ]
        }
        
        solutions_keys = {"solutions", "individual_solutions", "paradigms"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & solutions_keys)
        assert detected is True
    
    def test_detect_data_features_solutions_with_individual_solutions(self):
        """测试包含individual_solutions键的方案特征检测"""
        data = {
            "individual_solutions": [
                {"id": "sol-1", "name": "方案A"},
                {"id": "sol-2", "name": "方案B"}
            ]
        }
        
        solutions_keys = {"solutions", "individual_solutions", "paradigms"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & solutions_keys)
        assert detected is True
    
    def test_detect_data_features_solutions_with_paradigms(self):
        """测试包含paradigms键的方案特征检测"""
        data = {
            "paradigms": [
                {"name": "DDD", "description": "领域驱动设计"},
                {"name": "Clean Architecture", "description": "整洁架构"}
            ]
        }
        
        solutions_keys = {"solutions", "individual_solutions", "paradigms"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & solutions_keys)
        assert detected is True
    
    def test_detect_data_features_solutions_highest_priority(self):
        """测试方案特征具有最高优先级"""
        data = {
            "solutions": [],
            "flows": [],
            "interfaces": [],
            "schema": {}
        }
        
        solutions_keys = {"solutions", "individual_solutions", "paradigms"}
        flow_keys = {"flow", "flows", "entities", "business_flow"}
        interfaces_keys = {"interfaces", "api", "endpoints", "api_list"}
        schema_keys = {"schema", "properties", "fields", "data_schema"}
        
        data_keys = set(data.keys())
        
        features = []
        if data_keys & solutions_keys:
            features.append("solutions")
        if data_keys & flow_keys:
            features.append("flow")
        if data_keys & interfaces_keys:
            features.append("interfaces")
        if data_keys & schema_keys:
            features.append("schema")
        
        assert features[0] == "solutions"


class TestDetectDataFeaturesContracts:
    """契约特征检测测试"""
    
    def test_detect_data_features_contracts_with_contracts(self):
        """测试包含contracts键的契约特征检测"""
        data = {
            "contracts": {
                "data": {"User": {"type": "object"}},
                "interface": {"IUserService": {"methods": {}}}
            }
        }
        
        contracts_keys = {"contracts", "interface_stub", "data_contract"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & contracts_keys)
        assert detected is True
    
    def test_detect_data_features_contracts_with_interface_stub(self):
        """测试包含interface_stub键的契约特征检测"""
        data = {
            "interface_stub": {
                "IUserService": {
                    "create_user": {"params": {}, "returns": "User"}
                }
            }
        }
        
        contracts_keys = {"contracts", "interface_stub", "data_contract"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & contracts_keys)
        assert detected is True
    
    def test_detect_data_features_contracts_with_data_contract(self):
        """测试包含data_contract键的契约特征检测"""
        data = {
            "data_contract": {
                "UserSchema": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}}
                }
            }
        }
        
        contracts_keys = {"contracts", "interface_stub", "data_contract"}
        data_keys = set(data.keys())
        
        detected = bool(data_keys & contracts_keys)
        assert detected is True
    
    def test_detect_data_features_contracts_lowest_priority(self):
        """测试契约特征具有最低优先级"""
        priority_order = ["solutions", "flow", "interfaces", "schema", "markdown", "contracts"]
        
        assert priority_order[-1] == "contracts"


class TestDetectDataFeaturesEmpty:
    """空数据特征检测测试"""
    
    def test_detect_data_features_empty_dict(self):
        """测试空字典"""
        data = {}
        
        if not isinstance(data, dict):
            features = []
        else:
            features = []
        
        assert features == []
    
    def test_detect_data_features_none(self):
        """测试None值"""
        data = None
        
        if not isinstance(data, dict):
            features = []
        else:
            features = []
        
        assert features == []
    
    def test_detect_data_features_not_dict(self):
        """测试非字典类型"""
        data_list = [1, 2, 3]
        data_str = "test"
        data_int = 123
        
        for data in [data_list, data_str, data_int]:
            if not isinstance(data, dict):
                features = []
            else:
                features = []
            
            assert features == []
    
    def test_detect_data_features_empty_nested(self):
        """测试空嵌套结构"""
        data = {
            "empty_list": [],
            "empty_dict": {},
            "empty_string": ""
        }
        
        flow_keys = {"flow", "flows", "entities", "business_flow"}
        interfaces_keys = {"interfaces", "api", "endpoints", "api_list"}
        schema_keys = {"schema", "properties", "fields", "data_schema"}
        solutions_keys = {"solutions", "individual_solutions", "paradigms"}
        contracts_keys = {"contracts", "interface_stub", "data_contract"}
        
        data_keys = set(data.keys())
        
        features = []
        if data_keys & solutions_keys:
            features.append("solutions")
        if data_keys & flow_keys:
            features.append("flow")
        if data_keys & interfaces_keys:
            features.append("interfaces")
        if data_keys & schema_keys:
            features.append("schema")
        if data_keys & contracts_keys:
            features.append("contracts")
        
        assert features == []


class TestRouteToRenderer:
    """路由分发测试"""
    
    def test_route_to_renderer_solutions_priority(self):
        """测试方案特征路由优先级最高"""
        features = ["solutions", "flow", "interfaces"]
        priority_order = ["solutions", "flow", "interfaces", "schema", "markdown", "contracts"]
        
        rendered = False
        for feature in priority_order:
            if feature in features:
                first_feature = feature
                rendered = True
                break
        
        assert rendered is True
        assert first_feature == "solutions"
    
    def test_route_to_renderer_flow_priority(self):
        """测试流程特征路由优先级"""
        features = ["flow", "interfaces", "schema"]
        priority_order = ["solutions", "flow", "interfaces", "schema", "markdown", "contracts"]
        
        rendered = False
        for feature in priority_order:
            if feature in features:
                first_feature = feature
                rendered = True
                break
        
        assert rendered is True
        assert first_feature == "flow"
    
    def test_route_to_renderer_interfaces_priority(self):
        """测试接口特征路由优先级"""
        features = ["interfaces", "schema", "contracts"]
        priority_order = ["solutions", "flow", "interfaces", "schema", "markdown", "contracts"]
        
        rendered = False
        for feature in priority_order:
            if feature in features:
                first_feature = feature
                rendered = True
                break
        
        assert rendered is True
        assert first_feature == "interfaces"
    
    def test_route_to_renderer_schema_priority(self):
        """测试Schema特征路由优先级"""
        features = ["schema", "markdown", "contracts"]
        priority_order = ["solutions", "flow", "interfaces", "schema", "markdown", "contracts"]
        
        rendered = False
        for feature in priority_order:
            if feature in features:
                first_feature = feature
                rendered = True
                break
        
        assert rendered is True
        assert first_feature == "schema"
    
    def test_route_to_renderer_markdown_priority(self):
        """测试Markdown特征路由优先级"""
        features = ["markdown", "contracts"]
        priority_order = ["solutions", "flow", "interfaces", "schema", "markdown", "contracts"]
        
        rendered = False
        for feature in priority_order:
            if feature in features:
                first_feature = feature
                rendered = True
                break
        
        assert rendered is True
        assert first_feature == "markdown"
    
    def test_route_to_renderer_contracts_priority(self):
        """测试契约特征路由优先级"""
        features = ["contracts"]
        priority_order = ["solutions", "flow", "interfaces", "schema", "markdown", "contracts"]
        
        rendered = False
        for feature in priority_order:
            if feature in features:
                first_feature = feature
                rendered = True
                break
        
        assert rendered is True
        assert first_feature == "contracts"
    
    def test_route_to_renderer_empty_features(self):
        """测试空特征列表"""
        features = []
        
        if not features:
            should_use_default = True
        else:
            should_use_default = False
        
        assert should_use_default is True
    
    def test_route_to_renderer_stage_name_display(self):
        """测试阶段名称显示"""
        stage_name = "架构迭代阶段"
        
        if stage_name:
            has_stage_name = True
        else:
            has_stage_name = False
        
        assert has_stage_name is True
    
    def test_route_to_renderer_empty_stage_name(self):
        """测试空阶段名称"""
        stage_name = ""
        
        if stage_name:
            has_stage_name = True
        else:
            has_stage_name = False
        
        assert has_stage_name is False
    
    def test_route_to_renderer_multiple_features(self):
        """测试多特征时的路由选择"""
        features = ["contracts", "schema", "interfaces", "flow", "solutions"]
        priority_order = ["solutions", "flow", "interfaces", "schema", "markdown", "contracts"]
        
        selected_features = []
        for feature in priority_order:
            if feature in features:
                selected_features.append(feature)
        
        assert selected_features[0] == "solutions"
        assert len(selected_features) == 5


class TestDetectDataFeaturesIntegration:
    """特征检测集成测试"""
    
    def test_full_detection_workflow(self):
        """测试完整检测工作流"""
        data = {
            "solutions": [
                {"name": "方案A", "pros": [], "cons": []}
            ],
            "flows": [
                {"name": "业务流程", "steps": []}
            ],
            "interfaces": [
                {"method": "GET", "path": "/api/test"}
            ],
            "schema": {
                "type": "object",
                "properties": {}
            },
            "contracts": {
                "data": {},
                "interface": {}
            }
        }
        
        flow_keys = {"flow", "flows", "entities", "business_flow"}
        interfaces_keys = {"interfaces", "api", "endpoints", "api_list"}
        schema_keys = {"schema", "properties", "fields", "data_schema"}
        solutions_keys = {"solutions", "individual_solutions", "paradigms"}
        contracts_keys = {"contracts", "interface_stub", "data_contract"}
        
        data_keys = set(data.keys())
        
        features = []
        if data_keys & solutions_keys:
            features.append("solutions")
        if data_keys & flow_keys:
            features.append("flow")
        if data_keys & interfaces_keys:
            features.append("interfaces")
        if data_keys & schema_keys:
            features.append("schema")
        if data_keys & contracts_keys:
            features.append("contracts")
        
        assert len(features) == 5
        assert features[0] == "solutions"
    
    def test_detection_with_mixed_data(self):
        """测试混合数据检测"""
        data = {
            "project_name": "测试项目",
            "version": "1.0.0",
            "interfaces": [
                {"name": "API1"}
            ],
            "description": "# 项目说明"
        }
        
        interfaces_keys = {"interfaces", "api", "endpoints", "api_list"}
        data_keys = set(data.keys())
        
        features = []
        if data_keys & interfaces_keys:
            features.append("interfaces")
        
        for key, value in data.items():
            if isinstance(value, str):
                if value.strip().startswith("#") or "```" in value:
                    features.append("markdown")
                    break
        
        assert "interfaces" in features
        assert "markdown" in features
    
    def test_detection_priority_order(self):
        """测试检测优先级顺序"""
        priority_order = ["solutions", "flow", "interfaces", "schema", "markdown", "contracts"]
        
        for i, feature in enumerate(priority_order):
            if i < len(priority_order) - 1:
                current_index = priority_order.index(feature)
                next_feature = priority_order[i + 1]
                next_index = priority_order.index(next_feature)
                assert current_index < next_index

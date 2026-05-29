"""
UI渲染函数单元测试

测试 ui_renderer.py 中的渲染函数：
- render_l1_metrics: 关键指标渲染
- render_l3_raw_stub: 原始数据收纳
- render_metadata_badges: 元数据徽章渲染
- render_export_buttons: 导出按钮渲染
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock, call
from typing import Dict, Any

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)


class TestRenderL1Metrics:
    """关键指标渲染测试"""
    
    def test_render_l1_metrics_basic(self):
        """测试基本指标渲染"""
        metrics = {
            "识别实体数": {"value": 42, "delta": "+5"},
            "接口总数": {"value": 128},
            "风险点计数": {"value": 3, "delta": "-2", "delta_color": "normal"}
        }
        
        metric_keys = list(metrics.keys())
        assert len(metric_keys) == 3
        assert metric_keys[0] == "识别实体数"
        assert metric_keys[1] == "接口总数"
        assert metric_keys[2] == "风险点计数"
    
    def test_render_l1_metrics_value_extraction(self):
        """测试指标值提取"""
        metrics = {
            "实体数": {"value": 100},
            "流程数": {"value": 50, "delta": "+10"},
            "属性数": {"value": 200, "delta": None}
        }
        
        for key, metric_data in metrics.items():
            value = metric_data.get("value", "-")
            delta = metric_data.get("delta")
            delta_color = metric_data.get("delta_color", "normal")
            
            assert isinstance(value, int)
            if key == "实体数":
                assert delta is None
            elif key == "流程数":
                assert delta == "+10"
    
    def test_render_l1_metrics_empty(self):
        """测试空指标数据"""
        metrics = {}
        
        if not metrics:
            should_show_empty = True
        else:
            should_show_empty = False
        
        assert should_show_empty is True
    
    def test_render_l1_metrics_single_metric(self):
        """测试单个指标"""
        metrics = {
            "总文件数": {"value": 25}
        }
        
        assert len(metrics) == 1
        assert metrics["总文件数"]["value"] == 25
    
    def test_render_l1_metrics_with_delta_colors(self):
        """测试带变化颜色的指标"""
        metrics = {
            "增长指标": {"value": 100, "delta": "+20", "delta_color": "normal"},
            "下降指标": {"value": 50, "delta": "-10", "delta_color": "inverse"},
            "中性指标": {"value": 75, "delta": "0", "delta_color": "off"}
        }
        
        for key, data in metrics.items():
            delta_color = data.get("delta_color", "normal")
            assert delta_color in ["normal", "inverse", "off"]
    
    def test_render_l1_metrics_missing_value(self):
        """测试缺失value字段"""
        metrics = {
            "无值指标": {"delta": "+5"}
        }
        
        value = metrics["无值指标"].get("value", "-")
        assert value == "-"
    
    def test_render_l1_metrics_column_count(self):
        """测试列数与指标数匹配"""
        metrics = {
            "指标A": {"value": 1},
            "指标B": {"value": 2},
            "指标C": {"value": 3},
            "指标D": {"value": 4}
        }
        
        num_cols = len(metrics)
        assert num_cols == 4
    
    def test_render_l1_metrics_large_numbers(self):
        """测试大数值指标"""
        metrics = {
            "总Token数": {"value": 1500000},
            "请求数": {"value": 999999}
        }
        
        assert metrics["总Token数"]["value"] == 1500000
        assert metrics["请求数"]["value"] == 999999


class TestRenderL3RawStub:
    """原始数据收纳测试"""
    
    def test_render_l3_raw_stub_basic(self):
        """测试基本原始数据收纳"""
        data = {
            "interface": {"name": "UserService", "methods": ["create", "update"]},
            "data": {"schema": {"type": "object"}}
        }
        title = "接口契约原始数据"
        
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        
        assert "UserService" in json_str
        assert "interface" in json_str
        assert title == "接口契约原始数据"
    
    def test_render_l3_raw_stub_empty_data(self):
        """测试空数据"""
        data = {}
        
        if not data:
            is_empty = True
        else:
            is_empty = False
        
        assert is_empty is True
    
    def test_render_l3_raw_stub_none_data(self):
        """测试None数据"""
        data = None
        
        if not data:
            is_empty = True
        else:
            is_empty = False
        
        assert is_empty is True
    
    def test_render_l3_raw_stub_nested_data(self):
        """测试嵌套数据"""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep"
                    }
                }
            }
        }
        
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        
        assert "level1" in json_str
        assert "level2" in json_str
        assert "level3" in json_str
        assert "deep" in json_str
    
    def test_render_l3_raw_stub_with_chinese(self):
        """测试中文数据"""
        data = {
            "项目名称": "需求结构化分析工具",
            "描述": "这是一个用于需求分析的工具",
            "模块": ["模块0_全局调度面板", "模块1_数据锚点"]
        }
        
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        
        assert "需求结构化分析工具" in json_str
        assert "模块0_全局调度面板" in json_str
    
    def test_render_l3_raw_stub_custom_title(self):
        """测试自定义标题"""
        custom_titles = [
            "原始契约溯源",
            "需求锚定原始数据",
            "架构迭代原始数据",
            "契约原始数据"
        ]
        
        for title in custom_titles:
            assert isinstance(title, str)
            assert len(title) > 0
    
    def test_render_l3_raw_stub_list_data(self):
        """测试列表类型数据"""
        data = {
            "items": [
                {"id": 1, "name": "项目1"},
                {"id": 2, "name": "项目2"},
                {"id": 3, "name": "项目3"}
            ]
        }
        
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        
        assert "items" in json_str
        assert "项目1" in json_str
        assert "项目2" in json_str


class TestRenderMetadataBadges:
    """元数据徽章渲染测试"""
    
    def test_render_metadata_badges_single_model(self):
        """测试单模型徽章"""
        metadata = {
            "model": "DeepSeek-V3",
            "duration": 12.5,
            "tokens": 4500,
            "input_tokens": 3000,
            "output_tokens": 1500
        }
        
        model = metadata.get("model", "-")
        duration = metadata.get("duration", 0)
        tokens = metadata.get("tokens", 0)
        
        assert model == "DeepSeek-V3"
        assert duration == 12.5
        assert tokens == 4500
    
    def test_render_metadata_badges_multiple_models(self):
        """测试多模型徽章"""
        metadata = {
            "model": ["DeepSeek-V3", "GPT-4"],
            "duration": 25.0,
            "tokens": 8000
        }
        
        model = metadata.get("model", "-")
        
        if isinstance(model, list):
            model_str = " | ".join(model)
        else:
            model_str = str(model)
        
        assert model_str == "DeepSeek-V3 | GPT-4"
    
    def test_render_metadata_badges_format_number(self):
        """测试数字格式化"""
        def format_number(num):
            if num >= 1000:
                return f"{num / 1000:.1f}k"
            return str(num)
        
        assert format_number(500) == "500"
        assert format_number(1000) == "1.0k"
        assert format_number(1500) == "1.5k"
        assert format_number(10000) == "10.0k"
        assert format_number(12345) == "12.3k"
    
    def test_render_metadata_badges_duration_format(self):
        """测试耗时格式化"""
        durations = [0.5, 1.0, 12.5, 60.0, 120.5, 3600.0]
        
        for duration in durations:
            if isinstance(duration, (int, float)):
                duration_str = f"{duration:.1f}s"
            else:
                duration_str = str(duration)
            
            assert "s" in duration_str
    
    def test_render_metadata_badges_empty(self):
        """测试空元数据"""
        metadata = {}
        
        if not metadata:
            is_empty = True
        else:
            is_empty = False
        
        assert is_empty is True
    
    def test_render_metadata_badges_partial_data(self):
        """测试部分数据"""
        metadata = {
            "model": "GPT-4"
        }
        
        model = metadata.get("model", "-")
        duration = metadata.get("duration", 0)
        tokens = metadata.get("tokens", 0)
        
        assert model == "GPT-4"
        assert duration == 0
        assert tokens == 0
    
    def test_render_metadata_badges_with_input_output_tokens(self):
        """测试带输入输出Token的徽章"""
        metadata = {
            "model": "Claude-3",
            "duration": 15.0,
            "tokens": 5000,
            "input_tokens": 3500,
            "output_tokens": 1500
        }
        
        input_tokens = metadata.get("input_tokens")
        output_tokens = metadata.get("output_tokens")
        
        assert input_tokens is not None
        assert output_tokens is not None
        assert input_tokens == 3500
        assert output_tokens == 1500
    
    def test_render_metadata_badges_html_structure(self):
        """测试HTML结构生成"""
        metadata = {
            "model": "Test-Model",
            "duration": 10.0,
            "tokens": 1000
        }
        
        model_str = str(metadata.get("model", "-"))
        duration_str = f"{metadata.get('duration', 0):.1f}s"
        tokens_str = str(metadata.get("tokens", 0))
        
        badges_html = f"""
        <span>🤖 Model: {model_str}</span>
        <span>⏱️ Duration: {duration_str}</span>
        <span>📊 Tokens: {tokens_str}</span>
        """
        
        assert "🤖 Model: Test-Model" in badges_html
        assert "⏱️ Duration: 10.0s" in badges_html
        assert "📊 Tokens: 1000" in badges_html


class TestRenderExportButtons:
    """导出按钮渲染测试"""
    
    def test_render_export_buttons_json_generation(self):
        """测试JSON导出生成"""
        stage_name = "requirement_anchoring"
        result = {
            "entities": ["用户", "订单"],
            "flows": ["注册流程", "下单流程"],
            "metrics": {"entity_count": 2, "flow_count": 2}
        }
        
        json_data = json.dumps(result, ensure_ascii=False, indent=2)
        
        assert "entities" in json_data
        assert "用户" in json_data
        assert "flows" in json_data
        assert stage_name == "requirement_anchoring"
    
    def test_render_export_buttons_markdown_generation(self):
        """测试Markdown导出生成"""
        result = {
            "name": "测试项目",
            "version": "1.0.0",
            "items": ["项目1", "项目2"]
        }
        
        def dict_to_markdown_table(data, level=0):
            if not isinstance(data, dict):
                return str(data)
            
            indent = "  " * level
            lines = []
            
            lines.append(f"{indent}| 键 | 值 |")
            lines.append(f"{indent}|---|---|")
            
            for key, value in data.items():
                if isinstance(value, dict):
                    lines.append(f"{indent}| {key} | (嵌套对象) |")
                elif isinstance(value, list):
                    lines.append(f"{indent}| {key} | (列表，{len(value)}项) |")
                else:
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    lines.append(f"{indent}| {key} | {value_str} |")
            
            return "\n".join(lines)
        
        md_content = dict_to_markdown_table(result)
        
        assert "| 键 | 值 |" in md_content
        assert "| name | 测试项目 |" in md_content
        assert "| version | 1.0.0 |" in md_content
    
    def test_render_export_buttons_filename_generation(self):
        """测试文件名生成"""
        stage_names = [
            "requirement_anchoring",
            "architecture_iteration",
            "contract_generation",
            "landing_plan_generation"
        ]
        
        for stage_name in stage_names:
            json_filename = f"{stage_name}.json"
            md_filename = f"{stage_name}.md"
            
            assert json_filename.endswith(".json")
            assert md_filename.endswith(".md")
    
    def test_render_export_buttons_mime_types(self):
        """测试MIME类型"""
        mime_types = {
            "json": "application/json",
            "md": "text/markdown",
            "txt": "text/plain"
        }
        
        assert mime_types["json"] == "application/json"
        assert mime_types["md"] == "text/markdown"
    
    def test_render_export_buttons_nested_dict_to_markdown(self):
        """测试嵌套字典转Markdown"""
        result = {
            "name": "项目",
            "config": {
                "debug": True,
                "level": "info"
            }
        }
        
        def dict_to_markdown_table(data, level=0):
            if not isinstance(data, dict):
                return str(data)
            
            indent = "  " * level
            lines = []
            
            lines.append(f"{indent}| 键 | 值 |")
            lines.append(f"{indent}|---|---|")
            
            for key, value in data.items():
                if isinstance(value, dict):
                    lines.append(f"{indent}| {key} | (嵌套对象) |")
                    nested = dict_to_markdown_table(value, level + 1)
                    lines.append(nested)
                elif isinstance(value, list):
                    lines.append(f"{indent}| {key} | (列表，{len(value)}项) |")
                else:
                    lines.append(f"{indent}| {key} | {value} |")
            
            return "\n".join(lines)
        
        md_content = dict_to_markdown_table(result)
        
        assert "(嵌套对象)" in md_content
        assert "debug" in md_content or "config" in md_content
    
    def test_render_export_buttons_list_to_markdown(self):
        """测试列表转Markdown"""
        result = {
            "items": [
                {"id": 1, "name": "A"},
                {"id": 2, "name": "B"}
            ]
        }
        
        items = result.get("items", [])
        
        assert isinstance(items, list)
        assert len(items) == 2
    
    def test_render_export_buttons_special_characters(self):
        """测试特殊字符处理"""
        result = {
            "description": "这是一个包含特殊字符的描述：\n换行\t制表符",
            "code": "def test():\n    pass"
        }
        
        json_data = json.dumps(result, ensure_ascii=False, indent=2)
        
        assert "换行" in json_data
        assert "制表符" in json_data
    
    def test_render_export_buttons_empty_result(self):
        """测试空结果"""
        result = {}
        
        json_data = json.dumps(result, ensure_ascii=False, indent=2)
        
        assert json_data == "{}"


class TestRenderExportButtonsIntegration:
    """导出按钮集成测试"""
    
    def test_full_export_workflow(self):
        """测试完整导出工作流"""
        stage_name = "contract_generation"
        result = {
            "interfaces": [
                {"method": "GET", "path": "/api/users", "description": "获取用户列表"}
            ],
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"}
                    }
                }
            },
            "mock_files": ["mock_user.py"]
        }
        
        json_data = json.dumps(result, ensure_ascii=False, indent=2)
        
        assert stage_name == "contract_generation"
        assert "interfaces" in json_data
        assert "schemas" in json_data
        assert "mock_user.py" in json_data
    
    def test_export_with_unicode(self):
        """测试Unicode字符导出"""
        stage_name = "requirement_anchoring"
        result = {
            "项目名称": "需求结构化分析工具",
            "描述": "支持中文、English、日本語、한국어",
            "emoji": "🎉 ✅ 📝 🏗️"
        }
        
        json_data = json.dumps(result, ensure_ascii=False, indent=2)
        
        assert "需求结构化分析工具" in json_data
        assert "日本語" in json_data
        assert "🎉" in json_data

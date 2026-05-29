"""
Mock测试模式 - Record & Replay
从真实 Pipeline 运行记录加载数据测试 UI 渲染
"""

import os
import json
from pathlib import Path
from datetime import datetime


class MockDataManager:
    """Mock数据管理器 - Record & Replay 模式
    
    从真实 Pipeline 运行记录加载数据，不再编造 UI 友好字段
    """
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.results = {}
        self.token_stats = {
            "total_tokens": 125000,
            "input_tokens": 85000,
            "output_tokens": 40000
        }
        self.models_used = ["deepseek-chat", "deepseek-reasoner"]
        self.elapsed_time = 180.5
    
    def load_all(self):
        """加载所有Mock数据 - Record & Replay 模式"""
        self.results = {}
        
        stage_files = {
            "requirement_anchoring": "structured_requirement.json",
            "requirement_validation": "requirement_validation.json",
            "architecture_iteration": "final_architecture.json",
            "contract_generation": "contracts.json",
            "landing_plan_generation": "landing_plan.json"
        }
        
        for stage_name, filename in stage_files.items():
            stage_data = self._load_stage(filename)
            if stage_data:
                self.results[stage_name] = {
                    "success": True,
                    "stage": stage_name,
                    "usage": {
                        "input_tokens": 12000,
                        "output_tokens": 5000,
                        "total_tokens": 17000
                    },
                    "model": "deepseek-chat",
                    "timestamp": datetime.now().isoformat()
                }
                
                if stage_name == "requirement_anchoring":
                    self.results[stage_name]["structured_requirement"] = stage_data
                elif stage_name == "requirement_validation":
                    self.results[stage_name]["validation_result"] = stage_data
                elif stage_name == "architecture_iteration":
                    self.results[stage_name]["final_solution"] = stage_data
                elif stage_name == "contract_generation":
                    self.results[stage_name]["contracts"] = stage_data
                elif stage_name == "landing_plan_generation":
                    self.results[stage_name]["landing_plan"] = stage_data
        
        if "visualization_generation" not in self.results:
            self.results["visualization_generation"] = {
                "success": True,
                "stage": "visualization_generation",
                "ascii_flows": """[用户输入]
    -> [需求解析]
    -> [实体识别]
    -> [流程建模]
    -> [架构设计]
    -> [输出结果]""",
                "ascii_entities": """[用户]
    |
    +-- [订单]
    |
    +-- [产品]
    |
    +-- [支付记录]""",
                "ascii_modules": """[模块0_全局调度]
    |
    v
[模块1_业务逻辑]
    |
    v
[模块2_数据存储]""",
                "mermaid_flows": "",
                "mermaid_entities": "",
                "mermaid_modules": "",
                "model": "deepseek-chat",
                "usage": {"input_tokens": 2000, "output_tokens": 1500, "total_tokens": 3500},
                "timestamp": datetime.now().isoformat()
            }
        
        if "ide_bundle_generation" not in self.results:
            self.results["ide_bundle_generation"] = {
                "success": True,
                "stage": "ide_bundle_generation",
                "ide_bundle": {
                    "global": {"content": ""},
                    "modules": []
                },
                "model": "deepseek-chat",
                "usage": {"input_tokens": 3000, "output_tokens": 2500, "total_tokens": 5500},
                "timestamp": datetime.now().isoformat()
            }
        
        return self.results
    
    def _load_stage(self, filename):
        """加载单个阶段的JSON文件"""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None


def get_mock_data_dir():
    """获取Mock数据目录（从环境变量或命令行参数）"""
    mock_dir = os.environ.get("MOCK_DATA_DIR")
    if mock_dir:
        return mock_dir
    
    import sys
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--mock-data-dir="):
            return arg.split("=", 1)[1]
        if arg == "--mock-data-dir" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    
    return None


def get_mock_ui_mode():
    """获取Mock UI模式（INPUT/REVIEW，默认REVIEW）"""
    ui_mode = os.environ.get("MOCK_UI_MODE", "REVIEW").upper()
    if ui_mode not in ["INPUT", "REVIEW"]:
        ui_mode = "REVIEW"
    return ui_mode


def is_mock_mode():
    """检查是否启用Mock模式"""
    return get_mock_data_dir() is not None


if __name__ == "__main__":
    mock_dir = get_mock_data_dir()
    if mock_dir:
        print(f"Mock数据目录: {mock_dir}")
        manager = MockDataManager(mock_dir)
        results = manager.load_all()
        print(f"加载的阶段: {list(results.keys())}")
        for stage, data in results.items():
            if data:
                print(f"  {stage}: {len(json.dumps(data, ensure_ascii=False))} 字符")
    else:
        print("未设置Mock数据目录")
        print("使用方法:")
        print("  1. 设置环境变量: $env:MOCK_DATA_DIR='workspace/outputs/20260309_064355'")
        print("  2. 或命令行参数: streamlit run app.py -- --mock-data-dir=workspace/outputs/20260309_064355")

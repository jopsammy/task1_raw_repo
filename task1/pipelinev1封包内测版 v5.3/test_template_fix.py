
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from modules.模块X_提示词工程模块.prompt_engine import get_prompt_engine

print("===== 测试 jinja 模板变量修复 =====")

# 测试数据
test_final_solution = {
    "fused_solution": {
        "architect_style": "边界防腐与高度解耦",
        "tech_stack": {"backend": "Python", "frontend": "Streamlit"},
        "architecture": {
            "modules": [
                {"id": 0, "name": "全局调度模块"},
                {"id": 1, "name": "业务核心模块"}
            ]
        }
    }
}

test_contracts = {
    "interface": {"endpoints": []},
    "data": {"schemas": []}
}

test_structured_requirement = {
    "project_name": "测试项目",
    "features": []
}

test_landing_plan = {
    "steps": []
}

test_agent_md = "# Test Agent MD"

test_module_info = {"id": 0, "name": "测试模块"}

# 初始化 prompt engine
prompt_engine = get_prompt_engine()
print("✅ PromptEngine 初始化成功")

print("\n----- 测试 agent_md_gen.jinja -----")
try:
    result = prompt_engine.generate_prompt(
        "agent_md_gen",
        {
            "final_solution": json.dumps(test_final_solution, ensure_ascii=False, indent=2),
            "contracts": json.dumps(test_contracts, ensure_ascii=False, indent=2)
        }
    )
    print("✅ agent_md_gen.jinja 测试成功")
except Exception as e:
    print(f"❌ agent_md_gen.jinja 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n----- 测试 global_ide_bundle.jinja -----")
try:
    result = prompt_engine.generate_prompt(
        "global_ide_bundle",
        {
            "final_solution": json.dumps(test_final_solution, ensure_ascii=False, indent=2),
            "contracts": json.dumps(test_contracts, ensure_ascii=False, indent=2),
            "agent_md": test_agent_md
        }
    )
    print("✅ global_ide_bundle.jinja 测试成功")
except Exception as e:
    print(f"❌ global_ide_bundle.jinja 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n----- 测试 module_ide_bundle.jinja -----")
try:
    result = prompt_engine.generate_prompt(
        "module_ide_bundle",
        {
            "module_info": json.dumps(test_module_info, ensure_ascii=False, indent=2),
            "final_solution": json.dumps(test_final_solution, ensure_ascii=False, indent=2),
            "contracts": json.dumps(test_contracts, ensure_ascii=False, indent=2),
            "agent_md": test_agent_md
        }
    )
    print("✅ module_ide_bundle.jinja 测试成功")
except Exception as e:
    print(f"❌ module_ide_bundle.jinja 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n===== 所有模板测试完成 =====")

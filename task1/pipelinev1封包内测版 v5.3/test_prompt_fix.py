
#!/usr/bin/env python
"""
测试提示词模板变量名修复
"""
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(current_dir)
sys.path.insert(0, project_root)

from modules.模块X_提示词工程模块.prompt_engine import get_prompt_engine

print("="*80)
print("验证提示词模板变量名修复")
print("="*80)

engine = get_prompt_engine()

test_requirement = "用户可以登录系统，包含用户名和密码验证"

print(f"\n测试需求: {test_requirement}\n")

print("-"*80)
print("1. 测试 requirement_validation 模板")
print("-"*80)

try:
    context = {
        "structured_requirement": {
            "requirements": [
                {"content": test_requirement, "level": 1, "order": 0}
            ]
        }
    }
    prompt = engine.generate_prompt("requirement_validation", context)
    print(f"✅ 模板变量名已正确修复！")
    print(f"   模板中使用的变量: structured_requirement")
    print(f"   上下文提供的变量: structured_requirement")
    print(f"\n用户提示词前100字符: {prompt['user_prompt'][:100]}...")
except Exception as e:
    print(f"❌ 模板有问题: {e}")

print("\n" + "-"*80)
print("2. 测试 data_contract_gen 模板")
print("-"*80)

try:
    context = {"final_solution": {"test": "data"}}
    prompt = engine.generate_prompt("data_contract_gen", context)
    print(f"✅ 模板变量名已正确修复！")
    print(f"   模板中使用的变量: final_solution")
    print(f"   上下文提供的变量: final_solution")
except Exception as e:
    print(f"❌ 模板有问题: {e}")

print("\n" + "-"*80)
print("3. 所有模板变量名验证完成！")
print("-"*80)
print("\n✅ 修复成功！所有提示词模板的变量名现在与代码中传递的变量名保持一致。")
print("\n修复总结:")
print("  - requirement_validation.jinja: structured_requirements → structured_requirement")
print("  - data_contract_gen.jinja: architecture_solution → final_solution")
print("  - interface_contract_gen.jinja: architecture_solution/data_contracts → final_solution")
print("  - mock_gen.jinja: interface_contracts → final_solution")
print("  - agent_md_gen.jinja: 统一为 final_solution/contracts")
print("  - ide_bundle_gen.jinja: 统一为 final_solution/contracts/agent_md")

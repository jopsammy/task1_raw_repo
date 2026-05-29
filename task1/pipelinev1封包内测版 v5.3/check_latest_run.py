
#!/usr/bin/env python
"""
检查最新的运行记录
"""
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(current_dir)
sys.path.insert(0, project_root)

from modules.模块1_数据锚点与存储模块.run_record_manager import get_run_record_manager

print("="*80)
print("检查最新运行记录")
print("="*80)

manager = get_run_record_manager()
runs = manager.list_run_records(limit=5)

if not runs:
    print("暂无运行记录")
    sys.exit(0)

latest_run = runs[0]
print(f"\n最新运行ID: {latest_run['run_id']}")
print(f"状态: {latest_run['status']}")
print(f"开始时间: {latest_run.get('start_time', '-')}")

# 加载完整记录
full_run = manager.load_run_record(latest_run['run_id'])

print("\n" + "-"*80)
print("需求锚定阶段结果：")
print("-"*80)
req_anchor = full_run.get('results', {}).get('requirement_anchoring', {})
print(f"成功: {req_anchor.get('success')}")
structured = req_anchor.get('structured_requirement', {})
print(f"结构化需求前200字符: {str(structured)[:200]}...")

print("\n" + "-"*80)
print("需求校验阶段结果：")
print("-"*80)
req_valid = full_run.get('results', {}).get('requirement_validation', {})
print(f"成功: {req_valid.get('success')}")
valid_result = req_valid.get('validation_result', {})
print(f"校验结果前200字符: {str(valid_result)[:200]}...")

print("\n" + "-"*80)
print("架构迭代阶段最终方案摘要：")
print("-"*80)
arch_iter = full_run.get('results', {}).get('architecture_iteration', {})
final_sol = arch_iter.get('final_solution', {})
fused = final_sol.get('fused_solution', {})
print(f"架构风格: {fused.get('architect_style', '-')}")
print(f"技术栈: {fused.get('tech_stack', {})}")

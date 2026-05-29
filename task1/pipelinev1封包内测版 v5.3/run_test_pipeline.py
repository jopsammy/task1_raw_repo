
#!/usr/bin/env python
"""
测试Pipeline运行
"""
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(current_dir)
sys.path.insert(0, project_root)

from modules.模块0_全局调度面板.pipeline_controller import get_pipeline_controller

print("="*80)
print("测试Pipeline运行")
print("="*80)

controller = get_pipeline_controller()

requirement_text = "用户可以登录系统，包含用户名和密码验证"
project_id = "20260301_361617"

print(f"\n需求文本: {requirement_text}")
print(f"项目ID: {project_id}\n")

print("启动Pipeline...")
result = controller.start_pipeline(requirement_text, project_id)

print("\n" + "="*80)
print("Pipeline执行完成")
print("="*80)

print(f"\n结果: {'成功' if result.get('success') else '失败'}")

if result.get('success'):
    print("\n各阶段结果:")
    results = result.get('results', {})
    for stage, stage_result in results.items():
        status = "✅" if stage_result.get('success') else "❌"
        print(f"  {status} {stage}")
        
    print("\n查看运行记录以了解详情！")
else:
    print(f"错误: {result.get('error')}")

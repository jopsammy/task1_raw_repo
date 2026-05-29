#!/usr/bin/env python
"""
测试路径修复是否正确
"""
import os
import sys

print("="*80)
print("测试路径修复")
print("="*80)

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(current_dir)
sys.path.insert(0, project_root)

print(f"\n当前目录: {current_dir}")
print(f"项目根目录: {project_root}")

print("\n" + "="*80)
print("1. 测试 DataAnchorManager 路径")
print("="*80)

from modules.模块1_数据锚点与存储模块.data_anchor_manager import DataAnchorManager

data_manager = DataAnchorManager()
print(f"DataAnchorManager workspace_dir: {data_manager.workspace_dir}")
print(f"✓ 路径正确: {'v1/v1' not in data_manager.workspace_dir}")

print("\n" + "="*80)
print("2. 测试 RunRecordManager 路径")
print("="*80)

from modules.模块1_数据锚点与存储模块.run_record_manager import RunRecordManager

run_manager = RunRecordManager()
print(f"RunRecordManager workspace_dir: {run_manager.workspace_dir}")
print(f"✓ 路径正确: {'v1/v1' not in run_manager.workspace_dir}")

print("\n" + "="*80)
print("3. 检查目录是否存在")
print("="*80)

v1_v1_path = os.path.join(project_root, "v1")
print(f"v1/v1 路径: {v1_v1_path}")
print(f"v1/v1 存在: {os.path.exists(v1_v1_path)}")

workspace_path = os.path.join(project_root, "workspace")
print(f"workspace 路径: {workspace_path}")
print(f"workspace 存在: {os.path.exists(workspace_path)}")

print("\n" + "="*80)
print("测试完成")
print("="*80)

if 'v1/v1' not in data_manager.workspace_dir and 'v1/v1' not in run_manager.workspace_dir and not os.path.exists(v1_v1_path):
    print("\n✅ 所有测试通过！路径修复成功！")
else:
    print("\n❌ 测试失败，请检查！")

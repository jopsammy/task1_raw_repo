#!/usr/bin/env python3
"""
验证 AGENTS.md 命名改造是否正确的脚本
"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

v1_dir = os.path.join(project_root, 'v1')
sys.path.insert(0, v1_dir)

print("=" * 60)
print("AGENTS.md 命名改造验证")
print("=" * 60)

# 检查 pipeline_orchestrator.py
print("\n1. 检查 pipeline_orchestrator.py...")
pipeline_file = os.path.join(v1_dir, 'modules', '模块2_核心业务引擎模块', 'pipeline_orchestrator.py')
with open(pipeline_file, 'r', encoding='utf-8') as f:
    content = f.read()
    if 'ide_bundles = {' in content and '"agents_md":' in content:
        print("   ✓ ide_bundles key 已更新为 agents_md")
    else:
        print("   ✗ ide_bundles key 未正确更新")
    
    if '"生成AGENTS.md"' in content:
        print("   ✓ 日志文案已更新为 生成AGENTS.md")
    else:
        print("   ✗ 日志文案未正确更新")
    
    if 'agents_md_content' in content:
        print("   ✓ 参数名已更新为 agents_md_content")
    else:
        print("   ✗ 参数名未正确更新")

# 检查 delivery_output_splitter.py
print("\n2. 检查 delivery_output_splitter.py...")
splitter_file = os.path.join(v1_dir, 'modules', '模块5_交付物切分模块', 'delivery_output_splitter.py')
with open(splitter_file, 'r', encoding='utf-8') as f:
    content = f.read()
    if '"agents_md" in ide_bundles:' in content:
        print("   ✓ _save_agent_md 读取 agents_md key")
    else:
        print("   ✗ _save_agent_md 未正确读取 key")
    
    if 'AGENTS.md' in content and 'filepath = os.path.join(outputs_dir, "AGENTS.md")' in content:
        print("   ✓ 文件名已更新为 AGENTS.md")
    else:
        print("   ✗ 文件名未正确更新")
    
    if 'deliveries["AGENTS.md"] = filepath' in content:
        print("   ✓ deliveries key 已更新为 AGENTS.md")
    else:
        print("   ✗ deliveries key 未正确更新")

# 检查提示词模板
print("\n3. 检查提示词模板...")
templates_dir = os.path.join(v1_dir, 'modules', '模块X_提示词工程模块', 'prompts')

global_bundle = os.path.join(templates_dir, 'global_ide_bundle.jinja')
with open(global_bundle, 'r', encoding='utf-8') as f:
    content = f.read()
    if '{{ agents_md }}' in content:
        print("   ✓ global_ide_bundle.jinja 已更新")
    else:
        print("   ✗ global_ide_bundle.jinja 未正确更新")

module_bundle = os.path.join(templates_dir, 'module_ide_bundle.jinja')
with open(module_bundle, 'r', encoding='utf-8') as f:
    content = f.read()
    if '{{ agents_md }}' in content:
        print("   ✓ module_ide_bundle.jinja 已更新")
    else:
        print("   ✗ module_ide_bundle.jinja 未正确更新")

agent_md_gen = os.path.join(templates_dir, 'agent_md_gen.jinja')
with open(agent_md_gen, 'r', encoding='utf-8') as f:
    content = f.read()
    if 'AGENTS规则生成模板' in content:
        print("   ✓ agent_md_gen.jinja 已更新")
    else:
        print("   ✗ agent_md_gen.jinja 未正确更新")

# 检查测试文件
print("\n4. 检查测试文件...")
test_file = os.path.join(v1_dir, 'tests', 'unit', 'test_stage_renderers.py')
with open(test_file, 'r', encoding='utf-8') as f:
    content = f.read()
    if '"name": "AGENTS.md"' in content:
        print("   ✓ test_stage_renderers.py 已更新")
    else:
        print("   ✗ test_stage_renderers.py 未正确更新")

print("\n" + "=" * 60)
print("验证完成！")
print("=" * 60)

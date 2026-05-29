
#!/usr/bin/env python
"""
测试 landing_plan 阶段修复
"""
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(current_dir)
sys.path.insert(0, project_root)

print("="*80)
print("测试 landing_plan 阶段修复")
print("="*80)

# 测试1: 导入检查
print("\n[测试1] 导入检查...")
try:
    from modules.模块2_核心业务引擎模块.pipeline_orchestrator import PipelineStage
    print("✅ PipelineStage 导入成功")
    print(f"   阶段列表: {[s.value for s in PipelineStage]}")
    
    # 检查 LANDING_PLAN_GENERATION 是否存在
    if hasattr(PipelineStage, 'LANDING_PLAN_GENERATION'):
        print(f"✅ LANDING_PLAN_GENERATION 阶段存在: {PipelineStage.LANDING_PLAN_GENERATION.value}")
    else:
        print("❌ LANDING_PLAN_GENERATION 阶段不存在")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 检查 pipeline_orchestrator.py 的方法
print("\n[测试2] 检查 pipeline_orchestrator.py...")
try:
    from modules.模块2_核心业务引擎模块.pipeline_orchestrator import PipelineOrchestrator
    
    # 检查方法是否存在
    orchestrator = PipelineOrchestrator()
    methods = dir(orchestrator)
    
    if 'run_landing_plan_generation' in methods:
        print("✅ run_landing_plan_generation 方法存在")
    else:
        print("❌ run_landing_plan_generation 方法不存在")
    
    if 'run_ide_bundle_generation' in methods:
        print("✅ run_ide_bundle_generation 方法存在")
        
        # 检查方法签名
        import inspect
        sig = inspect.signature(orchestrator.run_ide_bundle_generation)
        params = list(sig.parameters.keys())
        print(f"   参数列表: {params}")
        
        # self 是隐式的，不需要显式检查
        expected_params = ['final_solution', 'contracts', 'landing_plan', 'structured_requirement']
        if all(p in params for p in expected_params):
            print("✅ run_ide_bundle_generation 方法签名正确")
        else:
            print(f"❌ run_ide_bundle_generation 方法签名不正确，期望包含: {expected_params}")
    else:
        print("❌ run_ide_bundle_generation 方法不存在")
        
except Exception as e:
    print(f"❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3: 检查 pipeline_controller.py
print("\n[测试3] 检查 pipeline_controller.py...")
try:
    from modules.模块0_全局调度面板.pipeline_controller import PipelineController
    
    controller = PipelineController()
    methods = dir(controller)
    
    if 'start_pipeline' in methods:
        print("✅ start_pipeline 方法存在")
    else:
        print("❌ start_pipeline 方法不存在")
        
except Exception as e:
    print(f"❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 检查 jinja 模板（传入测试数据）
print("\n[测试4] 检查 jinja 模板...")
try:
    from modules.模块X_提示词工程模块.prompt_engine import PromptEngine
    
    prompt_engine = PromptEngine()
    
    # 准备测试数据
    test_data = {
        "final_solution": json.dumps({"test": "data"}, ensure_ascii=False),
        "contracts": json.dumps({"test": "data"}, ensure_ascii=False),
        "agent_md": "# Test",
        "module_info": json.dumps({"id": 0, "name": "test"}, ensure_ascii=False),
        "module": json.dumps({"id": 0, "name": "test"}, ensure_ascii=False),
        "modules": json.dumps([], ensure_ascii=False),
        "project_info": json.dumps({}, ensure_ascii=False),
        "structured_requirement": json.dumps({}, ensure_ascii=False),
        "landing_plan": json.dumps({}, ensure_ascii=False)
    }
    
    # 检查模板是否存在
    templates_to_check = [
        ('final_landing_plan_md', {'structured_requirement': '{}', 'final_architecture': '{}', 'contracts': '{}'}),
        ('final_landing_plan_json', {'structured_requirement': '{}', 'final_architecture': '{}', 'contracts': '{}'}),
        ('agent_md_gen', {'final_solution': '{}', 'contracts': '{}', 'modules': '[]', 'project_info': '{}'}),
        ('global_ide_bundle', {'final_solution': '{}', 'contracts': '{}', 'agent_md': '# Test', 'structured_requirement': '{}', 'landing_plan': '{}'}),
        ('module_ide_bundle', {'module_info': '{}', 'module': '{}', 'final_solution': '{}', 'contracts': '{}', 'agent_md': '# Test', 'structured_requirement': '{}'})
    ]
    
    for template_id, template_vars in templates_to_check:
        try:
            prompt = prompt_engine.generate_prompt(template_id, template_vars)
            print(f"✅ {template_id} 模板存在")
        except Exception as e:
            print(f"❌ {template_id} 模板不存在或加载失败: {e}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("测试完成")
print("="*80)


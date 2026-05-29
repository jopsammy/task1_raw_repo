"""
测试 UI 修复脚本
验证 ViewModel Adapter 和指标提取函数是否正常工作
"""

import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

from modules.模块4_交互层模块.view_model_adapter import (
    normalize_all_stage,
    normalize_requirement_anchoring,
    normalize_requirement_validation,
    normalize_contract_generation,
    normalize_landing_plan,
    normalize_ide_bundle
)
from modules.模块4_交互层模块.streamlit.ui_renderer import (
    extract_requirement_anchoring_metrics,
    extract_requirement_validation_metrics,
    extract_contract_generation_metrics,
    extract_landing_plan_metrics,
    extract_ide_bundle_metrics
)


def load_test_data():
    """加载测试数据 - 使用真实的运行记录"""
    test_dir = os.path.join(current_dir, "workspace", "outputs", "20260309_064355")
    
    if not os.path.exists(test_dir):
        print(f"测试目录不存在: {test_dir}")
        return None
    
    data = {}
    
    files = [
        ("structured_requirement.json", "requirement_anchoring", "structured_requirement"),
        ("requirement_validation.json", "requirement_validation", "validation_result"),
        ("final_architecture.json", "architecture_iteration", "final_solution"),
        ("contracts.json", "contract_generation", "contracts"),
        ("landing_plan.json", "landing_plan_generation", "landing_plan")
    ]
    
    for filename, stage_name, key in files:
        filepath = os.path.join(test_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                stage_data = json.load(f)
                data[stage_name] = {
                    "success": True,
                    "stage": stage_name,
                    key: stage_data
                }
    
    return data


def test_requirement_anchoring():
    """测试需求锚定阶段"""
    print("\n" + "="*60)
    print("测试 1: 需求锚定阶段")
    print("="*60)
    
    test_dir = os.path.join(current_dir, "workspace", "outputs", "20260309_064355")
    filepath = os.path.join(test_dir, "structured_requirement.json")
    
    if not os.path.exists(filepath):
        print("❌ 测试文件不存在")
        return False
    
    with open(filepath, "r", encoding="utf-8") as f:
        structured_req = json.load(f)
    
    stage_result = {
        "success": True,
        "stage": "requirement_anchoring",
        "structured_requirement": structured_req
    }
    
    print("1.1 测试 ViewModel Adapter 归一化...")
    normalized = normalize_requirement_anchoring(stage_result)
    
    print(f"   - entities: {len(normalized.get('entities', []))}")
    print(f"   - flows: {len(normalized.get('flows', []))}")
    print(f"   - attributes: {len(normalized.get('attributes', []))}")
    
    if normalized.get('entities') or normalized.get('flows') or normalized.get('attributes'):
        print("   ✅ ViewModel Adapter 工作正常")
    else:
        print("   ❌ ViewModel Adapter 没有提取到数据")
    
    print("\n1.2 测试指标提取函数...")
    metrics = extract_requirement_anchoring_metrics(normalized)
    print(f"   - 识别实体数: {metrics.get('识别实体数', {}).get('value', 0)}")
    print(f"   - 业务流程数: {metrics.get('业务流程数', {}).get('value', 0)}")
    print(f"   - 属性总数: {metrics.get('属性总数', {}).get('value', 0)}")
    
    if (metrics.get('识别实体数', {}).get('value', 0) > 0 or 
        metrics.get('业务流程数', {}).get('value', 0) > 0 or 
        metrics.get('属性总数', {}).get('value', 0) > 0):
        print("   ✅ 指标提取函数工作正常")
        return True
    else:
        print("   ❌ 指标提取函数返回全0")
        return False


def test_requirement_validation():
    """测试需求校验阶段"""
    print("\n" + "="*60)
    print("测试 2: 需求校验阶段")
    print("="*60)
    
    test_dir = os.path.join(current_dir, "workspace", "outputs", "20260309_064355")
    filepath = os.path.join(test_dir, "requirement_validation.json")
    
    if not os.path.exists(filepath):
        print("❌ 测试文件不存在")
        return False
    
    with open(filepath, "r", encoding="utf-8") as f:
        validation_result = json.load(f)
    
    stage_result = {
        "success": True,
        "stage": "requirement_validation",
        "validation_result": validation_result
    }
    
    print("2.1 测试 ViewModel Adapter 归一化...")
    normalized = normalize_requirement_validation(stage_result)
    
    print(f"   - passed: {len(normalized.get('passed', []))}")
    print(f"   - warnings: {len(normalized.get('warnings', []))}")
    print(f"   - errors: {len(normalized.get('errors', []))}")
    
    if normalized.get('passed') or normalized.get('warnings') or normalized.get('errors'):
        print("   ✅ ViewModel Adapter 工作正常")
    else:
        print("   ❌ ViewModel Adapter 没有提取到数据")
    
    print("\n2.2 测试指标提取函数...")
    metrics = extract_requirement_validation_metrics(normalized)
    print(f"   - 校验维度: {metrics.get('校验维度', {}).get('value', 0)}")
    print(f"   - 平均得分: {metrics.get('平均得分', {}).get('value', 0)}")
    print(f"   - 问题数: {metrics.get('问题数', {}).get('value', 0)}")
    
    if (metrics.get('校验维度', {}).get('value', 0) > 0 or 
        metrics.get('平均得分', {}).get('value', 0) > 0):
        print("   ✅ 指标提取函数工作正常")
        return True
    else:
        print("   ❌ 指标提取函数返回全0")
        return False


def test_contract_generation():
    """测试契约生成阶段"""
    print("\n" + "="*60)
    print("测试 3: 契约生成阶段")
    print("="*60)
    
    test_dir = os.path.join(current_dir, "workspace", "outputs", "20260309_064355")
    filepath = os.path.join(test_dir, "contracts.json")
    
    if not os.path.exists(filepath):
        print("❌ 测试文件不存在")
        return False
    
    with open(filepath, "r", encoding="utf-8") as f:
        contracts = json.load(f)
    
    stage_result = {
        "success": True,
        "stage": "contract_generation",
        "contracts": contracts
    }
    
    print("3.1 测试 ViewModel Adapter 归一化...")
    normalized = normalize_contract_generation(stage_result)
    
    print(f"   - interfaces: {len(normalized.get('interfaces', []))}")
    print(f"   - schemas: {len(normalized.get('schemas', {}))}")
    print(f"   - mock_files: {len(normalized.get('mock_files', []))}")
    
    if normalized.get('interfaces') or normalized.get('schemas') or normalized.get('mock_files'):
        print("   ✅ ViewModel Adapter 工作正常")
    else:
        print("   ❌ ViewModel Adapter 没有提取到数据")
    
    print("\n3.2 测试指标提取函数...")
    metrics = extract_contract_generation_metrics(normalized)
    print(f"   - 接口总数: {metrics.get('接口总数', {}).get('value', 0)}")
    print(f"   - Schema总数: {metrics.get('Schema总数', {}).get('value', 0)}")
    print(f"   - Mock文件数: {metrics.get('Mock文件数', {}).get('value', 0)}")
    
    if (metrics.get('接口总数', {}).get('value', 0) > 0 or 
        metrics.get('Schema总数', {}).get('value', 0) > 0 or 
        metrics.get('Mock文件数', {}).get('value', 0) > 0):
        print("   ✅ 指标提取函数工作正常")
        return True
    else:
        print("   ❌ 指标提取函数返回全0")
        return False


def test_landing_plan():
    """测试落地方案阶段"""
    print("\n" + "="*60)
    print("测试 4: 落地方案阶段")
    print("="*60)
    
    test_dir = os.path.join(current_dir, "workspace", "outputs", "20260309_064355")
    filepath = os.path.join(test_dir, "landing_plan.json")
    
    if not os.path.exists(filepath):
        print("❌ 测试文件不存在")
        return False
    
    with open(filepath, "r", encoding="utf-8") as f:
        landing_plan = json.load(f)
    
    stage_result = {
        "success": True,
        "stage": "landing_plan_generation",
        "landing_plan": landing_plan
    }
    
    print("4.1 测试 ViewModel Adapter 归一化...")
    normalized = normalize_landing_plan(stage_result)
    
    print(f"   - modules: {len(normalized.get('modules', []))}")
    print(f"   - markdown_content: {'存在' if normalized.get('markdown_content') else '不存在'}")
    
    if normalized.get('modules') or normalized.get('markdown_content'):
        print("   ✅ ViewModel Adapter 工作正常")
    else:
        print("   ❌ ViewModel Adapter 没有提取到数据")
    
    print("\n4.2 测试指标提取函数...")
    metrics = extract_landing_plan_metrics(normalized)
    print(f"   - 模块数: {metrics.get('模块数', {}).get('value', 0)}")
    print(f"   - 文件数: {metrics.get('文件数', {}).get('value', 0)}")
    
    if (metrics.get('模块数', {}).get('value', 0) > 0 or 
        metrics.get('文件数', {}).get('value', 0) > 0):
        print("   ✅ 指标提取函数工作正常")
        return True
    else:
        print("   ❌ 指标提取函数返回全0")
        return False


def test_ide_bundle():
    """测试IDE引导包阶段"""
    print("\n" + "="*60)
    print("测试 5: IDE引导包阶段")
    print("="*60)
    
    stage_result = {
        "success": True,
        "stage": "ide_bundle_generation",
        "ide_bundle": {
            "global": {"content": "测试内容"},
            "modules": [
                {"name": "模块0", "content": "模块内容"},
                {"name": "模块1", "content": "模块内容"}
            ]
        }
    }
    
    print("5.1 测试 ViewModel Adapter 归一化...")
    normalized = normalize_ide_bundle(stage_result)
    
    print(f"   - files: {len(normalized.get('files', []))}")
    print(f"   - rules_count: {normalized.get('rules_count', 0)}")
    print(f"   - mock_count: {normalized.get('mock_count', 0)}")
    
    if normalized.get('files') or normalized.get('rules_count') or normalized.get('mock_count'):
        print("   ✅ ViewModel Adapter 工作正常")
    else:
        print("   ❌ ViewModel Adapter 没有提取到数据")
    
    print("\n5.2 测试指标提取函数...")
    metrics = extract_ide_bundle_metrics(normalized)
    print(f"   - 文件数: {metrics.get('文件数', {}).get('value', 0)}")
    print(f"   - 规则数: {metrics.get('规则数', {}).get('value', 0)}")
    print(f"   - Mock数: {metrics.get('Mock数', {}).get('value', 0)}")
    
    if (metrics.get('文件数', {}).get('value', 0) > 0 or 
        metrics.get('规则数', {}).get('value', 0) > 0 or 
        metrics.get('Mock数', {}).get('value', 0) > 0):
        print("   ✅ 指标提取函数工作正常")
        return True
    else:
        print("   ❌ 指标提取函数返回全0")
        return False


def main():
    print("="*60)
    print("UI 修复验证测试")
    print("="*60)
    
    results = []
    
    results.append(("需求锚定阶段", test_requirement_anchoring()))
    results.append(("需求校验阶段", test_requirement_validation()))
    results.append(("契约生成阶段", test_contract_generation()))
    results.append(("落地方案阶段", test_landing_plan()))
    results.append(("IDE引导包阶段", test_ide_bundle()))
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n🎉 所有测试通过！修复成功！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查")
        return 1


if __name__ == "__main__":
    sys.exit(main())

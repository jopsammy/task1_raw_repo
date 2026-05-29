
import json
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.insert(0, project_root)

# 让我们直接复制 _parse_llm_json_output 并测试
def my_parse(content):
    result = {}
    
    # 1. 尝试直接解析
    try:
        result = json.loads(content)
        print("✅ 直接解析成功")
    except Exception as e:
        print(f"❌ 直接解析失败: {e}")
    
    # 2. 如果失败，尝试提取代码块
    if not result:
        import re
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if match:
            try:
                result = json.loads(match.group(1))
                print("✅ 从代码块解析成功")
            except Exception as e:
                print(f"❌ 代码块解析失败: {e}")
    
    # 3. 如果解析结果包含 raw_content，继续解析
    for i in range(3):
        print(f"  第 {i+1} 轮解析: result is dict: {isinstance(result, dict)}, has raw_content: {'raw_content' in result if isinstance(result, dict) else False}")
        if isinstance(result, dict) and "raw_content" in result:
            try:
                inner = json.loads(result["raw_content"])
                print(f"  ✅ 解析 raw_content 成功")
                result = inner
            except Exception as e:
                print(f"  ❌ 解析 raw_content 失败: {e}")
                break
        else:
            break
    
    print(f"最终结果: {type(result)}, keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
    return result

# 让我们从 run_record 中取一个 fusion_result
run_path = os.path.join(current_dir, "..", "workspace", "runs", "20260309", "1f8c2419-1f18-4a79-8336-29a5c7d1bd1b.json")

print("=" * 80)
print("读取运行记录")
print("=" * 80)

with open(run_path, 'r', encoding='utf-8') as f:
    run_data = json.load(f)

arch_iter = run_data["results"]["architecture_iteration"]

print("\n=== 查看 arch_iter keys ===")
print(list(arch_iter.keys()))

print("\n=== 查看 arch_iter['final_solution'] ===")
print(f"type: {type(arch_iter['final_solution'])}")
if isinstance(arch_iter['final_solution'], dict):
    print(f"keys: {list(arch_iter['final_solution'].keys())}")
    
    # 看看原始 raw_llm_response
    # 我们需要找 fusion 相关的原始响应

print("\n" + "=" * 80)

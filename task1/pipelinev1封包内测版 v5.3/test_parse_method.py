
import json
import sys
import os

# 添加项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.insert(0, project_root)

# 从运行记录中读取 fusion_result 的 content
run_record_path = os.path.join(current_dir, "..", "workspace", "runs", "20260309", "1f8c2419-1f18-4a79-8336-29a5c7d1bd1b.json")

print("=" * 80)
print("测试 _parse_llm_json_output 方法")
print("=" * 80)

with open(run_record_path, 'r', encoding='utf-8') as f:
    run_data = json.load(f)

# 让我们复制一个简单版本的 _parse_llm_json_output
def test_parse(content):
    print(f"\n输入长度: {len(content)}")
    
    def deep_parse(raw_content):
        """递归解析，处理嵌套的raw_content"""
        try:
            result = raw_content
            if isinstance(result, dict) and "raw_content" in result:
                try:
                    inner = json.loads(result["raw_content"])
                    return deep_parse(inner)
                except:
                    pass
            return result
        except:
            return {"raw_content": raw_content}
    
    try:
        result = json.loads(content)
        print(f"✅ 直接解析成功")
        result = deep_parse(result)
        return result
    except json.JSONDecodeError:
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                print(f"✅ 从代码块解析成功")
                result = deep_parse(result)
                return result
            except json.JSONDecodeError:
                pass
        return {}

# 让我们测试
arch_iter_result = run_data["results"]["architecture_iteration"]

# 我们来查看一下 individual_solutions
print("\n=== 查看 individual_solutions[0].solution ===")
sol0 = arch_iter_result["individual_solutions"][0]["solution"]
print(f"sol0 type: {type(sol0)}")
print(f"sol0 keys: {list(sol0.keys()) if isinstance(sol0, dict) else 'N/A'}")

print("\n=== 测试解析 ===")
# 我们直接复制 _parse_llm_json_output 原来的实现
def original_parse(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        return {"raw_content": content}

# 我们来尝试读取一个 solution 的 raw_response
sol0_raw = arch_iter_result["individual_solutions"][0]["raw_response"]
print(f"\nsol0 raw_response 长度: {len(sol0_raw)}")
print(f"sol0 raw_response 前200字符: {repr(sol0_raw[:200])}")

result1 = original_parse(sol0_raw)
print(f"\noriginal_parse 结果: {type(result1)}, keys: {list(result1.keys()) if isinstance(result1, dict) else 'N/A'}")

print("\n" + "=" * 80)

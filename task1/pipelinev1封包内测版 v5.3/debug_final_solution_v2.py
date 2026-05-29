
import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

# 从运行记录中读取 architecture_iteration 的 final_solution
run_record_path = os.path.join(current_dir, "..", "workspace", "runs", "20260309", "1f8c2419-1f18-4a79-8336-29a5c7d1bd1b.json")

print("=" * 80)
print("从运行记录中分析 final_solution 结构")
print("=" * 80)

with open(run_record_path, 'r', encoding='utf-8') as f:
    run_data = json.load(f)

print("✅ 读取运行记录成功")

arch_iter_result = run_data["results"]["architecture_iteration"]
final_solution = arch_iter_result["final_solution"]

print(f"\nfinal_solution 类型: {type(final_solution)}")
print(f"final_solution keys: {list(final_solution.keys()) if isinstance(final_solution, dict) else 'N/A'}")

if isinstance(final_solution, dict) and "raw_content" in final_solution:
    print("\n发现 raw_content，尝试解析...")
    try:
        inner = json.loads(final_solution["raw_content"])
        print(f"✅ 解析成功，inner 类型: {type(inner)}")
        print(f"inner keys: {list(inner.keys())}")
        
        if "fused_solution" in inner:
            print("\n✅ 发现 fused_solution!")
            fused = inner["fused_solution"]
            print(f"fused_solution keys: {list(fused.keys())}")
            
            if "architecture" in fused:
                print("\n✅ 发现 architecture!")
                arch = fused["architecture"]
                print(f"architecture keys: {list(arch.keys())}")
                
                if "modules" in arch:
                    print(f"\n✅ 发现 modules! 数量: {len(arch['modules'])}")
                    for idx, mod in enumerate(arch['modules']):
                        print(f"  模块 {idx+1}: {mod.get('name', '未命名')}")
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)

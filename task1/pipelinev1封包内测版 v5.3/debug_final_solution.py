
import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
final_arch_path = os.path.join(current_dir, "workspace", "outputs", "20260309_cb3446", "final_architecture.json")

print("=" * 80)
print("调试 final_architecture.json")
print("=" * 80)
print(f"文件路径: {final_arch_path}")
print(f"文件存在: {os.path.exists(final_arch_path)}")

with open(final_arch_path, 'r', encoding='utf-8') as f:
    data_str = f.read()

print(f"\n文件长度: {len(data_str)} 字符")
print("\n尝试直接解析...")
try:
    data = json.loads(data_str)
    print(f"✅ 解析成功，类型: {type(data)}")
    print(f"keys: {list(data.keys())}")
    
    if "raw_content" in data:
        print("\n发现 raw_content，尝试解析...")
        try:
            inner_data = json.loads(data["raw_content"])
            print(f"✅ 内部解析成功，类型: {type(inner_data)}")
            print(f"inner keys: {list(inner_data.keys())}")
            
            if "fused_solution" in inner_data:
                print("\n发现 fused_solution!")
                fused = inner_data["fused_solution"]
                print(f"fused keys: {list(fused.keys())}")
                
                if "architecture" in fused:
                    print("\n发现 architecture!")
                    arch = fused["architecture"]
                    print(f"arch keys: {list(arch.keys())}")
                    
                    if "modules" in arch:
                        print(f"\n✅ 发现 modules! 数量: {len(arch['modules'])}")
                        for idx, mod in enumerate(arch['modules']):
                            print(f"  模块 {idx+1}: {mod.get('name', '未命名')}")
        except Exception as e:
            print(f"❌ 内部解析失败: {e}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"❌ 解析失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

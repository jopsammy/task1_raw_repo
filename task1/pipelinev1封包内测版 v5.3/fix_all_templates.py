
#!/usr/bin/env python
"""
批量修复所有模板文件：移除 {% raw %} 和 {% endraw %} 包裹
"""
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
prompts_dir = os.path.join(current_dir, "modules", "模块X_提示词工程模块", "prompts")

print("="*80)
print("批量修复所有提示词模板")
print("="*80)

for filename in os.listdir(prompts_dir):
    if not filename.endswith(".jinja"):
        continue
    
    filepath = os.path.join(prompts_dir, filename)
    print(f"\n处理文件: {filename}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除 {% raw %} 和 {% endraw %}
    old_content = content
    content = content.replace("{% raw %}\n", "")
    content = content.replace("{% raw %}", "")
    content = content.replace("\n{% endraw %}", "")
    content = content.replace("{% endraw %}", "")
    
    if old_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已修复: 移除了 raw/endraw 包裹")
    else:
        print(f"ℹ️  无需修改")

print("\n" + "="*80)
print("所有模板修复完成！")
print("="*80)

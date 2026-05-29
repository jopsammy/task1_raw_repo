
"""
修复HTML实体编码问题的脚本
将 -&amp;gt; 替换为 -&gt;
"""
import os

def fix_file(filepath):
    """修复单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含需要修复的内容
    if '-&gt;' in content:
        print(f"修复: {filepath}")
        content = content.replace('-&gt;', '-&gt;')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    return False

def main():
    """主函数"""
    v1_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 查找所有Python文件
    python_files = []
    for root, dirs, files in os.walk(v1_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"找到 {len(python_files)} 个Python文件")
    
    fixed_count = 0
    for filepath in python_files:
        if fix_file(filepath):
            fixed_count += 1
    
    print(f"修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    main()

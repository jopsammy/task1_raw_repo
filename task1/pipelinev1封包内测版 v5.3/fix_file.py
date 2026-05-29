
import os

# 读取备份文件
backup_path = 'modules/模块2_核心业务引擎模块/pipeline_orchestrator.py.backup_20260309'
with open(backup_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复空行问题
lines = content.split('\n')
new_lines = []

consecutive_empty = 0
for line in lines:
    if not line.strip():
        consecutive_empty += 1
        if consecutive_empty &lt;= 2:
            new_lines.append(line)
    else:
        consecutive_empty = 0
        new_lines.append(line)

fixed_content = '\n'.join(new_lines)

# 写回主文件
target_path = 'modules/模块2_核心业务引擎模块/pipeline_orchestrator.py'
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print(f'已修复并写入: {target_path}')
print(f'原行数: {len(lines)}, 修复后行数: {len(new_lines)}')

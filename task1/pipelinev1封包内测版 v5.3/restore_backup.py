
import os
import shutil

# 备份当前的 pipeline_orchestrator.py（以防万一）
backup_dir = os.path.dirname(os.path.abspath(__file__))
orchestrator_path = os.path.join(backup_dir, "modules", "模块2_核心业务引擎模块", "pipeline_orchestrator.py")
backup_path = os.path.join(backup_dir, "modules", "模块2_核心业务引擎模块", "pipeline_orchestrator.py.backup_20260309")

# 先读一下备份文件的内容，确保 PipelineStage 枚举正确
with open(backup_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 确保 PipelineStage 枚举没有 LANDING_PLAN_GENERATION
if 'LANDING_PLAN_GENERATION' in content:
    print("备份文件中有 LANDING_PLAN_GENERATION，需要清理...")
    # 这太复杂了，让我手动修复
    pass

# 简单直接：复制备份文件覆盖
shutil.copyfile(backup_path, orchestrator_path)
print(f"✅ 已从 {backup_path} 恢复到 {orchestrator_path}")

# 现在手动修复 PipelineStage 枚举 - 移除可能误添加的 LANDING_PLAN_GENERATION
with open(orchestrator_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_enum = False
for line in lines:
    if 'class PipelineStage' in line:
        in_enum = True
    if in_enum and 'LANDING_PLAN_GENERATION' in line:
        print("❌ 发现 LANDING_PLAN_GENERATION，跳过该行")
        continue
    if in_enum and 'COMPLETED' in line:
        in_enum = False
    new_lines.append(line)

with open(orchestrator_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ PipelineStage 枚举已修复")
print("✅ 备份恢复完成！")

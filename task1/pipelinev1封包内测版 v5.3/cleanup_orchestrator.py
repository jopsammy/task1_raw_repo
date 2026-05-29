
import os

file_path = 'modules/模块2_核心业务引擎模块/pipeline_orchestrator.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 移除 run_landing_plan_generation 方法
start_marker = '    def run_landing_plan_generation'
end_marker = '    def run_ide_bundle_generation'

idx1 = content.find(start_marker)
idx2 = content.find(end_marker)

if idx1 &gt; -1 and idx2 &gt; -1:
    content = content[:idx1] + content[idx2:]
    print('已移除 run_landing_plan_generation 方法')

# 2. 修复 run_ide_bundle_generation 方法签名
old_sig = '    def run_ide_bundle_generation(self, final_solution: Dict[str, Any], \n                                   contracts: Dict[str, Any],\n                                   structured_requirement: Optional[Dict[str, Any]] = None,\n                                   landing_plan: Optional[Dict[str, Any]] = None) -&gt; Dict[str, Any]:'
new_sig = '    def run_ide_bundle_generation(self, final_solution: Dict[str, Any], \n                                   contracts: Dict[str, Any]) -&gt; Dict[str, Any]:'
content = content.replace(old_sig, new_sig)
print('已修复 run_ide_bundle_generation 方法签名')

# 3. 清理 run_full_pipeline 中的调用
# 找到并移除阶段4.5的代码
# 使用简单的分割方式
lines = content.split('\n')
new_lines = []
skip = False

for line in lines:
    if '# 阶段4.5: 落地方案生成' in line:
        skip = True
        continue
    if skip and '# 阶段5: IDE引导包生成' in line:
        skip = False
        new_lines.append(line)
        continue
    if skip:
        continue
    new_lines.append(line)

content = '\n'.join(new_lines)

# 然后修复 stage5_result 调用
old_call = '''            stage5_result = self.run_ide_bundle_generation(

                stage3_result["final_solution"],

                stage4_result["contracts"],
                stage1_result["structured_requirement"],
                stage4_5_result["landing_plan"]

            )'''

new_call = '''            stage5_result = self.run_ide_bundle_generation(

                stage3_result["final_solution"],

                stage4_result["contracts"]

            )'''

content = content.replace(old_call, new_call)
print('已修复 run_full_pipeline 中的调用')

# 清理 run_ide_bundle_generation 内部对 modules 和 project_info 的使用
# 我们不修改这个，因为模板已经修复了

# 保存
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'✅ 清理完成，保存到: {file_path}')

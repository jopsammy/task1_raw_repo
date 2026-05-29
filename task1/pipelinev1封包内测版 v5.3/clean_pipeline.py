
import os

file_path = 'modules/模块2_核心业务引擎模块/pipeline_orchestrator.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0

# 找到 PipelineStage 枚举类，移除 LANDING_PLAN_GENERATION
while i &lt; len(lines):
    line = lines[i]
    if 'LANDING_PLAN_GENERATION' in line:
        i += 1
        continue
    new_lines.append(line)
    i += 1

content = ''.join(new_lines)

# 找到并移除 run_landing_plan_generation 方法
# 我们从 "def run_landing_plan_generation" 开始
# 找到 "def run_ide_bundle_generation" 作为结束标记
content = content.replace(
    '    def run_landing_plan_generation',
    '    def run_ide_bundle_generation'
)

# 现在清理 run_ide_bundle_generation 的多余部分
# 先找到 "def run_ide_bundle_generation" 出现的位置
idx1 = content.find('def run_ide_bundle_generation')
idx2 = content.find('def run_ide_bundle_generation', idx1 + 1)

if idx2 &gt; -1:
    # 保留第一个，移除第二个
    content = content[:idx1] + content[idx2:]

# 清理 run_full_pipeline 中的阶段4.5
# 简单的替换
content = content.replace(
    '            # 阶段4.5: 落地方案生成\n'
    '            stage4_5_result = self.run_landing_plan_generation(\n'
    '                stage1_result["structured_requirement"],\n'
    '                stage3_result["final_solution"],\n'
    '                stage4_result["contracts"]\n'
    '            )\n'
    '            pipeline_result["stages"][PipelineStage.LANDING_PLAN_GENERATION.value] = stage4_5_result\n'
    '            if not stage4_5_result["success"]:\n'
    '                pipeline_result["error"] = stage4_5_result.get("error")\n'
    '                return pipeline_result\n'
    '\n'
    '            # 阶段5: IDE引导包生成\n'
    '\n'
    '            stage5_result = self.run_ide_bundle_generation(\n'
    '\n'
    '                stage3_result["final_solution"],\n'
    '\n'
    '                stage4_result["contracts"],\n'
    '                stage1_result["structured_requirement"],\n'
    '                stage4_5_result["landing_plan"]\n'
    '\n'
    '            )\n',
    '            # 阶段5: IDE引导包生成\n'
    '\n'
    '            stage5_result = self.run_ide_bundle_generation(\n'
    '\n'
    '                stage3_result["final_solution"],\n'
    '\n'
    '                stage4_result["contracts"]\n'
    '\n'
    '            )\n'
)

# 清理 run_ide_bundle_generation 方法签名
content = content.replace(
    '    def run_ide_bundle_generation(self, final_solution: Dict[str, Any], \n'
    '                                   contracts: Dict[str, Any],\n'
    '                                   structured_requirement: Optional[Dict[str, Any]] = None,\n'
    '                                   landing_plan: Optional[Dict[str, Any]] = None) -&gt; Dict[str, Any]:',
    '    def run_ide_bundle_generation(self, final_solution: Dict[str, Any], \n'
    '                                   contracts: Dict[str, Any]) -&gt; Dict[str, Any]:'
)

# 清理提示词调用中传递的变量
# 先保存文件，然后让我们手动修复
with open(file_path + '.tmp', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'已生成临时文件: {file_path}.tmp')
print('现在手动检查并替换原始文件')

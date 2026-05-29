
"""
模块职责：交付物切分模块
负责pipeline运行结果的切分、格式化与保存
"""

import os
import json
from typing import Dict, Any, Optional


class DeliveryOutputSplitter:
    """
    交付物切分器
    负责pipeline最终结果的切分、格式化与保存
    """

    def __init__(self, workspace_dir=None):
        """
        初始化交付物切分器

        Args:
            workspace_dir: 工作区目录，None则使用默认路径
        """
        if workspace_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '../..'))
            self.workspace_dir = os.path.join(project_root, "workspace")
        else:
            self.workspace_dir = workspace_dir

        self.outputs_dir = os.path.join(self.workspace_dir, "outputs")
        self._ensure_directories()

    def _ensure_directories(self):
        """
        确保必要的目录存在
        """
        if not os.path.exists(self.outputs_dir):
            os.makedirs(self.outputs_dir, exist_ok=True)

    def split_and_save(
        self,
        final_solution,
        all_results,
        project_id,
        workspace_dir=None
    ):
        """
        切分并保存交付物

        Args:
            final_solution: 最终架构解决方案
            all_results: pipeline所有阶段结果
            project_id: 项目ID
            workspace_dir: 工作区目录（可选，覆盖初始化时的目录）

        Returns:
            交付物文件路径字典
        """
        target_workspace = workspace_dir or self.workspace_dir
        outputs_dir = os.path.join(target_workspace, "outputs", project_id)

        if not os.path.exists(outputs_dir):
            os.makedirs(outputs_dir, exist_ok=True)

        deliveries = {}

        try:
            self._save_structured_requirement(outputs_dir, all_results, deliveries)
            self._save_requirement_validation(outputs_dir, all_results, deliveries)
            self._save_final_architecture(outputs_dir, final_solution, deliveries)
            self._save_contracts(outputs_dir, all_results, deliveries)
            self._save_landing_plan(outputs_dir, all_results, deliveries)
            self._save_ide_bundle(outputs_dir, all_results, deliveries)
            self._save_agent_md(outputs_dir, all_results, deliveries)
        except Exception as e:
            print(f"[ERROR] 保存交付物时出错: {e}")

        return deliveries

    def _save_structured_requirement(self, outputs_dir, all_results, deliveries):
        req_anchor = all_results.get("requirement_anchoring", {})
        if req_anchor.get("success") and "structured_requirement" in req_anchor:
            filepath = os.path.join(outputs_dir, "structured_requirement.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(req_anchor["structured_requirement"], f, ensure_ascii=False, indent=2)
            deliveries["structured_requirement.json"] = filepath

    def _save_requirement_validation(self, outputs_dir, all_results, deliveries):
        req_valid = all_results.get("requirement_validation", {})
        if req_valid.get("success") and "validation_result" in req_valid:
            filepath = os.path.join(outputs_dir, "requirement_validation.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(req_valid["validation_result"], f, ensure_ascii=False, indent=2)
            deliveries["requirement_validation.json"] = filepath

    def _save_final_architecture(self, outputs_dir, final_solution, deliveries):
        if final_solution:
            filepath = os.path.join(outputs_dir, "final_architecture.json")
            
            # 解析 raw_content 包裹
            parsed_solution = final_solution
            for _ in range(3):
                if isinstance(parsed_solution, dict) and "raw_content" in parsed_solution:
                    try:
                        parsed_solution = json.loads(parsed_solution["raw_content"])
                    except:
                        break
                else:
                    break
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(parsed_solution, f, ensure_ascii=False, indent=2)
            deliveries["final_architecture.json"] = filepath

    def _save_contracts(self, outputs_dir, all_results, deliveries):
        contract_gen = all_results.get("contract_generation", {})
        if contract_gen.get("success") and "contracts" in contract_gen:
            filepath = os.path.join(outputs_dir, "contracts.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(contract_gen["contracts"], f, ensure_ascii=False, indent=2)
            deliveries["contracts.json"] = filepath

    def _save_landing_plan(self, outputs_dir, all_results, deliveries):
        landing_plan_gen = all_results.get("landing_plan_generation", {})
        if landing_plan_gen.get("success") and "landing_plan" in landing_plan_gen:
            landing_plan = landing_plan_gen["landing_plan"]
            if "markdown" in landing_plan:
                filepath = os.path.join(outputs_dir, "landing_plan.md")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(landing_plan["markdown"]))
                deliveries["landing_plan.md"] = filepath
            if "json" in landing_plan:
                filepath = os.path.join(outputs_dir, "landing_plan.json")
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(landing_plan["json"], f, ensure_ascii=False, indent=2)
                deliveries["landing_plan.json"] = filepath

    def _save_ide_bundle(self, outputs_dir, all_results, deliveries):
        ide_bundle_data = all_results.get("ide_bundle_generation", {})
        if not ide_bundle_data.get("success") or "ide_bundle" not in ide_bundle_data:
            return

        ide_bundles = ide_bundle_data["ide_bundle"]

        # 检查是否是新格式（包含 global 和 modules）
        if isinstance(ide_bundles, dict) and "global" in ide_bundles and "modules" in ide_bundles:
            # --------------------------
            # 保存全局引导包
            # --------------------------
            global_file_path = os.path.join(outputs_dir, "ide_bundle_global.md")
            with open(global_file_path, "w", encoding="utf-8") as f:
                f.write(str(ide_bundles.get("global", "")))
            deliveries["ide_bundle_global.md"] = global_file_path

            # --------------------------
            # 动态保存每个模块的引导包
            # --------------------------
            for module_bundle in ide_bundles.get("modules", []):
                # 清理模块名中的特殊字符，避免文件名问题
                safe_module_name = "".join([c if c.isalnum() or c in ("_", "-") else "_" 
                                            for c in module_bundle.get("module_name", "unknown")])
                # 文件名规则：ide_bundle_module_模块序号_模块名.md，避免重名
                file_name = f"ide_bundle_module_{module_bundle['module_id']}_{safe_module_name}.md"
                module_file_path = os.path.join(outputs_dir, file_name)
                with open(module_file_path, "w", encoding="utf-8") as f:
                    f.write(str(module_bundle.get("content", "")))
                deliveries[file_name] = module_file_path

            # --------------------------
            # 生成引导包索引文件
            # --------------------------
            index_content = "# IDE引导包索引\n\n"
            index_content += "- [全局引导包](ide_bundle_global.md)\n"
            for module_bundle in ide_bundles.get("modules", []):
                safe_module_name = "".join([c if c.isalnum() or c in ("_", "-") else "_" 
                                            for c in module_bundle.get("module_name", "unknown")])
                file_name = f"ide_bundle_module_{module_bundle['module_id']}_{safe_module_name}.md"
                index_content += f"- [模块{module_bundle['module_id']}: {module_bundle.get('module_name', '未知')}]({file_name})\n"
            index_file_path = os.path.join(outputs_dir, "ide_bundle_index.md")
            with open(index_file_path, "w", encoding="utf-8") as f:
                f.write(index_content)
            deliveries["ide_bundle_index.md"] = index_file_path

        else:
            # 兼容旧格式
            filepath = os.path.join(outputs_dir, "ide_bundle.md")
            content = ide_bundles
            if isinstance(content, dict):
                content = json.dumps(content, ensure_ascii=False, indent=2)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(content))
            deliveries["ide_bundle.md"] = filepath

    def _save_agent_md(self, outputs_dir, all_results, deliveries):
        agent_md = all_results.get("ide_bundle_generation", {})
        if agent_md.get("success") and "ide_bundle" in agent_md:
            ide_bundles = agent_md["ide_bundle"]
            # 检查是否是新格式
            if isinstance(ide_bundles, dict) and "agents_md" in ide_bundles:
                content = ide_bundles["agents_md"]
            else:
                # 兼容旧格式
                if isinstance(ide_bundles, dict) and "agent_md" in ide_bundles:
                    content = ide_bundles["agent_md"]
                else:
                    content = ""
            filepath = os.path.join(outputs_dir, "AGENTS.md")
            if isinstance(content, dict):
                content = json.dumps(content, ensure_ascii=False, indent=2)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(content))
            deliveries["AGENTS.md"] = filepath


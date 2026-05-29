
"""
模块职责：全局调度面板模块
负责pipeline流程编排、进度监控、暂停/继续/回滚
"""

import os
import sys
import json
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
from queue import Queue, Empty

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.insert(0, project_root)

from modules.模块2_核心业务引擎模块.pipeline_orchestrator import (
    get_pipeline_orchestrator, 
    PipelineOrchestrator,
    PipelineStage
)
from modules.模块1_数据锚点与存储模块.run_record_manager import get_run_record_manager
from modules.模块5_交付物切分模块 import get_delivery_output_splitter
from modules.模块4_交互层模块.cli.rich_console import get_rich_console


class ControllerStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class PipelineController:
    def __init__(self, pipeline_orchestrator: Optional[PipelineOrchestrator] = None):
        self.pipeline_orchestrator = pipeline_orchestrator or get_pipeline_orchestrator()
        self.run_record_manager = get_run_record_manager()
        self.console = get_rich_console()
        self.status = ControllerStatus.IDLE
        self.current_stage = ""
        self.progress = 0
        self.logs: List[Dict[str, Any]] = []
        self.results: Dict[str, Any] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.current_run_id: Optional[str] = None
        self._log_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self._progress_callback: Optional[Callable[[int], None]] = None
        self._metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self._state_proxy_callback: Optional[Callable[[str, Any], None]] = None
        
        self.total_tokens = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.files_generated = 0
        self.stage_metrics: Dict[str, Dict[str, Any]] = {}
        self.models_used: List[str] = []
        self.providers_used: List[str] = []
        self.provider_models: Dict[str, List[str]] = {}
        
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._stop_event = threading.Event()
        self._command_queue = Queue()
        self._worker_thread: Optional[threading.Thread] = None
        
        self._init_outputs_directory()
    
    def set_log_callback(self, callback: Optional[Callable[[Dict[str, Any]], None]]):
        """设置日志回调函数
        
        Args:
            callback: 回调函数，接收日志条目字典作为参数
        """
        self._log_callback = callback
    
    def set_progress_callback(self, callback: Optional[Callable[[int], None]]):
        """设置进度回调函数
        
        Args:
            callback: 回调函数，接收进度百分比作为参数
        """
        self._progress_callback = callback
    
    def set_metrics_callback(self, callback: Optional[Callable[[Dict[str, Any]], None]]):
        """设置指标回调函数
        
        Args:
            callback: 回调函数，接收指标字典作为参数
        """
        self._metrics_callback = callback
    
    def set_state_proxy_callback(self, callback: Optional[Callable[[str, Any], None]]):
        """设置StateProxy回调函数（用于同步阶段结果）
        
        Args:
            callback: 回调函数，接收stage名称和result数据作为参数
        """
        self._state_proxy_callback = callback
    
    def _update_metrics(self):
        """更新指标并触发回调"""
        metrics = {
            "total_tokens": self.total_tokens,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "files_generated": self.files_generated,
            "stage_metrics": self.stage_metrics,
            "models_used": self.models_used,
            "providers_used": self.providers_used,
            "provider_models": self.provider_models
        }
        if self._metrics_callback:
            self._metrics_callback(metrics)
    
    def _normalize_usage(self, provider, response, prompt_text=None, completion_text=None):
        """归一化不同 Provider 的 Token 统计（简单版本）
        
        Args:
            provider: Provider 名称
            response: LLM 响应对象
            prompt_text: Prompt 文本（用于兜底估算）
            completion_text: Completion 文本（用于兜底估算）
        
        Returns:
            {"input_tokens": int, "output_tokens": int, "total_tokens": int}
        """
        input_tokens = 0
        output_tokens = 0
        
        if prompt_text:
            input_tokens = max(1, len(prompt_text) // 4)
        if completion_text:
            output_tokens = max(1, len(completion_text) // 4)
        
        total_tokens = input_tokens + output_tokens
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }
    
    def _init_outputs_directory(self):
        workspace_dir = os.path.join(project_root, "workspace")
        outputs_dir = os.path.join(workspace_dir, "outputs")
        if not os.path.exists(outputs_dir):
            os.makedirs(outputs_dir, exist_ok=True)
    
    def _save_delivery_outputs(self, project_id: Optional[str]):
        if not project_id:
            import uuid
            project_id = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
            self._log(f"未指定project_id，自动生成: {project_id}", "INFO", "delivery_output_splitting")
        
        self._log("开始交付物切分阶段", "INFO", "delivery_output_splitting")
        self._update_progress("交付物切分", 98)
        
        workspace_dir = os.path.join(project_root, "workspace")
        
        splitter = get_delivery_output_splitter()
        
        final_solution = self.results.get("architecture_iteration", {}).get("final_solution", {})
        
        deliveries = splitter.split_and_save(
            final_solution=final_solution,
            all_results=self.results,
            project_id=project_id,
            workspace_dir=workspace_dir
        )
        
        # 保存交付物切分结果到运行记录
        if self.current_run_id:
            run_data = self.run_record_manager.load_run_record(self.current_run_id)
            if run_data:
                run_data["results"]["delivery_output_splitting"] = {
                    "success": True,
                    "deliveries": deliveries,
                    "timestamp": datetime.now().isoformat()
                }
                run_data["updated_at"] = datetime.now().isoformat()
                self.run_record_manager.save_run_record(run_data)
        
        for name, filepath in deliveries.items():
            self._log(f"已保存 {name}", "SUCCESS", "delivery_output_splitting")
        
        self._log("交付物切分完成", "SUCCESS", "delivery_output_splitting")
        self._update_progress("交付物切分", 100)

    def _log(self, message: str, level: str = "INFO", stage: str = ""):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "stage": stage or self.current_stage,
            "message": message
        }
        self.logs.append(log_entry)
        if self._log_callback:
            self._log_callback(log_entry)
        else:
            # 使用与CLI一致的rich格式化输出
            if level == "INFO":
                self.console.log_info(message, stage or self.current_stage)
            elif level == "SUCCESS":
                self.console.log_success(message, stage or self.current_stage)
            elif level == "WARNING":
                self.console.log_warning(message, stage or self.current_stage)
            elif level == "ERROR":
                self.console.log_error(message, stage or self.current_stage)

    def _update_progress(self, stage: str, progress: float):
        self.current_stage = stage
        self.progress = max(0, min(100, progress))
        
        # 调用进度回调
        if self._progress_callback:
            self._progress_callback(self.progress)
        
        # 更新运行记录
        if self.current_run_id:
            run_data = self.run_record_manager.load_run_record(self.current_run_id)
            if run_data:
                run_data["current_stage"] = stage
                run_data["progress"] = progress
                run_data["updated_at"] = datetime.now().isoformat()
                self.run_record_manager.save_run_record(run_data)

    def start_pipeline(self, requirement_text: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        if self.status == ControllerStatus.RUNNING:
            return {
                "success": False,
                "error": "Pipeline正在运行中"
            }

        self.status = ControllerStatus.RUNNING
        self.start_time = datetime.now()
        self.end_time = None
        self.logs = []
        self.results = {}
        self.progress = 0
        self.total_tokens = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.files_generated = 0
        self.stage_metrics = {}
        self.models_used = []
        self.providers_used = []
        self.provider_models = {}
        self._stop_event.clear()
        self._pause_event.set()

        # 创建运行记录
        run_data = {
            "run_id": self.run_record_manager.generate_run_id(),
            "project_id": project_id,
            "requirement_text": requirement_text,
            "status": "running",
            "start_time": self.start_time.isoformat(),
            "current_stage": "",
            "progress": 0,
            "logs": [],
            "results": {}
        }
        self.current_run_id = run_data["run_id"]
        self.run_record_manager.save_run_record(run_data)

        self._log("Pipeline启动", "INFO", "pipeline_start")

        try:
            if self._should_stop():
                return self._handle_stop()
            
            self._wait_for_resume()
            self._update_progress("需求锚定", 10)
            self._log("开始需求锚定阶段", "INFO", PipelineStage.REQUIREMENT_ANCHORING.value)
            
            stage1_result = self.pipeline_orchestrator.run_requirement_anchoring(requirement_text, project_id)
            self.results["requirement_anchoring"] = stage1_result
            
            # 同步到StateProxy
            if self._state_proxy_callback:
                self._state_proxy_callback("requirement_anchoring", stage1_result)
            
            # 更新运行记录
            if self.current_run_id:
                run_data = self.run_record_manager.load_run_record(self.current_run_id)
                if run_data:
                    run_data["results"]["requirement_anchoring"] = stage1_result
                    run_data["updated_at"] = datetime.now().isoformat()
                    self.run_record_manager.save_run_record(run_data)
            
            if not stage1_result.get("success"):
                return self._handle_failure(stage1_result.get("error", "需求锚定失败"))
            
            usage = stage1_result.get("usage", {})
            self.total_tokens += usage.get("total_tokens", 0)
            self.input_tokens += usage.get("input_tokens", 0)
            self.output_tokens += usage.get("output_tokens", 0)
            model = stage1_result.get("model", "")
            if model and model not in self.models_used:
                self.models_used.append(model)
            self._update_metrics()
            
            self._update_progress("需求锚定", 20)
            self._log("需求锚定完成", "SUCCESS", PipelineStage.REQUIREMENT_ANCHORING.value)

            if self._should_stop():
                return self._handle_stop()
            
            self._wait_for_resume()
            self._update_progress("需求校验", 30)
            self._log("开始需求校验阶段", "INFO", PipelineStage.REQUIREMENT_VALIDATION.value)
            
            stage2_result = self.pipeline_orchestrator.run_requirement_validation(
                stage1_result["structured_requirement"]
            )
            self.results["requirement_validation"] = stage2_result
            
            # 同步到StateProxy
            if self._state_proxy_callback:
                self._state_proxy_callback("requirement_validation", stage2_result)
            
            # 更新运行记录
            if self.current_run_id:
                run_data = self.run_record_manager.load_run_record(self.current_run_id)
                if run_data:
                    run_data["results"]["requirement_validation"] = stage2_result
                    run_data["updated_at"] = datetime.now().isoformat()
                    self.run_record_manager.save_run_record(run_data)
            
            if not stage2_result.get("success"):
                return self._handle_failure(stage2_result.get("error", "需求校验失败"))
            
            usage = stage2_result.get("usage", {})
            self.total_tokens += usage.get("total_tokens", 0)
            self.input_tokens += usage.get("input_tokens", 0)
            self.output_tokens += usage.get("output_tokens", 0)
            model = stage2_result.get("model", "")
            if model and model not in self.models_used:
                self.models_used.append(model)
            self._update_metrics()
            
            self._update_progress("需求校验", 40)
            self._log("需求校验完成", "SUCCESS", PipelineStage.REQUIREMENT_VALIDATION.value)

            if self._should_stop():
                return self._handle_stop()
            
            self._wait_for_resume()
            self._update_progress("架构迭代", 50)
            self._log("开始架构迭代阶段", "INFO", PipelineStage.ARCHITECTURE_ITERATION.value)
            
            stage3_result = self.pipeline_orchestrator.run_architecture_iteration(
                stage2_result["validation_result"],
                stop_check_callback=self._should_stop
            )
            self.results["architecture_iteration"] = stage3_result
            
            # 同步到StateProxy
            if self._state_proxy_callback:
                self._state_proxy_callback("architecture_iteration", stage3_result)
            
            # 更新运行记录
            if self.current_run_id:
                run_data = self.run_record_manager.load_run_record(self.current_run_id)
                if run_data:
                    run_data["results"]["architecture_iteration"] = stage3_result
                    run_data["updated_at"] = datetime.now().isoformat()
                    self.run_record_manager.save_run_record(run_data)
            
            if not stage3_result.get("success"):
                return self._handle_failure(stage3_result.get("error", "架构迭代失败"))
            
            usage = stage3_result.get("usage", {})
            self.total_tokens += usage.get("total_tokens", 0)
            self.input_tokens += usage.get("input_tokens", 0)
            self.output_tokens += usage.get("output_tokens", 0)
            model = stage3_result.get("model", "")
            if model and model not in self.models_used:
                self.models_used.append(model)
            self._update_metrics()
            
            self._update_progress("架构迭代", 70)
            self._log("架构迭代完成", "SUCCESS", PipelineStage.ARCHITECTURE_ITERATION.value)

            if self._should_stop():
                return self._handle_stop()
            
            self._wait_for_resume()
            self._update_progress("契约生成", 80)
            self._log("开始契约生成阶段", "INFO", PipelineStage.CONTRACT_GENERATION.value)
            
            stage4_result = self.pipeline_orchestrator.run_contract_generation(
                stage3_result["final_solution"]
            )
            self.results["contract_generation"] = stage4_result
            
            # 同步到StateProxy
            if self._state_proxy_callback:
                self._state_proxy_callback("contract_generation", stage4_result)
            
            # 更新运行记录
            if self.current_run_id:
                run_data = self.run_record_manager.load_run_record(self.current_run_id)
                if run_data:
                    run_data["results"]["contract_generation"] = stage4_result
                    run_data["updated_at"] = datetime.now().isoformat()
                    self.run_record_manager.save_run_record(run_data)
            
            if not stage4_result.get("success"):
                return self._handle_failure(stage4_result.get("error", "契约生成失败"))
            
            usage = stage4_result.get("usage", {})
            self.total_tokens += usage.get("total_tokens", 0)
            self.input_tokens += usage.get("input_tokens", 0)
            self.output_tokens += usage.get("output_tokens", 0)
            model = stage4_result.get("model", "")
            if model and model not in self.models_used:
                self.models_used.append(model)
            self._update_metrics()
            
            self._update_progress("契约生成", 85)
            self._log("契约生成完成", "SUCCESS", PipelineStage.CONTRACT_GENERATION.value)

            if self._should_stop():
                return self._handle_stop()
            
            self._wait_for_resume()
            self._update_progress("落地方案生成", 90)
            self._log("开始落地方案生成阶段", "INFO", "landing_plan_generation")
            
            stage5_result = self.pipeline_orchestrator.run_landing_plan_generation(
                stage1_result["structured_requirement"],
                stage3_result["final_solution"],
                stage4_result["contracts"]
            )
            self.results["landing_plan_generation"] = stage5_result
            
            # 同步到StateProxy
            if self._state_proxy_callback:
                self._state_proxy_callback("landing_plan_generation", stage5_result)
            
            # 更新运行记录
            if self.current_run_id:
                run_data = self.run_record_manager.load_run_record(self.current_run_id)
                if run_data:
                    run_data["results"]["landing_plan_generation"] = stage5_result
                    run_data["updated_at"] = datetime.now().isoformat()
                    self.run_record_manager.save_run_record(run_data)
            
            if not stage5_result.get("success"):
                return self._handle_failure(stage5_result.get("error", "落地方案生成失败"))
            
            usage = stage5_result.get("usage", {})
            self.total_tokens += usage.get("total_tokens", 0)
            self.input_tokens += usage.get("input_tokens", 0)
            self.output_tokens += usage.get("output_tokens", 0)
            model = stage5_result.get("model", "")
            if model and model not in self.models_used:
                self.models_used.append(model)
            self._update_metrics()
            
            self._update_progress("落地方案生成", 92)
            self._log("落地方案生成完成", "SUCCESS", "landing_plan_generation")

            if self._should_stop():
                return self._handle_stop()
            
            self._wait_for_resume()
            self._update_progress("可视化生成", 93)
            self._log("开始可视化生成阶段", "INFO", "visualization_generation")
            
            visualization_result = self.pipeline_orchestrator.run_visualization_generation(
                stage5_result.get("landing_plan", {}),
                stage1_result["structured_requirement"]
            )
            self.results["visualization_generation"] = visualization_result
            
            # 同步到StateProxy
            if self._state_proxy_callback:
                self._state_proxy_callback("visualization_generation", visualization_result)
            
            if self.current_run_id:
                run_data = self.run_record_manager.load_run_record(self.current_run_id)
                if run_data:
                    run_data["results"]["visualization_generation"] = visualization_result
                    run_data["updated_at"] = datetime.now().isoformat()
                    self.run_record_manager.save_run_record(run_data)
            
            if not visualization_result.get("success"):
                return self._handle_failure(visualization_result.get("error", "可视化生成失败"))
            
            usage = visualization_result.get("usage", {})
            self.total_tokens += usage.get("total_tokens", 0)
            self.input_tokens += usage.get("input_tokens", 0)
            self.output_tokens += usage.get("output_tokens", 0)
            model = visualization_result.get("model", "")
            if model and model not in self.models_used:
                self.models_used.append(model)
            self._update_metrics()
            
            self._update_progress("可视化生成", 95)
            self._log("可视化生成完成", "SUCCESS", "visualization_generation")

            if self._should_stop():
                return self._handle_stop()
            
            self._wait_for_resume()
            self._update_progress("IDE引导包生成", 98)
            self._log("开始IDE引导包生成阶段", "INFO", PipelineStage.IDE_BUNDLE_GENERATION.value)
            
            stage6_result = self.pipeline_orchestrator.run_ide_bundle_generation(
                stage3_result["final_solution"],
                stage4_result["contracts"],
                stage5_result.get("landing_plan"),
                stage1_result["structured_requirement"]
            )
            self.results["ide_bundle_generation"] = stage6_result
            
            # 同步到StateProxy
            if self._state_proxy_callback:
                self._state_proxy_callback("ide_bundle_generation", stage6_result)
            
            # 更新运行记录
            if self.current_run_id:
                run_data = self.run_record_manager.load_run_record(self.current_run_id)
                if run_data:
                    run_data["results"]["ide_bundle_generation"] = stage6_result
                    run_data["updated_at"] = datetime.now().isoformat()
                    self.run_record_manager.save_run_record(run_data)
            
            if not stage6_result.get("success"):
                return self._handle_failure(stage6_result.get("error", "IDE引导包生成失败"))
            
            usage = stage6_result.get("usage", {})
            self.total_tokens += usage.get("total_tokens", 0)
            self.input_tokens += usage.get("input_tokens", 0)
            self.output_tokens += usage.get("output_tokens", 0)
            model = stage6_result.get("model", "")
            if model and model not in self.models_used:
                self.models_used.append(model)
            self._update_metrics()
            
            self._update_progress("IDE引导包生成", 100)
            self._log("IDE引导包生成完成", "SUCCESS", PipelineStage.IDE_BUNDLE_GENERATION.value)

            self.status = ControllerStatus.IDLE
            self.end_time = datetime.now()
            self._log("Pipeline执行完成", "SUCCESS", "pipeline_complete")

            # 保存交付物文件
            self._save_delivery_outputs(project_id)

            # 更新运行记录为完成状态
            if self.current_run_id:
                run_data = self.run_record_manager.load_run_record(self.current_run_id)
                if run_data:
                    run_data["status"] = "completed"
                    run_data["end_time"] = self.end_time.isoformat()
                    run_data["duration_seconds"] = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
                    run_data["logs"] = self.logs
                    run_data["updated_at"] = datetime.now().isoformat()
                    self.run_record_manager.save_run_record(run_data)

            return {
                "success": True,
                "run_id": self.current_run_id,
                "project_id": project_id,
                "started_at": self.start_time.isoformat() if self.start_time else None,
                "completed_at": self.end_time.isoformat() if self.end_time else None,
                "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0,
                "results": self.results
            }

        except Exception as e:
            return self._handle_failure(str(e))

    def pause_pipeline(self) -> bool:
        if self.status != ControllerStatus.RUNNING:
            return False
        
        self.status = ControllerStatus.PAUSED
        self._pause_event.clear()
        self._log("Pipeline已暂停", "WARNING")
        return True

    def resume_pipeline(self) -> bool:
        if self.status != ControllerStatus.PAUSED:
            return False
        
        self.status = ControllerStatus.RUNNING
        self._pause_event.set()
        self._log("Pipeline已继续", "INFO")
        return True

    def stop_pipeline(self) -> bool:
        if self.status not in [ControllerStatus.RUNNING, ControllerStatus.PAUSED]:
            return False
        
        self._stop_event.set()
        self._pause_event.set()
        self._log("Pipeline正在停止...", "WARNING")
        return True

    def rollback_to_stage(self, stage: str) -> Dict[str, Any]:
        if stage not in self.results:
            return {
                "success": False,
                "error": f"阶段 {stage} 不存在或未完成"
            }
        
        self._log(f"回滚到阶段: {stage}", "WARNING")
        
        stages_order = [
            PipelineStage.REQUIREMENT_ANCHORING.value,
            PipelineStage.REQUIREMENT_VALIDATION.value,
            PipelineStage.ARCHITECTURE_ITERATION.value,
            PipelineStage.CONTRACT_GENERATION.value,
            "landing_plan_generation",
            "visualization_generation",
            PipelineStage.IDE_BUNDLE_GENERATION.value
        ]
        
        try:
            stage_index = stages_order.index(stage)
            for i in range(stage_index + 1, len(stages_order)):
                self.results.pop(stages_order[i], None)
            
            self._update_progress(stage, (stage_index + 1) * 20)
            self._log(f"回滚完成", "SUCCESS")
            
            return {
                "success": True,
                "current_stage": stage,
                "remaining_stages": stages_order[stage_index + 1:]
            }
        except ValueError:
            return {
                "success": False,
                "error": f"无效的阶段: {stage}"
            }

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "current_stage": self.current_stage,
            "progress": self.progress,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "log_count": len(self.logs),
            "result_count": len(self.results),
            "total_tokens": self.total_tokens,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "files_generated": self.files_generated,
            "models_used": self.models_used,
            "providers_used": self.providers_used,
            "provider_models": self.provider_models
        }

    def get_logs(self, limit: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
        logs = self.logs.copy()
        
        if level:
            logs = [log for log in logs if log["level"] == level]
        
        return logs[-limit:]

    def get_results(self) -> Dict[str, Any]:
        return self.results.copy()

    def get_result(self, stage: str) -> Optional[Dict[str, Any]]:
        return self.results.get(stage)

    def clear(self):
        self.status = ControllerStatus.IDLE
        self.current_stage = ""
        self.progress = 0
        self.logs = []
        self.results = {}
        self.start_time = None
        self.end_time = None
        self._stop_event.clear()
        self._pause_event.set()

    def _should_stop(self) -> bool:
        return self._stop_event.is_set()

    def _wait_for_resume(self):
        self._pause_event.wait()

    def _handle_stop(self) -> Dict[str, Any]:
        self.status = ControllerStatus.STOPPED
        self.end_time = datetime.now()
        self._log("Pipeline已停止", "WARNING", "pipeline_stop")
        
        # 更新运行记录为停止状态
        if self.current_run_id:
            run_data = self.run_record_manager.load_run_record(self.current_run_id)
            if run_data:
                run_data["status"] = "stopped"
                run_data["error"] = "Pipeline被用户停止"
                run_data["end_time"] = self.end_time.isoformat()
                run_data["duration_seconds"] = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
                run_data["logs"] = self.logs
                run_data["updated_at"] = datetime.now().isoformat()
                self.run_record_manager.save_run_record(run_data)
        
        return {
            "success": False,
            "run_id": self.current_run_id,
            "error": "Pipeline被用户停止",
            "stopped_at": self.end_time.isoformat() if self.end_time else None,
            "results": self.results
        }

    def _handle_failure(self, error: str) -> Dict[str, Any]:
        self.status = ControllerStatus.IDLE
        self.end_time = datetime.now()
        self._log(f"Pipeline失败: {error}", "ERROR", "pipeline_error")
        
        # 更新运行记录为失败状态
        if self.current_run_id:
            run_data = self.run_record_manager.load_run_record(self.current_run_id)
            if run_data:
                run_data["status"] = "failed"
                run_data["error"] = error
                run_data["end_time"] = self.end_time.isoformat()
                run_data["duration_seconds"] = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
                run_data["logs"] = self.logs
                run_data["updated_at"] = datetime.now().isoformat()
                self.run_record_manager.save_run_record(run_data)
        
        return {
            "success": False,
            "run_id": self.current_run_id,
            "error": error,
            "failed_at": self.end_time.isoformat() if self.end_time else None,
            "results": self.results
        }


_pipeline_controller_instance: Optional[PipelineController] = None


def get_pipeline_controller() -> PipelineController:
    global _pipeline_controller_instance
    if _pipeline_controller_instance is None:
        _pipeline_controller_instance = PipelineController()
    return _pipeline_controller_instance


def reset_pipeline_controller():
    global _pipeline_controller_instance
    _pipeline_controller_instance = None


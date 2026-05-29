"""
模块职责：UI状态代理模块

负责会话状态管理、pipeline进度跟踪、状态持久化
为Streamlit UI提供统一的状态访问接口

v2.0 新增：UIMode状态机管理（INPUT/MONITOR/REVIEW三态模态）
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime
from enum import Enum

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.insert(0, project_root)

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class PipelineStatus(Enum):
    """Pipeline状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class UIMode(Enum):
    """
    UI模态枚举
    
    三态模态架构：
    - INPUT: 意图定义模态，人类主导，专注输入需求
    - MONITOR: 执行监控模态，机器主导，人类监督
    - REVIEW: 成果审查模态，人机交互，展示结果
    """
    INPUT = "input"
    MONITOR = "monitor"
    REVIEW = "review"


class StateProxy:
    """
    UI状态代理类
    
    负责管理Streamlit的session_state与底层数据的同步，以及Pipeline进度跟踪
    
    v2.0 新增：UIMode状态机管理
    """

    def __init__(self, data_anchor_manager=None, pipeline_orchestrator=None):
        """
        初始化状态代理
        
        Args:
            data_anchor_manager: 数据锚点管理器实例
            pipeline_orchestrator: Pipeline编排器实例
        """
        self.data_anchor_manager = data_anchor_manager
        self.pipeline_orchestrator = pipeline_orchestrator
        self._init_session_defaults()

    def _init_session_defaults(self) -> None:
        """初始化session_state的默认属性，避免页面刷新时KeyError"""
        if not STREAMLIT_AVAILABLE:
            return

        if "current_project_id" not in st.session_state:
            st.session_state["current_project_id"] = ""

        if "current_project_data" not in st.session_state:
            st.session_state["current_project_data"] = {}

        if "pipeline_status" not in st.session_state:
            st.session_state["pipeline_status"] = PipelineStatus.IDLE.value

        if "pipeline_current_stage" not in st.session_state:
            st.session_state["pipeline_current_stage"] = ""

        if "pipeline_progress" not in st.session_state:
            st.session_state["pipeline_progress"] = 0

        if "pipeline_logs" not in st.session_state:
            st.session_state["pipeline_logs"] = []

        if "pipeline_results" not in st.session_state:
            st.session_state["pipeline_results"] = {}

        if "prompt_debug_template_id" not in st.session_state:
            st.session_state["prompt_debug_template_id"] = ""

        if "prompt_debug_context" not in st.session_state:
            st.session_state["prompt_debug_context"] = "{}"

        if "prompt_debug_system_prompt" not in st.session_state:
            st.session_state["prompt_debug_system_prompt"] = ""

        if "prompt_debug_user_prompt" not in st.session_state:
            st.session_state["prompt_debug_user_prompt"] = ""

        if "prompt_debug_result" not in st.session_state:
            st.session_state["prompt_debug_result"] = ""

        if "dirty_keys" not in st.session_state:
            st.session_state["dirty_keys"] = set()

        if "last_save_time" not in st.session_state:
            st.session_state["last_save_time"] = 0

        if "active_tab" not in st.session_state:
            st.session_state["active_tab"] = "需求锚定"

        if "ui_mode" not in st.session_state:
            st.session_state["ui_mode"] = UIMode.INPUT.value

        if "pipeline_start_time" not in st.session_state:
            st.session_state["pipeline_start_time"] = 0

        if "total_tokens" not in st.session_state:
            st.session_state["total_tokens"] = 0

    def load_project(self, project_id: str) -> bool:
        """
        加载项目数据到session_state
        
        Args:
            project_id: 项目ID
            
        Returns:
            是否加载成功
        """
        if not STREAMLIT_AVAILABLE or not self.data_anchor_manager:
            return False

        try:
            if not project_id:
                if STREAMLIT_AVAILABLE:
                    st.toast("项目ID不能为空", icon="⚠️")
                return False

            project_data = self.data_anchor_manager.load_requirement_project(project_id)
            st.session_state["current_project_id"] = project_id
            st.session_state["current_project_data"] = project_data
            st.session_state["dirty_keys"] = set()

            if STREAMLIT_AVAILABLE:
                st.toast(f"项目【{project_data['project_name']}】加载成功", icon="✅")
            return True

        except Exception as e:
            if STREAMLIT_AVAILABLE:
                st.toast(f"加载项目失败：{str(e)}", icon="❌")
            return False

    def save_project(self) -> bool:
        """
        将session_state中的项目数据保存到磁盘
        
        Returns:
            是否保存成功
        """
        if not STREAMLIT_AVAILABLE or not self.data_anchor_manager:
            return False

        project_id = st.session_state.get("current_project_id", "")
        if not project_id:
            st.toast("请先加载或创建项目", icon="⚠️")
            return False

        project_data = st.session_state.get("current_project_data", {})
        try:
            success = self.data_anchor_manager.save_requirement_project(project_id, project_data)
            if success:
                st.session_state["dirty_keys"] = set()
                st.session_state["last_save_time"] = int(time.time())
                st.toast("保存成功", icon="✅")
            return success
        except Exception as e:
            st.toast(f"保存失败：{str(e)}", icon="❌")
            return False

    def mark_dirty(self, key: str) -> None:
        """
        标记脏数据
        
        Args:
            key: 脏数据标识
        """
        if not STREAMLIT_AVAILABLE:
            return
        st.session_state["dirty_keys"].add(key)

    def update_pipeline_status(self, status: PipelineStatus, stage: str = "", 
                               progress: float = 0, log_message: str = "") -> None:
        """
        更新Pipeline状态
        
        Args:
            status: Pipeline状态
            stage: 当前阶段
            progress: 进度(0-100)
            log_message: 日志消息
        """
        if not STREAMLIT_AVAILABLE:
            return

        st.session_state["pipeline_status"] = status.value
        st.session_state["pipeline_current_stage"] = stage
        st.session_state["pipeline_progress"] = max(0, min(100, progress))

        if log_message:
            self.add_pipeline_log(log_message)

    def add_pipeline_log(self, message: str, level: str = "INFO", stage: str = None) -> None:
        """
        添加Pipeline日志
        
        Args:
            message: 日志消息
            level: 日志级别(INFO/SUCCESS/WARNING/ERROR)
            stage: 阶段名称（可选）
        """
        if not STREAMLIT_AVAILABLE:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "stage": stage or st.session_state.get("pipeline_current_stage", ""),
            "message": message
        }
        st.session_state["pipeline_logs"].append(log_entry)

        if len(st.session_state["pipeline_logs"]) > 500:
            st.session_state["pipeline_logs"] = st.session_state["pipeline_logs"][-500:]

    def clear_pipeline_logs(self) -> None:
        """清空Pipeline日志"""
        if not STREAMLIT_AVAILABLE:
            return
        st.session_state["pipeline_logs"] = []

    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        获取Pipeline状态
        
        Returns:
            Pipeline状态字典
        """
        if not STREAMLIT_AVAILABLE:
            return {
                "status": PipelineStatus.IDLE.value,
                "stage": "",
                "progress": 0,
                "logs": []
            }

        return {
            "status": st.session_state.get("pipeline_status", PipelineStatus.IDLE.value),
            "stage": st.session_state.get("pipeline_current_stage", ""),
            "progress": st.session_state.get("pipeline_progress", 0),
            "logs": st.session_state.get("pipeline_logs", [])
        }

    def store_pipeline_result(self, stage: str, result: Any) -> None:
        """
        存储Pipeline阶段结果
        
        Args:
            stage: 阶段名称
            result: 结果数据
        """
        if not STREAMLIT_AVAILABLE:
            return
        if "pipeline_results" not in st.session_state:
            st.session_state["pipeline_results"] = {}
        st.session_state["pipeline_results"][stage] = result

    def get_pipeline_result(self, stage: str) -> Optional[Any]:
        """
        获取Pipeline阶段结果
        
        Args:
            stage: 阶段名称
            
        Returns:
            结果数据，不存在返回None
        """
        if not STREAMLIT_AVAILABLE:
            return None
        return st.session_state["pipeline_results"].get(stage)

    def clear_pipeline_results(self) -> None:
        """清空Pipeline结果"""
        if not STREAMLIT_AVAILABLE:
            return
        st.session_state["pipeline_results"] = {}

    def update_prompt_debug(self, template_id: str = None, context: str = None,
                           system_prompt: str = None, user_prompt: str = None,
                           result: str = None) -> None:
        """
        更新提示词调试面板状态
        
        Args:
            template_id: 模板ID
            context: 上下文JSON
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            result: 调试结果
        """
        if not STREAMLIT_AVAILABLE:
            return

        if template_id is not None:
            st.session_state["prompt_debug_template_id"] = template_id
        if context is not None:
            st.session_state["prompt_debug_context"] = context
        if system_prompt is not None:
            st.session_state["prompt_debug_system_prompt"] = system_prompt
        if user_prompt is not None:
            st.session_state["prompt_debug_user_prompt"] = user_prompt
        if result is not None:
            st.session_state["prompt_debug_result"] = result

    def get_prompt_debug_state(self) -> Dict[str, str]:
        """
        获取提示词调试面板状态
        
        Returns:
            调试状态字典
        """
        if not STREAMLIT_AVAILABLE:
            return {
                "template_id": "",
                "context": "{}",
                "system_prompt": "",
                "user_prompt": "",
                "result": ""
            }

        return {
            "template_id": st.session_state.get("prompt_debug_template_id", ""),
            "context": st.session_state.get("prompt_debug_context", "{}"),
            "system_prompt": st.session_state.get("prompt_debug_system_prompt", ""),
            "user_prompt": st.session_state.get("prompt_debug_user_prompt", ""),
            "result": st.session_state.get("prompt_debug_result", "")
        }

    def set_active_tab(self, tab_name: str) -> None:
        """
        设置当前活动Tab
        
        Args:
            tab_name: Tab名称
        """
        if not STREAMLIT_AVAILABLE:
            return
        st.session_state["active_tab"] = tab_name

    def get_active_tab(self) -> str:
        """
        获取当前活动Tab
        
        Returns:
            Tab名称
        """
        if not STREAMLIT_AVAILABLE:
            return "需求锚定"
        return st.session_state.get("active_tab", "需求锚定")

    def persist_state(self, file_path: str) -> bool:
        """
        持久化当前状态到文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        if not STREAMLIT_AVAILABLE:
            return False

        try:
            state_data = {
                "current_project_id": st.session_state.get("current_project_id", ""),
                "current_project_data": st.session_state.get("current_project_data", {}),
                "pipeline_results": st.session_state.get("pipeline_results", {}),
                "persisted_at": datetime.now().isoformat()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"持久化状态失败：{str(e)}")
            return False

    def load_persisted_state(self, file_path: str) -> bool:
        """
        从文件加载持久化状态
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        if not STREAMLIT_AVAILABLE:
            return False

        try:
            if not os.path.exists(file_path):
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)

            if "current_project_id" in state_data:
                st.session_state["current_project_id"] = state_data["current_project_id"]
            if "current_project_data" in state_data:
                st.session_state["current_project_data"] = state_data["current_project_data"]
            if "pipeline_results" in state_data:
                st.session_state["pipeline_results"] = state_data["pipeline_results"]

            return True
        except Exception as e:
            print(f"加载持久化状态失败：{str(e)}")
            return False

    def get_ui_mode(self) -> UIMode:
        """
        获取当前UI模态
        
        Returns:
            当前UIMode枚举值
        """
        if not STREAMLIT_AVAILABLE:
            return UIMode.INPUT
        
        mode_value = st.session_state.get("ui_mode", UIMode.INPUT.value)
        return UIMode(mode_value)

    def set_ui_mode(self, mode: UIMode) -> None:
        """
        设置UI模态
        
        Args:
            mode: 目标UIMode
        """
        if not STREAMLIT_AVAILABLE:
            return
        st.session_state["ui_mode"] = mode.value

    def transition_to_mode(self, target_mode: UIMode) -> None:
        """
        模态切换方法
        
        根据目标模态执行相应的状态转换逻辑
        
        Args:
            target_mode: 目标UIMode
        """
        if not STREAMLIT_AVAILABLE:
            return

        current_mode = self.get_ui_mode()
        
        if target_mode == UIMode.MONITOR:
            if current_mode == UIMode.INPUT:
                st.session_state["pipeline_start_time"] = time.time()
                st.session_state["total_tokens"] = 0
                self.clear_pipeline_logs()
        
        elif target_mode == UIMode.REVIEW:
            pass
        
        elif target_mode == UIMode.INPUT:
            st.session_state["pipeline_status"] = PipelineStatus.IDLE.value
            st.session_state["pipeline_progress"] = 0
            st.session_state["pipeline_current_stage"] = ""
        
        st.session_state["ui_mode"] = target_mode.value

    def get_elapsed_time(self):
        """
        获取Pipeline运行耗时（秒）
        
        支持两种方式获取时间：
        1. 优先使用controller的start_time和end_time（适用于Mock模式）
        2. 如果没有controller时间，则使用pipeline_start_time（适用于真实运行）
        
        Returns:
            耗时秒数
        """
        if not STREAMLIT_AVAILABLE:
            return 0.0
        
        try:
            if "pipeline_controller" in st.session_state:
                controller = st.session_state["pipeline_controller"]
                if hasattr(controller, "start_time") and hasattr(controller, "end_time"):
                    if controller.start_time and controller.end_time:
                        return (controller.end_time - controller.start_time).total_seconds()
                    elif controller.start_time:
                        return (datetime.now() - controller.start_time).total_seconds()
        except Exception:
            pass
        
        start_time = st.session_state.get("pipeline_start_time", 0)
        if start_time == 0:
            return 0.0
        return time.time() - start_time

    def update_tokens(self, tokens: int) -> None:
        """
        更新Token消耗统计
        
        Args:
            tokens: 新增Token数
        """
        if not STREAMLIT_AVAILABLE:
            return
        st.session_state["total_tokens"] = st.session_state.get("total_tokens", 0) + tokens

    def get_total_tokens(self) -> int:
        """
        获取总Token消耗
        
        Returns:
            Token总数
        """
        if not STREAMLIT_AVAILABLE:
            return 0
        return st.session_state.get("total_tokens", 0)

    def is_pipeline_running(self) -> bool:
        """
        检查Pipeline是否正在运行
        
        Returns:
            是否运行中
        """
        if not STREAMLIT_AVAILABLE:
            return False
        return st.session_state.get("pipeline_status") == PipelineStatus.RUNNING.value


_state_proxy_instance: Optional[StateProxy] = None


def get_state_proxy(data_anchor_manager=None, pipeline_orchestrator=None) -> StateProxy:
    """
    获取状态代理单例
    
    Args:
        data_anchor_manager: 数据锚点管理器实例
        pipeline_orchestrator: Pipeline编排器实例
        
    Returns:
        StateProxy实例
    """
    global _state_proxy_instance
    if _state_proxy_instance is None:
        _state_proxy_instance = StateProxy(data_anchor_manager, pipeline_orchestrator)
    return _state_proxy_instance


def reset_state_proxy():
    """重置状态代理单例"""
    global _state_proxy_instance
    _state_proxy_instance = None

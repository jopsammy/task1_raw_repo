"""
模块职责：Streamlit UI模块
提供三态模态架构：意图定义模态、执行监控模态、成果审查模态

v2.0 核心升级：
- 三态模态架构（INPUT/MONITOR/REVIEW）
- 摒弃Meta Refresh，采用Event Loop
- 流式日志展示
- 侧边栏全局控制

- 修复UI执行进度和实时日志与终端不同步问题
- 新增回调函数同步Controller数据到session_state

v2.1 修复：
- 修复后台线程访问st.session_state的警告
- 使用线程安全的共享数据结构替代直接访问st.session_state
"""

import os
import sys
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../../..'))
sys.path.insert(0, project_root)

import streamlit as st

from modules.模块1_数据锚点与存储模块.data_anchor_manager import DataAnchorManager
from modules.模块1_数据锚点与存储模块.config_manager import get_config_manager
from modules.模块1_数据锚点与存储模块.run_record_manager import get_run_record_manager
from modules.模块0_全局调度面板.pipeline_controller import get_pipeline_controller, ControllerStatus
from modules.模块3_UI状态代理模块.state_proxy import get_state_proxy, PipelineStatus, UIMode
from modules.模块X_提示词工程模块.prompt_engine import get_prompt_engine
from modules.模块4_交互层模块.streamlit.ui_renderer import (
    render_pipeline_status,
    render_project_list,
    render_stage_result,
    render_dict_as_cards,
    render_logs,
    render_run_record,
    render_download_button,
    render_stage_progress_bar,
    render_streaming_logs,
    render_review_tabs,
    render_colored_logs_batch,
    render_progress_bar,
    render_footer_summary
)

from modules.模块4_交互层模块.streamlit.mock_mode import (
    is_mock_mode,
    get_mock_data_dir,
    get_mock_ui_mode,
    MockDataManager
)
from modules.模块2_核心业务引擎模块.llm_client import reset_llm_client
from modules.模块2_核心业务引擎模块.pipeline_orchestrator import reset_pipeline_orchestrator
from modules.模块0_全局调度面板.pipeline_controller import reset_pipeline_controller


_pipeline_shared_state = {}
_pipeline_shared_state_lock = threading.Lock()
_pipeline_state_update_queue = []
_pipeline_state_update_lock = threading.Lock()


def _set_shared_state(key: str, value: Any):
    """设置共享状态（线程安全）"""
    with _pipeline_shared_state_lock:
        _pipeline_shared_state[key] = value


def _get_shared_state(key: str, default: Any = None) -> Any:
    """获取共享状态（线程安全）"""
    with _pipeline_shared_state_lock:
        return _pipeline_shared_state.get(key, default)


def _enqueue_state_update(stage: str, result: Any):
    """将状态更新任务加入队列（线程安全）"""
    with _pipeline_state_update_lock:
        _pipeline_state_update_queue.append((stage, result))


def _process_state_updates():
    """处理队列中的状态更新（仅在主线程调用）"""
    with _pipeline_state_update_lock:
        state_proxy = st.session_state.state_proxy
        for stage, result in _pipeline_state_update_queue:
            state_proxy.store_pipeline_result(stage, result)
        _pipeline_state_update_queue.clear()


def _load_mock_data():
    """加载Mock数据，根据MOCK_UI_MODE决定是否进入REVIEW模式"""
    from pathlib import Path
    from modules.模块0_全局调度面板.pipeline_controller import ControllerStatus
    
    mock_dir = get_mock_data_dir()
    if not mock_dir:
        st.error("Mock数据目录未设置")
        return
    
    project_root = Path(__file__).parent.parent.parent.parent
    if not os.path.isabs(mock_dir):
        mock_dir = str(project_root / mock_dir)
    
    if not os.path.exists(mock_dir):
        st.error(f"Mock数据目录不存在: {mock_dir}")
        return
    
    manager = MockDataManager(mock_dir)
    results = manager.load_all()
    
    controller = st.session_state.pipeline_controller
    controller.results = results
    controller.total_tokens = manager.token_stats["total_tokens"]
    controller.input_tokens = manager.token_stats["input_tokens"]
    controller.output_tokens = manager.token_stats["output_tokens"]
    controller.models_used = manager.models_used
    controller.status = ControllerStatus.IDLE
    controller._start_time = datetime.now() - timedelta(seconds=manager.elapsed_time)
    controller._end_time = datetime.now()
    controller.current_run_id = "mock_run_001"
    controller.start_time = datetime.now() - timedelta(seconds=manager.elapsed_time)
    controller.end_time = datetime.now()
    
    mock_dir_path = Path(mock_dir)
    project_id = mock_dir_path.name
    st.session_state["current_project_id"] = project_id
    
    mock_ui_mode = get_mock_ui_mode()
    
    state_proxy = st.session_state.state_proxy
    
    if mock_ui_mode == "REVIEW":
        state_proxy.transition_to_mode(UIMode.REVIEW)
        state_proxy.update_pipeline_status(
            PipelineStatus.COMPLETED, "Mock模式加载完成", 100, "Mock数据加载成功"
        )
        
        for stage, stage_result in results.items():
            if stage_result:
                state_proxy.store_pipeline_result(stage, stage_result)
    else:
        state_proxy.transition_to_mode(UIMode.INPUT)
    
    st.session_state["mock_loaded"] = True
    st.toast(f"✅ Mock数据加载成功: {mock_dir} (模式: {mock_ui_mode})", icon="🎉")


def sync_log_to_session_state(log_entry: Dict[str, Any]):
    """将日志同步到共享状态（线程安全）
    
    Args:
        log_entry: 日志条目字典
    """
    logs = _get_shared_state("pipeline_logs", [])
    logs.append(log_entry)
    
    if len(logs) > 500:
        _set_shared_state("pipeline_logs", logs[-500:])


def sync_progress_to_session_state(progress: int):
    """将进度同步到共享状态（线程安全）
    
    Args:
        progress: 进度百分比(0-100)
    """
    _set_shared_state("pipeline_progress", progress)


def sync_stage_to_session_state(stage: str):
    """将当前阶段同步到共享状态（线程安全）
    
    Args:
        stage: 当前阶段名称
    """
    _set_shared_state("pipeline_current_stage", stage)


def init_services():
    """初始化服务实例
    
    v2.3 新增：支持Mock模式，快速加载预存数据测试UI渲染
    """
    if "data_manager" not in st.session_state:
        st.session_state.data_manager = DataAnchorManager()
    
    if "config_manager" not in st.session_state:
        st.session_state.config_manager = get_config_manager()
    
    if "pipeline_controller" not in st.session_state:
        st.session_state.pipeline_controller = get_pipeline_controller()
    
    if "state_proxy" not in st.session_state:
        st.session_state.state_proxy = get_state_proxy()
    
    if "prompt_engine" not in st.session_state:
        st.session_state.prompt_engine = get_prompt_engine()
    
    if "run_record_manager" not in st.session_state:
        st.session_state.run_record_manager = get_run_record_manager()
    
    if "pipeline_logs" not in st.session_state:
        st.session_state.pipeline_logs = []
    
    if "pipeline_progress" not in st.session_state:
        st.session_state.pipeline_progress = 0
    
    if "pipeline_current_stage" not in st.session_state:
        st.session_state.pipeline_current_stage = ""
    
    controller = st.session_state.pipeline_controller
    
    controller.set_state_proxy_callback(
        lambda stage, result: _enqueue_state_update(stage, result)
    )
    
    if is_mock_mode() and "mock_loaded" not in st.session_state:
        _load_mock_data()


def render_api_management():
    """渲染 API 管理区（3 行 * 3 格 + 保存按钮）"""
    config_manager = st.session_state.config_manager
    controller = st.session_state.pipeline_controller
    
    st.markdown("### 🔑 API 管理")
    with st.expander("展开配置", expanded=False):
        provider_slots = config_manager.get_provider_slots()
        providers = config_manager.get_llm_providers()
        
        api_inputs = []
        for i in range(3):
            provider_id = provider_slots[i]
            provider_config = providers.get(provider_id, {})
            
            st.markdown(f"#### API-{i+1}")
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                url = st.text_input(
                    "URL",
                    value=provider_config.get("api_base", ""),
                    key=f"api_url_{i}",
                    placeholder="https://api.example.com/v1"
                )
            with col2:
                key = st.text_input(
                    "Key",
                    value="",
                    type="password",
                    key=f"api_key_{i}",
                    placeholder="留空保持原值"
                )
            with col3:
                model = st.text_input(
                    "模型",
                    value=provider_config.get("model", ""),
                    key=f"api_model_{i}",
                    placeholder="gpt-4o-mini"
                )
            api_inputs.append((provider_id, url, key, model))
        
        is_running = controller.status == ControllerStatus.RUNNING
        save_disabled = is_running
        
        if st.button(
            "💾 保存配置",
            type="primary",
            disabled=save_disabled,
            key="save_api_config",
            help="运行中禁止修改配置" if save_disabled else None
        ):
            success = True
            for provider_id, url, key, model in api_inputs:
                if url or model:
                    update_result = config_manager.update_provider_fields(
                        provider_id=provider_id,
                        api_base=url if url else None,
                        api_key=key,
                        model=model if model else None
                    )
                    if not update_result:
                        success = False
                        break
            
            if success:
                config_manager.set_default_provider(provider_slots[0])
                if config_manager.save_config():
                    reset_llm_client()
                    reset_pipeline_orchestrator()
                    reset_pipeline_controller()
                    st.toast("✅ 配置保存成功", icon="🎉")
                    st.rerun()
                else:
                    st.toast("❌ 配置保存失败", icon="⚠️")
            else:
                st.toast("❌ 配置验证失败，请检查 URL 格式和模型名称", icon="⚠️")
        
        if is_running:
            st.caption("⚠️ 运行中禁止修改配置")


def render_sidebar():
    """渲染侧边栏：全局控制区 + 项目信息"""
    state_proxy = st.session_state.state_proxy
    controller = st.session_state.pipeline_controller
    ui_mode = state_proxy.get_ui_mode()
    
    sidebar_action = None
    
    with st.sidebar:
        st.markdown("### 🎛️ 全局控制")
        st.markdown("---")
        
        if ui_mode == UIMode.INPUT:
            st.markdown("#### 🟢 空闲状态")
            st.info("输入需求后点击启动按钮开始分析")
            
            if st.button("🚀 启动 Pipeline", type="primary", width="stretch"):
                sidebar_action = "start"
        
        elif ui_mode == UIMode.MONITOR:
            st.markdown("#### 🔵 运行中")
            
            elapsed = state_proxy.get_elapsed_time()
            st.metric("⏱️ 运行耗时", f"{elapsed:.1f}秒")
            
            tokens = controller.total_tokens
            st.metric("📊 Token消耗", f"{tokens:,}")
            
            progress = _get_shared_state("pipeline_progress", 0)
            st.progress(progress / 100)
            current_stage = _get_shared_state("pipeline_current_stage", "")
            st.caption(f"当前阶段: {current_stage if current_stage else controller.current_stage}")
            
            if st.button("⏹️ 停止 Pipeline", type="secondary", width="stretch"):
                sidebar_action = "stop"
        
        elif ui_mode == UIMode.REVIEW:
            st.markdown("#### ✅ 已完成")
            
            elapsed = state_proxy.get_elapsed_time()
            st.metric("⏱️ 总耗时", f"{elapsed:.1f}秒")
            
            tokens = controller.total_tokens
            st.metric("📊 Token消耗", f"{tokens:,}")
            
            if st.button("🔄 重新开始", type="primary", width="stretch"):
                sidebar_action = "reset"
        
        st.markdown("---")
        st.markdown("### 📁 项目信息")
        project_id = st.session_state.get("current_project_id", "")
        if project_id:
            st.caption(f"项目ID: {project_id[:20]}...")
        else:
            st.caption("未加载项目")
    
    return sidebar_action


def render_intent_mode():
    """渲染意图定义模态：需求锚定台"""
    st.markdown("# 🎯 需求锚定台")
    st.markdown("---")
    
    st.markdown("### 📝 输入您的需求")
    st.markdown("请详细描述您的需求，系统将自动进行结构化分析。")
    
    requirement_text = st.text_area(
        label="需求描述",
        placeholder="例如：构建一个用户管理系统，包含用户注册、登录、权限管理等功能...",
        height=200,
        label_visibility="collapsed"
    )
    
    st.session_state["requirement_text"] = requirement_text
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.caption(f"字符数: {len(requirement_text)}")
    
    with col2:
        if st.button("📋 从剪贴板粘贴", width="stretch"):
            pass
    
    st.markdown("---")
    
    render_api_management()
    
    st.markdown("---")
    
    st.info("💡 提示：填写完需求后，点击左侧边栏的「🚀 启动 Pipeline」按钮开始分析。")


def render_monitor_mode():
    """渲染执行监控模态：全息监控屏
    
    v2.1 修复：直接从controller读取数据，确保与终端同步
    v2.2 升级：使用彩色日志渲染、进度条、Footer摘要组件
    """
    state_proxy = st.session_state.state_proxy
    controller = st.session_state.pipeline_controller
    
    st.markdown("# 🔵 执行监控屏")
    st.markdown("---")
    
    progress = controller.progress
    current_stage = controller.current_stage
    
    stages = [
        ("需求锚定", 10),
        ("需求校验", 30),
        ("架构迭代", 50),
        ("契约生成", 80),
        ("落地方案", 90),
        ("交付物切分", 98)
    ]
    
    render_stage_progress_bar(stages, progress, current_stage)
    
    st.markdown("---")
    
    st.markdown("### 📜 实时日志流")
    
    logs = controller.logs
    render_colored_logs_batch(logs[-100:] if logs else [])


def render_review_mode():
    """渲染成果审查模态：架构审查台
    
    v2.2 升级：添加Footer摘要显示
    """
    state_proxy = st.session_state.state_proxy
    controller = st.session_state.pipeline_controller
    
    st.markdown("# ✅ 成果审查台")
    st.markdown("---")
    
    results = controller.results
    
    if not results:
        st.warning("暂无执行结果")
        return
    
    render_review_tabs(results)
    
    st.markdown("---")
    
    duration_seconds = 0.0
    if controller.start_time and controller.end_time:
        duration_seconds = (controller.end_time - controller.start_time).total_seconds()
    elif controller.start_time:
        from datetime import datetime
        duration_seconds = (datetime.now() - controller.start_time).total_seconds()
    
    metrics = {
        "total_tokens": controller.total_tokens,
        "input_tokens": controller.input_tokens,
        "output_tokens": controller.output_tokens,
        "models": controller.models_used if controller.models_used else []
    }
    
    render_footer_summary(duration_seconds, metrics)


def handle_start_pipeline():
    """处理启动Pipeline
    
    v2.1 修复：设置回调函数同步数据，使用共享数据结构避免线程安全问题
    v2.2 修复：后台线程中不访问st.session_state，使用共享数据结构传递状态
    """
    state_proxy = st.session_state.state_proxy
    controller = st.session_state.pipeline_controller
    
    requirement_text = st.session_state.get("requirement_text", "")
    if not requirement_text.strip():
        st.toast("请先输入需求描述", icon="⚠️")
        return
    
    _set_shared_state("pipeline_logs", [])
    _set_shared_state("pipeline_progress", 0)
    _set_shared_state("pipeline_current_stage", "")
    _set_shared_state("pipeline_status", "running")
    _set_shared_state("pipeline_should_transition_to_review", False)
    
    controller.set_log_callback(sync_log_to_session_state)
    controller.set_progress_callback(sync_progress_to_session_state)
    
    state_proxy.transition_to_mode(UIMode.MONITOR)
    state_proxy.update_pipeline_status(PipelineStatus.RUNNING, "启动中", 0, "Pipeline启动")
    
    project_id = st.session_state.get("current_project_id", "")
    
    def run_pipeline_thread():
        try:
            result = controller.start_pipeline(requirement_text, project_id)
            
            if result.get("success"):
                _set_shared_state("pipeline_status", "completed")
                _set_shared_state("pipeline_progress", 100)
                _set_shared_state("pipeline_current_stage", "完成")
                _set_shared_state("pipeline_result_success", True)
            else:
                error_msg = result.get("error", "未知错误")
                _set_shared_state("pipeline_status", "failed")
                _set_shared_state("pipeline_error", error_msg)
                _set_shared_state("pipeline_result_success", False)
            
            _set_shared_state("pipeline_should_transition_to_review", True)
            
        except Exception as e:
            _set_shared_state("pipeline_status", "failed")
            _set_shared_state("pipeline_error", str(e))
            _set_shared_state("pipeline_should_transition_to_review", True)
    
    thread = threading.Thread(target=run_pipeline_thread, daemon=True)
    thread.start()


def handle_stop_pipeline():
    """处理停止Pipeline"""
    state_proxy = st.session_state.state_proxy
    controller = st.session_state.pipeline_controller
    
    controller.stop_pipeline()
    state_proxy.update_pipeline_status(
        PipelineStatus.FAILED, "已停止", 1, "用户手动停止"
    )
    state_proxy.transition_to_mode(UIMode.REVIEW)


def handle_reset():
    """处理重置"""
    state_proxy = st.session_state.state_proxy
    controller = st.session_state.pipeline_controller
    
    state_proxy.transition_to_mode(UIMode.INPUT)
    state_proxy.clear_pipeline_logs()
    state_proxy.clear_pipeline_results()
    st.session_state["requirement_text"] = ""
    st.session_state["pipeline_logs"] = []
    st.session_state["pipeline_progress"] = 0
    st.session_state["pipeline_current_stage"] = ""


def main():
    """主函数：三态模态分发"""
    st.set_page_config(
        page_title="需求结构化分析管道",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_services()
    
    # 处理队列中的状态更新（主线程中执行，避免后台线程访问st.session_state警告
    _process_state_updates()
    
    state_proxy = st.session_state.state_proxy
    controller = st.session_state.pipeline_controller
    
    should_transition = _get_shared_state("pipeline_should_transition_to_review", False)
    if should_transition:
        pipeline_status = _get_shared_state("pipeline_status", "failed")
        if pipeline_status == "completed":
            state_proxy.update_pipeline_status(
                PipelineStatus.COMPLETED, "完成", 100, "Pipeline执行完成"
            )
            for stage, stage_result in controller.results.items():
                state_proxy.store_pipeline_result(stage, stage_result)
            if controller.current_run_id:
                st.session_state["current_project_id"] = controller.current_run_id
        else:
            error_msg = _get_shared_state("pipeline_error", "未知错误")
            state_proxy.update_pipeline_status(
                PipelineStatus.FAILED, "失败", 0, f"Pipeline执行失败: {error_msg}"
            )
        
        state_proxy.transition_to_mode(UIMode.REVIEW)
        _set_shared_state("pipeline_should_transition_to_review", False)
        st.rerun()
    
    if controller.status == ControllerStatus.RUNNING:
        if state_proxy.get_ui_mode() != UIMode.MONITOR:
            state_proxy.transition_to_mode(UIMode.MONITOR)
    elif controller.status in [ControllerStatus.IDLE, ControllerStatus.STOPPED]:
        if state_proxy.get_ui_mode() not in [UIMode.INPUT, UIMode.REVIEW]:
            if state_proxy.get_pipeline_status().get("status") == PipelineStatus.COMPLETED.value:
                state_proxy.transition_to_mode(UIMode.REVIEW)
            else:
                state_proxy.transition_to_mode(UIMode.INPUT)
    
    action = render_sidebar()
    
    if action == "start":
        handle_start_pipeline()
        st.rerun()
    elif action == "stop":
        handle_stop_pipeline()
        st.rerun()
    elif action == "reset":
        handle_reset()
        st.rerun()
    
    ui_mode = state_proxy.get_ui_mode()
    
    if ui_mode == UIMode.INPUT:
        render_intent_mode()
    elif ui_mode == UIMode.MONITOR:
        render_monitor_mode()
        
        time.sleep(1)
        st.rerun()
    elif ui_mode == UIMode.REVIEW:
        render_review_mode()


if __name__ == "__main__":
    main()

"""
模块职责：UI渲染函数模块
提供Streamlit UI组件渲染函数

v2.0 新增：
- render_stage_progress_bar(): 阶段进度条
- render_streaming_logs(): 流式日志展示
- render_review_tabs(): 审查模态Tab
"""

import os
import sys
import json
import streamlit as st

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../../..'))
sys.path.insert(0, project_root)

from modules.模块4_交互层模块.view_model_adapter import normalize_all_stage


def render_pipeline_status(status_data):
    """渲染Pipeline状态看板
    
    Args:
        status_data: 状态字典，包含 status, current_stage, progress, log_count
    """
    status_map = {
        "idle": ("🟢 空闲", "green"),
        "running": ("🔵 运行中", "blue"),
        "paused": ("🟡 已暂停", "orange"),
        "stopped": ("🔴 已停止", "red")
    }
    status_text, status_color = status_map.get(status_data.get("status", "idle"), ("⚪ 未知", "gray"))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("状态", status_text)
    with col2:
        st.metric("当前阶段", status_data.get("current_stage") or "-")
    with col3:
        st.metric("进度", f"{status_data.get('progress', 0)}%")
    with col4:
        st.metric("日志数", status_data.get("log_count", 0))
    
    st.progress(status_data.get("progress", 0) / 100)


def render_project_list(projects):
    """渲染项目列表（表格格式）
    
    Args:
        projects: 项目列表
    """
    if not projects:
        st.info("📭 暂无项目")
        return
    
    import pandas as pd
    df = pd.DataFrame(projects)
    df = df.rename(columns={
        "project_name": "项目名称",
        "project_id": "项目ID",
        "created_at": "创建时间",
        "updated_at": "更新时间"
    })
    st.dataframe(df, width='stretch')


def render_stage_result(stage_name: str, result_data: dict):
    """渲染单个阶段结果
    
    v2.0 重构：使用特征识别路由器替代 switch case
    v2.1 新增：使用 ViewModel Adapter 归一化数据
    
    Args:
        stage_name: 阶段名称
        result_data: 阶段结果字典
    """
    success = result_data.get("success", False)
    
    if not success:
        st.error(f"❌ {stage_name} - 执行失败")
        st.error(result_data.get("error", "未知错误"))
        return
    
    st.success(f"✅ {stage_name} - 执行成功")
    
    normalized_data = normalize_all_stage(stage_name, result_data)
    
    stage_renderers = {
        "requirement_anchoring": render_requirement_anchoring,
        "architecture_iteration": render_architecture_iteration,
        "contract_generation": render_contract_generation,
        "requirement_validation": render_requirement_validation,
        "landing_plan_generation": render_landing_plan,
        "visualization_generation": render_visualization_generation,
        "ide_bundle_generation": render_ide_bundle,
    }
    
    if stage_name in stage_renderers:
        stage_renderers[stage_name](normalized_data)
    else:
        features = detect_data_features(normalized_data)
        route_to_renderer(features, normalized_data, stage_name)


def render_dict_as_cards(data, title=None, level: int = 0):
    """将字典渲染为卡片列表
    
    支持嵌套数据的层级展示，使用缩进和颜色区分层级，
    对于深层嵌套数据自动使用折叠展示。
    
    Args:
        data: 字典数据
        title: 可选标题
        level: 当前层级深度，默认为0，用于控制缩进和颜色
    """
    if title:
        st.markdown(f"### {title}")
    
    if not isinstance(data, dict):
        st.json(data)
        return
    
    level_styles = [
        {"bg": "#E3F2FD", "border": "#1565C0", "icon": "🔹"},
        {"bg": "#E8F5E9", "border": "#2E7D32", "icon": "📗"},
        {"bg": "#FFF3E0", "border": "#EF6C00", "icon": "🔶"},
        {"bg": "#F3E5F5", "border": "#7B1FA2", "icon": "💜"},
        {"bg": "#ECEFF1", "border": "#455A64", "icon": "⚪"},
    ]
    
    style = level_styles[min(level, len(level_styles) - 1)]
    
    keys = list(data.keys())
    cols_per_row = 2 if level == 0 else 1
    
    for i in range(0, len(keys), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx >= len(keys):
                break
            key = keys[idx]
            value = data[key]
            with cols[j]:
                if level >= 2:
                    with st.expander(f"{style['icon']} {key}", expanded=False):
                        _render_nested_value(value, level + 1)
                else:
                    _render_card_item(key, value, style, level)


def _render_card_item(key: str, value, style: dict, level: int):
    """渲染单个卡片项
    
    Args:
        key: 键名
        value: 值
        style: 样式配置字典
        level: 当前层级
    """
    with st.container(border=True):
        header_html = f"""
        <div style="
            background-color: {style['bg']};
            border-left: 4px solid {style['border']};
            padding: 8px 12px;
            margin: -8px -8px 8px -8px;
            font-weight: bold;
            color: {style['border']};
        ">{style['icon']} {key}</div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        _render_nested_value(value, level + 1)


def _render_nested_value(value, level: int):
    """渲染嵌套值，递归处理字典和列表
    
    Args:
        value: 待渲染的值
        level: 当前层级深度
    """
    if isinstance(value, dict):
        if len(value) == 0:
            st.caption("空对象")
        elif len(value) <= 3 and level < 3:
            render_dict_as_cards(value, level=level)
        else:
            with st.expander(f"📋 嵌套对象 ({len(value)}项)", expanded=False):
                render_dict_as_cards(value, level=level)
    elif isinstance(value, list):
        if len(value) == 0:
            st.caption("空列表")
        elif value and isinstance(value[0], dict):
            with st.expander(f"📑 列表 ({len(value)}项)", expanded=False):
                for i, item in enumerate(value[:10]):
                    st.markdown(f"**项目 {i + 1}**")
                    if isinstance(item, dict):
                        render_dict_as_cards(item, level=level)
                    else:
                        st.write(item)
                if len(value) > 10:
                    st.caption(f"... 还有 {len(value) - 10} 项")
        else:
            list_str = ", ".join(str(v) for v in value[:5])
            if len(value) > 5:
                list_str += f" ... (共{len(value)}项)"
            st.text(list_str)
    elif isinstance(value, str):
        if len(value) > 100:
            with st.expander("查看完整内容", expanded=False):
                st.text(value)
        else:
            st.text(value)
    else:
        st.text(str(value))


def render_logs(logs, limit=100, level=None):
    """渲染日志面板
    
    Args:
        logs: 日志列表
        limit: 显示数量限制
        level: 日志级别过滤
    """
    if not logs:
        st.info("📭 暂无日志")
        return
    
    filtered_logs = logs
    if level:
        filtered_logs = [log for log in logs if log.get("level") == level]
    
    display_logs = filtered_logs[-limit:]
    
    log_text = ""
    for log in display_logs:
        level_str = log.get("level", "INFO")
        timestamp = log.get("timestamp", "")
        stage = log.get("stage", "")
        message = log.get("message", "")
        log_line = f"[{timestamp}] [{level_str}] {stage}: {message}\n"
        log_text += log_line
    
    st.text_area(
        label="日志面板",
        value=log_text,
        height=400,
        disabled=True,
        label_visibility='hidden'
    )


def render_run_record(run_data):
    """渲染运行记录详情
    
    Args:
        run_data: 运行记录数据
    """
    status_map = {
        "running": "🔄 运行中",
        "completed": "✅ 已完成",
        "failed": "❌ 失败",
        "stopped": "⏹️ 已停止"
    }
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("运行ID", run_data.get("run_id", "")[:20] + "...")
    with col2:
        st.metric("状态", status_map.get(run_data.get("status", "unknown"), "⚪ 未知"))
    with col3:
        st.metric("项目ID", run_data.get("project_id", "-"))
    with col4:
        st.metric("耗时", f"{run_data.get('duration_seconds', 0):.2f} 秒")
    
    st.markdown("### 📝 需求文本")
    st.text(run_data.get("requirement_text", "无"))
    
    results = run_data.get("results", {})
    if results:
        st.markdown("### 📋 阶段结果")
        for stage, result in results.items():
            success = result.get("success", False)
            status_icon = "✅" if success else "❌"
            with st.expander(f"{status_icon} {stage}", expanded=False):
                render_dict_as_cards(result)
    
    llm_calls = run_data.get("llm_calls", [])
    if llm_calls:
        st.markdown(f"### 🤖 LLM调用记录 ({len(llm_calls)} 次)")
        for i, call in enumerate(llm_calls, 1):
            success = call.get("success", False)
            status_icon = "✅" if success else "❌"
            with st.expander(f"{i}. {status_icon} {call.get('provider')} - {call.get('model')}", expanded=False):
                render_dict_as_cards(call)
    
    logs = run_data.get("logs", [])
    if logs:
        st.markdown(f"### 📝 运行日志 ({len(logs)} 条)")
        with st.expander("查看日志", expanded=False):
            render_logs(logs)


def render_download_button(data, filename, label="下载"):
    """渲染下载按钮
    
    Args:
        data: 数据（字典/列表/字符串/字节）
        filename: 文件名
        label: 按钮标签
    """
    content = None
    mime_type = "text/plain"
    
    if isinstance(data, (dict, list)):
        content = json.dumps(data, ensure_ascii=False, indent=2)
        mime_type = "application/json"
    elif isinstance(data, str):
        content = data
        if filename.endswith(".json"):
            mime_type = "application/json"
        elif filename.endswith(".md"):
            mime_type = "text/markdown"
    elif isinstance(data, bytes):
        content = data
        mime_type = "application/octet-stream"
    else:
        content = str(data)
    
    st.download_button(
        label=label,
        data=content,
        file_name=filename,
        mime=mime_type,
        key=f"download_btn_{filename}"
    )


def render_stage_progress_bar(stages, current_progress, current_stage):
    """渲染阶段进度条
    
    Args:
        stages: 阶段列表，格式为 [(阶段名, 起始进度), ...]
        current_progress: 当前进度(0-100)
        current_stage: 当前阶段名称
    """
    st.markdown("### 📊 执行进度")
    
    cols = st.columns(len(stages))
    
    for i, (stage_name, stage_progress) in enumerate(stages):
        with cols[i]:
            is_current = (stage_name == current_stage)
            is_completed = (current_progress >= stage_progress)
            
            if is_completed:
                status_icon = "✅"
                status_color = "green"
            elif is_current:
                status_icon = "🔵"
                status_color = "blue"
            else:
                status_icon = "⚪"
                status_color = "gray"
            
            st.markdown(
                f"<div style='text-align: center; padding: 10px; "
                f"border-radius: 8px; background-color: #f0f2f6;'>"
                f"<div style='font-size: 24px;'>{status_icon}</div>"
                f"<div style='font-size: 12px; font-weight: bold; "
                f"color: {status_color};'>{stage_name}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
    
    st.progress(current_progress / 100)
    st.caption(f"当前进度: {current_progress}% - {current_stage or '准备中'}")


def render_streaming_logs(logs, max_display=50):
    """渲染流式日志展示
    
    Args:
        logs: 日志列表
        max_display: 最大显示数量
    """
    if not logs:
        st.info("📭 等待日志输出...")
        return
    
    level_colors = {
        "INFO": "#2196F3",
        "SUCCESS": "#4CAF50",
        "WARNING": "#FF9800",
        "ERROR": "#F44336"
    }
    
    display_logs = logs[-max_display:]
    
    log_html = "<div style='font-family: monospace; font-size: 12px; "
    log_html += "background-color: #1e1e1e; color: #d4d4d4; "
    log_html += "padding: 15px; border-radius: 8px; height: 400px; "
    log_html += "overflow-y: auto;'>"
    
    for log in display_logs:
        level = log.get("level", "INFO")
        timestamp = log.get("timestamp", "")[-12:] if log.get("timestamp") else ""
        stage = log.get("stage", "")
        message = log.get("message", "")
        
        color = level_colors.get(level, "#d4d4d4")
        
        log_html += (
            f"<div style='margin-bottom: 4px;'>"
            f"<span style='color: #808080;'>{timestamp}</span> "
            f"<span style='color: {color}; font-weight: bold;'>[{level}]</span> "
            f"<span style='color: #ce9178;'>{stage}:</span> "
            f"<span>{message}</span>"
            f"</div>"
        )
    
    log_html += "</div>"
    
    st.markdown(log_html, unsafe_allow_html=True)


def render_colored_log(log_entry: dict):
    """渲染单条彩色日志
    
    根据 log_entry["level"] 显示不同颜色的日志条目：
    - INFO = 蓝色
    - SUCCESS = 绿色
    - WARNING = 黄色
    - ERROR = 红色
    
    Args:
        log_entry: 日志字典，包含 level, timestamp, stage, message 字段
    """
    level = log_entry.get("level", "INFO")
    timestamp = log_entry.get("timestamp", "")
    stage = log_entry.get("stage", "")
    message = log_entry.get("message", "")
    
    level_styles = {
        "INFO": {
            "color": "#2196F3",
            "bg_color": "#E3F2FD",
            "icon": "ℹ️",
            "st_method": "info"
        },
        "SUCCESS": {
            "color": "#4CAF50",
            "bg_color": "#E8F5E9",
            "icon": "✅",
            "st_method": "success"
        },
        "WARNING": {
            "color": "#FF9800",
            "bg_color": "#FFF3E0",
            "icon": "⚠️",
            "st_method": "warning"
        },
        "ERROR": {
            "color": "#F44336",
            "bg_color": "#FFEBEE",
            "icon": "❌",
            "st_method": "error"
        }
    }
    
    style = level_styles.get(level, level_styles["INFO"])
    
    stage_part = f"[{stage}] " if stage else ""
    formatted_msg = f"`[{timestamp}]` {stage_part}{message}"
    
    st.markdown(
        f"<div style='"
        f"font-family: monospace; font-size: 13px; "
        f"padding: 8px 12px; margin: 2px 0; "
        f"border-radius: 4px; "
        f"background-color: {style['bg_color']}; "
        f"border-left: 4px solid {style['color']};"
        f"'>"
        f"<span style='color: {style['color']}; font-weight: bold;'>"
        f"{style['icon']} [{level}]"
        f"</span> "
        f"<span style='color: #666;'>[{timestamp}]</span> "
        f"<span style='color: #888;'>[{stage}]</span> "
        f"<span style='color: #333;'>{message}</span>"
        f"</div>",
        unsafe_allow_html=True
    )


def render_colored_logs_batch(log_entries: list):
    """批量渲染彩色日志列表
    
    Args:
        log_entries: 日志字典列表
    """
    if not log_entries:
        st.info("📭 暂无日志")
        return
    
    level_colors = {
        "INFO": "#2196F3",
        "SUCCESS": "#4CAF50",
        "WARNING": "#FF9800",
        "ERROR": "#F44336"
    }
    
    level_bg_colors = {
        "INFO": "#E3F2FD",
        "SUCCESS": "#E8F5E9",
        "WARNING": "#FFF3E0",
        "ERROR": "#FFEBEE"
    }
    
    level_icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌"
    }
    
    log_html = "<div style='font-family: monospace; font-size: 12px;'>"
    
    for log in log_entries:
        level = log.get("level", "INFO")
        timestamp = log.get("timestamp", "")
        stage = log.get("stage", "")
        message = log.get("message", "")
        
        color = level_colors.get(level, "#2196F3")
        bg_color = level_bg_colors.get(level, "#E3F2FD")
        icon = level_icons.get(level, "ℹ️")
        
        log_html += (
            f"<div style='"
            f"padding: 6px 10px; margin: 2px 0; "
            f"border-radius: 4px; "
            f"background-color: {bg_color}; "
            f"border-left: 3px solid {color};"
            f"'>"
            f"<span style='color: {color}; font-weight: bold;'>{icon} [{level}]</span> "
            f"<span style='color: #666;'>[{timestamp}]</span> "
            f"<span style='color: #888;'>[{stage}]</span> "
            f"<span style='color: #333;'>{message}</span>"
            f"</div>"
        )
    
    log_html += "</div>"
    st.markdown(log_html, unsafe_allow_html=True)


def render_export_buttons(stage_name: str, result: dict):
    """渲染一键导出按钮组
    
    为阶段结果提供JSON和Markdown两种导出格式，使用Popover组件
    收纳导出按钮，避免界面拥挤。
    
    Args:
        stage_name: 阶段名称，用于生成文件名
        result: 阶段结果数据
    """
    with st.popover("📤 导出", width="stretch"):
        col1, col2 = st.columns(2)
        
        with col1:
            json_data = json.dumps(result, ensure_ascii=False, indent=2)
            st.download_button(
                label="📄 JSON",
                data=json_data,
                file_name=f"{stage_name}.json",
                mime="application/json",
                key=f"export_json_{stage_name}_{id(result)}"
            )
        
        with col2:
            if isinstance(result, dict):
                md_content = dict_to_markdown_table(result)
            else:
                md_content = f"```\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"
            st.download_button(
                label="📝 Markdown",
                data=md_content,
                file_name=f"{stage_name}.md",
                mime="text/markdown",
                key=f"export_md_{stage_name}_{id(result)}"
            )


def render_review_tabs(results: dict, metadata: dict = None):
    """渲染审查模态的Tab页
    
    v2.0 重构：
    - 添加顶部元数据徽章区域
    - 为每个Tab添加一键导出按钮
    - 统一底部原始数据收纳区
    
    Args:
        results: Pipeline执行结果字典
        metadata: 可选的元数据字典，包含 model, duration, tokens 等
    """
    if metadata:
        render_metadata_badges(metadata)
        st.markdown("---")
    
    tab_mapping = [
        ("requirement_anchoring", "📝 需求锚定"),
        ("requirement_validation", "✅ 需求校验"),
        ("architecture_iteration", "🏗️ 架构迭代"),
        ("contract_generation", "📜 契约生成"),
        ("landing_plan_generation", "📋 落地方案"),
        ("visualization_generation", "📊 可视化汇报"),
        ("ide_bundle_generation", "📦 IDE引导包"),
    ]
    
    tab_names = []
    tab_contents = []
    for stage_key, tab_label in tab_mapping:
        if stage_key in results:
            tab_names.append(tab_label)
            tab_contents.append((stage_key, results[stage_key]))
    
    if not tab_names:
        st.warning("暂无可展示的结果")
        return
    
    tabs = st.tabs(tab_names)
    
    for i, (stage_name, result) in enumerate(tab_contents):
        with tabs[i]:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{tab_names[i]}** 阶段成果")
            with col2:
                render_export_buttons(stage_name, result)
            
            st.markdown("---")
            
            render_stage_result(stage_name, result)
    
    st.markdown("---")
    with st.expander("🗂️ 全部原始数据 (JSON)", expanded=False):
        st.code(json.dumps(results, ensure_ascii=False, indent=2), language="json")


def render_progress_bar(current_stage: str, progress: float, total_stages: int = 6):
    """渲染进度条组件
    
    Args:
        current_stage: 当前阶段名称
        progress: 当前进度 (0.0-1.0)
        total_stages: 总阶段数，默认为6
    """
    progress_percent = int(progress * 100)
    current_stage_num = int(progress * total_stages) + 1
    current_stage_num = min(current_stage_num, total_stages)
    
    st.markdown(f"**{current_stage}**")
    
    progress_bar = st.progress(progress)
    
    st.caption(f"阶段 {current_stage_num}/{total_stages} | 进度 {progress_percent}%")


def render_footer_summary(duration_seconds: float, metrics: dict):
    """渲染Footer摘要组件
    
    使用现代卡片样式展示执行摘要信息，包括耗时、Token使用量和模型信息。
    采用多列布局和图标颜色区分，提供清晰的视觉层次。
    
    Args:
        duration_seconds: 总耗时（秒）
        metrics: 指标字典，包含 token 和 model 信息
    """
    total_tokens = metrics.get("total_tokens", 0)
    input_tokens = metrics.get("input_tokens", 0)
    output_tokens = metrics.get("output_tokens", 0)
    models = metrics.get("models", [])
    
    def format_tokens(tokens):
        if tokens >= 1000:
            return f"{tokens / 1000:.1f}k"
        return str(tokens)
    
    def format_duration(seconds):
        if seconds >= 60:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        return f"{seconds:.1f}s"
    
    total_str = format_tokens(total_tokens)
    input_str = format_tokens(input_tokens)
    output_str = format_tokens(output_tokens)
    models_str = ", ".join(models) if models else "-"
    
    st.markdown("---")
    
    header_html = """
    <div style="
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 15px;
    ">
        <span style="font-size: 18px;">📊</span>
        <span style="font-size: 16px; font-weight: bold; color: #333;">执行摘要</span>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        card_html = f"""
        <div style="
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            border-radius: 12px;
            padding: 16px;
            border-left: 4px solid #1976D2;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 12px; color: #1565C0; margin-bottom: 4px;">⏱️ 总耗时</div>
            <div style="font-size: 24px; font-weight: bold; color: #0D47A1;">{format_duration(duration_seconds)}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
    
    with col2:
        card_html = f"""
        <div style="
            background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
            border-radius: 12px;
            padding: 16px;
            border-left: 4px solid #388E3C;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 12px; color: #2E7D32; margin-bottom: 4px;">📊 Token用量</div>
            <div style="font-size: 24px; font-weight: bold; color: #1B5E20;">{total_str}</div>
            <div style="font-size: 11px; color: #558B2F; margin-top: 4px;">
                📥 {input_str} | 📤 {output_str}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
    
    with col3:
        card_html = f"""
        <div style="
            background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
            border-radius: 12px;
            padding: 16px;
            border-left: 4px solid #F57C00;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 12px; color: #E65100; margin-bottom: 4px;">🤖 使用模型</div>
            <div style="font-size: 14px; font-weight: bold; color: #BF360C; word-break: break-all;">
                {models_str}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)


def render_l1_metrics(metrics: dict):
    """渲染关键指标行
    
    使用多列布局展示核心业务指标，每列使用st.metric组件展示单个指标。
    适用于Pipeline执行概览、项目统计等场景。
    
    Args:
        metrics: 指标字典，格式为 {
            "识别实体数": {"value": 42, "delta": "+5"},
            "接口总数": {"value": 128, "delta": None},
            "风险点计数": {"value": 3, "delta": "-2"}
        }
        每个指标的value为必需，delta为可选（用于显示变化趋势）
    
    Example:
        >>> metrics = {
        ...     "识别实体数": {"value": 42, "delta": "+5"},
        ...     "接口总数": {"value": 128},
        ...     "风险点计数": {"value": 3, "delta": "-2", "delta_color": "normal"}
        ... }
        >>> render_l1_metrics(metrics)
    """
    if not metrics:
        st.info("📊 暂无指标数据")
        return
    
    metric_keys = list(metrics.keys())
    num_cols = len(metric_keys)
    cols = st.columns(num_cols)
    
    for i, key in enumerate(metric_keys):
        metric_data = metrics[key]
        value = metric_data.get("value", "-")
        delta = metric_data.get("delta")
        delta_color = metric_data.get("delta_color", "normal")
        
        with cols[i]:
            st.metric(
                label=key,
                value=value,
                delta=delta,
                delta_color=delta_color
            )


def render_l3_raw_stub(data: dict, title: str = "原始契约溯源"):
    """统一的原始数据收纳器
    
    使用折叠区域展示原始JSON数据，适用于契约溯源、调试信息、
    原始响应展示等场景。默认折叠以减少视觉干扰。
    
    Args:
        data: 原始数据字典，将被序列化为JSON展示
        title: 折叠区域标题，默认为"原始契约溯源"
    
    Example:
        >>> raw_contract = {
        ...     "interface": {"name": "UserService", "methods": [...]},
        ...     "data": {"schema": {...}}
        ... }
        >>> render_l3_raw_stub(raw_contract, "接口契约原始数据")
    """
    with st.expander(f"🛠️ {title} (JSON/YAML)", expanded=False):
        if not data:
            st.info("暂无数据")
            return
        
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        st.code(json_str, language='json')


def render_metadata_badges(metadata: dict):
    """元数据徽章组件
    
    以徽章形式展示LLM调用元数据，包括模型名称、耗时、Token数量等。
    支持单模型和多模型列表展示，使用HTML渲染徽章样式。
    
    Args:
        metadata: 元数据字典，格式为 {
            "model": "DeepSeek-V3" 或 ["DeepSeek-V3", "GPT-4"],
            "duration": 12.5,
            "tokens": 4500,
            "input_tokens": 3000,
            "output_tokens": 1500
        }
        - model: 模型名称（字符串或列表）
        - duration: 耗时（秒）
        - tokens: 总Token数
        - input_tokens: 输入Token数（可选）
        - output_tokens: 输出Token数（可选）
    
    Example:
        >>> metadata = {
        ...     "model": ["DeepSeek-V3", "GPT-4"],
        ...     "duration": 12.5,
        ...     "tokens": 4500,
        ...     "input_tokens": 3000,
        ...     "output_tokens": 1500
        ... }
        >>> render_metadata_badges(metadata)
    """
    if not metadata:
        return
    
    model = metadata.get("model", "-")
    duration = metadata.get("duration", 0)
    tokens = metadata.get("tokens", 0)
    input_tokens = metadata.get("input_tokens")
    output_tokens = metadata.get("output_tokens")
    
    def format_number(num):
        if num >= 1000:
            return f"{num / 1000:.1f}k"
        return str(num)
    
    if isinstance(model, list):
        model_str = " | ".join(model)
    else:
        model_str = str(model)
    
    duration_str = f"{duration:.1f}s" if isinstance(duration, (int, float)) else str(duration)
    tokens_str = format_number(tokens) if isinstance(tokens, (int, float)) else str(tokens)
    
    badges_html = f"""
    <div style="
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding: 10px 0;
        margin-bottom: 10px;
    ">
        <span style="
            background-color: #E3F2FD;
            color: #1565C0;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 500;
        ">🤖 Model: {model_str}</span>
        
        <span style="
            background-color: #E8F5E9;
            color: #2E7D32;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 500;
        ">⏱️ Duration: {duration_str}</span>
        
        <span style="
            background-color: #FFF3E0;
            color: #EF6C00;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 500;
        ">📊 Tokens: {tokens_str}</span>
    """
    
    if input_tokens is not None and output_tokens is not None:
        input_str = format_number(input_tokens)
        output_str = format_number(output_tokens)
        badges_html += f"""
        <span style="
            background-color: #F3E5F5;
            color: #7B1FA2;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 500;
        ">📥 Input: {input_str} | 📤 Output: {output_str}</span>
        """
    
    badges_html += "</div>"
    
    st.markdown(badges_html, unsafe_allow_html=True)


def detect_data_features(data: dict) -> list[str]:
    """数据特征检测函数
    
    检测数据结构中的特征标记，用于智能路由到对应的渲染函数。
    特征检测按优先级顺序进行，返回的特征列表按优先级排序。
    
    特征类型说明：
    - "flow": 数据包含流程相关字段（flow、flows、entities、business_flow）
    - "interfaces": 数据包含接口相关字段（interfaces、api、endpoints、api_list）
    - "schema": 数据包含数据结构字段（schema、properties、fields、data_schema）
    - "markdown": 数据包含Markdown内容字段或值为Markdown格式字符串
    - "solutions": 数据包含方案相关字段（solutions、individual_solutions、paradigms）
    - "contracts": 数据包含契约相关字段（contracts、interface_stub、data_contract）
    
    Args:
        data: 待检测的数据字典
    
    Returns:
        list[str]: 检测到的特征列表，按优先级排序（solutions > flow > interfaces > schema > markdown > contracts）
    
    Example:
        >>> data = {"flows": [...], "entities": [...]}
        >>> detect_data_features(data)
        ['flow']
        
        >>> data = {"solutions": [...], "interfaces": [...]}
        >>> detect_data_features(data)
        ['solutions', 'interfaces']
    """
    if not isinstance(data, dict):
        return []
    
    features = []
    
    flow_keys = {"flow", "flows", "entities", "business_flow"}
    interfaces_keys = {"interfaces", "api", "endpoints", "api_list"}
    schema_keys = {"schema", "properties", "fields", "data_schema"}
    solutions_keys = {"solutions", "individual_solutions", "paradigms"}
    contracts_keys = {"contracts", "interface_stub", "data_contract"}
    
    data_keys = set(data.keys())
    
    if data_keys & solutions_keys:
        features.append("solutions")
    if data_keys & flow_keys:
        features.append("flow")
    if data_keys & interfaces_keys:
        features.append("interfaces")
    if data_keys & schema_keys:
        features.append("schema")
    
    if "markdown_content" in data_keys:
        features.append("markdown")
    else:
        for key, value in data.items():
            if isinstance(value, str):
                if value.strip().startswith("#") or "```" in value:
                    features.append("markdown")
                    break
    
    if data_keys & contracts_keys:
        features.append("contracts")
    
    return features


def route_to_renderer(features: list, data: dict, stage_name: str = ""):
    """特征路由分发器
    
    根据特征列表调用对应的渲染函数，实现智能化的数据展示。
    渲染优先级：solutions > flow > interfaces > schema > markdown > contracts。
    如果没有匹配特征，使用默认的render_dict_as_cards进行渲染。
    每次渲染后调用render_l3_raw_stub收纳原始数据。
    
    Args:
        features: 特征列表，由detect_data_features函数返回
        data: 待渲染的数据字典
        stage_name: 阶段名称，用于展示标题，可选
    
    Example:
        >>> features = ["solutions", "interfaces"]
        >>> data = {"solutions": [...], "interfaces": [...]}
        >>> route_to_renderer(features, data, "架构设计阶段")
    """
    if stage_name:
        st.markdown(f"### {stage_name}")
    
    if not features:
        render_dict_as_cards(data)
        render_l3_raw_stub(data)
        return
    
    priority_order = ["solutions", "flow", "interfaces", "schema", "markdown", "contracts"]
    
    rendered = False
    for feature in priority_order:
        if feature in features:
            if feature == "solutions":
                _render_solutions(data)
            elif feature == "flow":
                _render_flow(data)
            elif feature == "interfaces":
                _render_interfaces(data)
            elif feature == "schema":
                _render_schema(data)
            elif feature == "markdown":
                _render_markdown(data)
            elif feature == "contracts":
                _render_contracts(data)
            
            rendered = True
            break
    
    if not rendered:
        render_dict_as_cards(data)
    
    render_l3_raw_stub(data)


def _render_solutions(data: dict):
    """渲染方案数据
    
    Args:
        data: 包含方案数据的字典
    """
    solutions = None
    for key in ["solutions", "individual_solutions", "paradigms"]:
        if key in data:
            solutions = data[key]
            break
    
    if not solutions:
        render_dict_as_cards(data)
        return
    
    if isinstance(solutions, list):
        for i, sol in enumerate(solutions, 1):
            with st.expander(f"📋 方案 {i}", expanded=(i == 1)):
                if isinstance(sol, dict):
                    render_dict_as_cards(sol)
                else:
                    st.write(sol)
    else:
        render_dict_as_cards(data)


def _render_flow(data: dict):
    """渲染流程数据
    
    Args:
        data: 包含流程数据的字典
    """
    flows = None
    for key in ["flow", "flows", "business_flow"]:
        if key in data:
            flows = data[key]
            break
    
    entities = data.get("entities", [])
    
    if entities:
        with st.expander("📊 实体列表", expanded=True):
            if isinstance(entities, list):
                for entity in entities:
                    if isinstance(entity, dict):
                        st.markdown(f"- **{entity.get('name', entity.get('id', '未知'))}**")
                    else:
                        st.markdown(f"- {entity}")
            else:
                st.json(entities)
    
    if flows:
        with st.expander("🔄 流程定义", expanded=True):
            if isinstance(flows, list):
                for flow in flows:
                    if isinstance(flow, dict):
                        flow_name = flow.get("name", flow.get("id", "未命名流程"))
                        st.markdown(f"**{flow_name}**")
                        if "steps" in flow:
                            for step in flow["steps"]:
                                step_name = step.get("name", step.get("action", "步骤"))
                                st.markdown(f"  → {step_name}")
                    else:
                        st.write(flow)
            else:
                st.json(flows)


def _render_interfaces(data: dict):
    """渲染接口数据
    
    Args:
        data: 包含接口数据的字典
    """
    interfaces = None
    for key in ["interfaces", "api", "endpoints", "api_list"]:
        if key in data:
            interfaces = data[key]
            break
    
    if not interfaces:
        render_dict_as_cards(data)
        return
    
    if isinstance(interfaces, list):
        for i, api in enumerate(interfaces, 1):
            if isinstance(api, dict):
                name = api.get("name", api.get("path", api.get("endpoint", f"接口{i}")))
                method = api.get("method", "GET")
                with st.expander(f"🔌 {method} {name}", expanded=False):
                    render_dict_as_cards(api)
            else:
                with st.expander(f"🔌 接口 {i}", expanded=False):
                    st.write(api)
    else:
        render_dict_as_cards(data)


def _render_schema(data: dict):
    """渲染数据结构
    
    Args:
        data: 包含数据结构的字典
    """
    schema = None
    for key in ["schema", "properties", "fields", "data_schema"]:
        if key in data:
            schema = data[key]
            break
    
    if not schema:
        render_dict_as_cards(data)
        return
    
    if isinstance(schema, dict):
        with st.expander("📐 数据结构", expanded=True):
            st.json(schema)
    elif isinstance(schema, list):
        with st.expander("📐 字段列表", expanded=True):
            for field in schema:
                if isinstance(field, dict):
                    field_name = field.get("name", field.get("field", "未知字段"))
                    field_type = field.get("type", "unknown")
                    st.markdown(f"- **{field_name}** ({field_type})")
                else:
                    st.markdown(f"- {field}")
    else:
        render_dict_as_cards(data)


def _render_markdown(data: dict):
    """渲染Markdown内容
    
    Args:
        data: 包含Markdown内容的字典
    """
    content = data.get("markdown_content")
    
    if not content:
        for key, value in data.items():
            if isinstance(value, str):
                if value.strip().startswith("#") or "```" in value:
                    content = value
                    break
    
    if content:
        st.markdown(content)
    else:
        render_dict_as_cards(data)


def _render_contracts(data: dict):
    """渲染契约数据
    
    Args:
        data: 包含契约数据的字典
    """
    contracts = None
    for key in ["contracts", "interface_stub", "data_contract"]:
        if key in data:
            contracts = data[key]
            break
    
    if not contracts:
        render_dict_as_cards(data)
        return
    
    if isinstance(contracts, dict):
        for contract_type, contract_data in contracts.items():
            with st.expander(f"📜 {contract_type}", expanded=False):
                if isinstance(contract_data, str):
                    st.code(contract_data, language="yaml")
                else:
                    st.json(contract_data)
    else:
        render_dict_as_cards(data)


def dict_to_markdown_table(data: dict, level: int = 0) -> str:
    """字典转Markdown表格
    
    将字典数据转换为Markdown表格格式，支持嵌套字典的递归处理。
    使用缩进表示层级关系，适用于生成文档、报告导出等场景。
    
    Args:
        data: 待转换的字典数据
        level: 当前层级深度，用于控制缩进，默认为0
    
    Returns:
        str: Markdown格式的表格字符串
    
    Example:
        >>> data = {"name": "用户服务", "version": "1.0", "config": {"debug": True}}
        >>> print(dict_to_markdown_table(data))
        | 键 | 值 |
        |---|---|
        | name | 用户服务 |
        | version | 1.0 |
        | config | (嵌套对象) |
          | 键 | 值 |
          |---|---|
          | debug | True |
    """
    if not isinstance(data, dict):
        return str(data)
    
    indent = "  " * level
    lines = []
    
    if level == 0:
        lines.append(f"{indent}| 键 | 值 |")
        lines.append(f"{indent}|---|---|")
    else:
        lines.append(f"{indent}| 键 | 值 |")
        lines.append(f"{indent}|---|---|")
    
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{indent}| {key} | (嵌套对象) |")
            nested_table = dict_to_markdown_table(value, level + 1)
            lines.append(nested_table)
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                lines.append(f"{indent}| {key} | (列表，{len(value)}项) |")
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        lines.append(f"{indent}  **项目 {i+1}:**")
                        nested_table = dict_to_markdown_table(item, level + 1)
                        lines.append(nested_table)
            else:
                list_str = ", ".join(str(v) for v in value[:5])
                if len(value) > 5:
                    list_str += f" ... (共{len(value)}项)"
                lines.append(f"{indent}| {key} | [{list_str}] |")
        elif isinstance(value, str) and (value.strip().startswith("#") or "```" in value):
            lines.append(f"{indent}| {key} | (Markdown内容) |")
            lines.append(f"{indent}```")
            lines.append(f"{indent}{value}")
            lines.append(f"{indent}```")
        else:
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:100] + "..."
            lines.append(f"{indent}| {key} | {value_str} |")
    
    return "\n".join(lines)


def render_requirement_anchoring(data: dict):
    """需求锚定阶段专属渲染器
    
    渲染需求锚定阶段的完整结果展示，采用分层布局：
    - L1层：关键指标行（实体数、流程数、属性数等）
    - L2层：左右两栏布局（业务逻辑摘要 + Mermaid流程图）
    - L3层：领域对象表格
    - L4层：原始数据收纳
    
    Args:
        data: 需求锚定结果字典，格式为 {
            "entities": [...],           # 领域实体列表
            "flows": [...],              # 业务流程列表
            "attributes": [...],         # 属性列表
            "business_logic_summary": str, # 业务逻辑摘要
            "metrics": {                 # 指标统计
                "entity_count": int,
                "flow_count": int,
                "attribute_count": int,
                ...
            },
            "raw_data": dict             # 原始数据
        }
    
    Example:
        >>> data = {
        ...     "entities": [{"name": "用户", "attributes": ["id", "name"]}],
        ...     "flows": [{"name": "注册流程", "steps": [...]}],
        ...     "metrics": {"entity_count": 5, "flow_count": 3}
        ... }
        >>> render_requirement_anchoring(data)
    """
    if not data:
        st.warning("📭 暂无需求锚定数据")
        return
    
    metrics = extract_requirement_anchoring_metrics(data)
    entities = data.get("entities", [])
    flows = data.get("flows", [])
    business_logic_summary = data.get("business_logic_summary", "")
    
    render_l1_metrics(metrics)
    
    st.markdown("---")
    
    st.markdown("### 📋 核心业务逻辑")
    if business_logic_summary:
        st.info(business_logic_summary)
    else:
        st.info("暂无业务逻辑摘要，请查看下方实体表格获取详细信息。")
    
    st.markdown("---")
    
    st.markdown("### 📊 领域对象")
    render_domain_objects_table(entities)
    
    render_l3_raw_stub(data, "需求锚定原始数据")


def render_business_flow_mermaid(flows: list, entities: list = None):
    """Mermaid流程图生成器
    
    根据业务流程和实体数据生成Mermaid flowchart语法，并使用Streamlit原生支持渲染。
    支持多流程展示，自动处理节点ID冲突，提供友好的空数据提示。
    
    Mermaid语法说明：
    - 使用flowchart TD（自上而下）布局
    - 实体节点使用圆角矩形
    - 流程步骤使用普通矩形
    - 决策节点使用菱形
    
    Args:
        flows: 业务流程列表，每个流程格式为 {
            "name": str,           # 流程名称
            "id": str,             # 流程ID（可选）
            "steps": [             # 流程步骤列表
                {
                    "id": str,      # 步骤ID
                    "name": str,    # 步骤名称
                    "type": str,    # 步骤类型：action/decision/start/end
                    "next": str     # 下一步骤ID（可选）
                }
            ]
        }
        entities: 领域实体列表（可选），用于在流程图中标注涉及的实体
    
    Example:
        >>> flows = [
        ...     {
        ...         "name": "用户注册流程",
        ...         "steps": [
        ...             {"id": "start", "name": "开始", "type": "start"},
        ...             {"id": "input", "name": "输入信息", "type": "action"},
        ...             {"id": "end", "name": "注册成功", "type": "end"}
        ...         ]
        ...     }
        ... ]
        >>> render_business_flow_mermaid(flows)
    """
    if not flows:
        st.info("📭 暂无流程数据，无法生成流程图")
        return
    
    if not isinstance(flows, list):
        flows = [flows]
    
    mermaid_lines = ["flowchart TD"]
    
    entity_nodes = set()
    if entities and isinstance(entities, list):
        for entity in entities:
            if isinstance(entity, dict):
                entity_name = entity.get("name", entity.get("id", ""))
                if entity_name:
                    entity_id = f"entity_{entity_name}".replace(" ", "_").replace("-", "_")
                    mermaid_lines.append(f"    {entity_id}[(\"{entity_name}\")]:::entityStyle")
                    entity_nodes.add(entity_id)
    
    if entity_nodes:
        mermaid_lines.append("    subgraph Entities[领域实体]")
        for entity_id in entity_nodes:
            mermaid_lines.append(f"        {entity_id}")
        mermaid_lines.append("    end")
    
    for flow_idx, flow in enumerate(flows):
        if not isinstance(flow, dict):
            continue
        
        flow_name = flow.get("name", flow.get("id", f"流程{flow_idx + 1}"))
        steps = flow.get("steps", [])
        
        if not steps:
            continue
        
        subgraph_id = f"flow_{flow_idx}"
        mermaid_lines.append(f"    subgraph {subgraph_id}[{flow_name}]")
        
        for step in steps:
            if not isinstance(step, dict):
                continue
            
            step_id = step.get("id", f"step_{flow_idx}_{id(step)}")
            step_name = step.get("name", "未命名步骤")
            step_type = step.get("type", "action")
            
            safe_id = f"{subgraph_id}_{step_id}".replace(" ", "_").replace("-", "_")
            
            if step_type == "start":
                mermaid_lines.append(f"        {safe_id}((\"{step_name}\")):::startStyle")
            elif step_type == "end":
                mermaid_lines.append(f"        {safe_id}(((\"{step_name}\"))):::endStyle")
            elif step_type == "decision":
                mermaid_lines.append(f"        {safe_id}{{\"{step_name}\"}}:::decisionStyle")
            else:
                mermaid_lines.append(f"        {safe_id}[\"{step_name}\"]")
        
        prev_step_id = None
        for step in steps:
            if not isinstance(step, dict):
                continue
            
            step_id = step.get("id", f"step_{flow_idx}_{id(step)}")
            safe_id = f"{subgraph_id}_{step_id}".replace(" ", "_").replace("-", "_")
            
            if prev_step_id:
                mermaid_lines.append(f"        {prev_step_id} --> {safe_id}")
            
            next_id = step.get("next")
            if next_id:
                next_safe_id = f"{subgraph_id}_{next_id}".replace(" ", "_").replace("-", "_")
                mermaid_lines.append(f"        {safe_id} --> {next_safe_id}")
                prev_step_id = None
            else:
                prev_step_id = safe_id
        
        mermaid_lines.append("    end")
    
    mermaid_lines.append("    classDef entityStyle fill:#E3F2FD,stroke:#1565C0,stroke-width:2px")
    mermaid_lines.append("    classDef startStyle fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px")
    mermaid_lines.append("    classDef endStyle fill:#FFEBEE,stroke:#C62828,stroke-width:2px")
    mermaid_lines.append("    classDef decisionStyle fill:#FFF3E0,stroke:#EF6C00,stroke-width:2px")
    
    mermaid_code = "\n".join(mermaid_lines)
    
    try:
        if STREAMLIT_MERMAID_AVAILABLE:
            try:
                st_mermaid(mermaid_code, height=400)
                return
            except Exception:
                pass
    except Exception:
        pass
    
    st.markdown(f"```mermaid\n{mermaid_code}\n```")


def render_domain_objects_table(entities: list):
    """领域对象表格渲染器
    
    使用Streamlit dataframe或Markdown表格展示领域对象信息，支持嵌套属性的展示。
    表格列包括：对象名称、核心属性、描述。对于复杂的嵌套属性，使用折叠展示。
    
    Args:
        entities: 领域实体列表，每个实体格式为 {
            "name": str,           # 实体名称
            "id": str,             # 实体ID（可选）
            "description": str,    # 实体描述（可选）
            "attributes": [        # 属性列表
                {
                    "name": str,    # 属性名
                    "type": str,    # 属性类型
                    "required": bool, # 是否必需
                    "description": str # 属性描述
                }
            ],
            "properties": dict     # 属性字典（替代attributes）
        }
    
    Example:
        >>> entities = [
        ...     {
        ...         "name": "用户",
        ...         "description": "系统用户实体",
        ...         "attributes": [
        ...             {"name": "id", "type": "string", "required": True},
        ...             {"name": "name", "type": "string", "required": True}
        ...         ]
        ...     }
        ... ]
        >>> render_domain_objects_table(entities)
    """
    if not entities:
        st.info("📭 暂无领域对象数据")
        return
    
    if not isinstance(entities, list):
        entities = [entities]
    
    valid_entities = [e for e in entities if isinstance(e, dict)]
    
    if not valid_entities:
        st.warning("⚠️ 领域对象数据格式不正确")
        st.json(entities)
        return
    
    for idx, entity in enumerate(valid_entities):
        entity_name = entity.get("name", entity.get("id", f"实体{idx + 1}"))
        entity_desc = entity.get("description", "暂无描述")
        attributes = entity.get("attributes", entity.get("properties", []))
        
        with st.container(border=True):
            col_name, col_desc = st.columns([1, 2])
            
            with col_name:
                st.markdown(f"**🎯 {entity_name}**")
            
            with col_desc:
                st.markdown(f"*{entity_desc}*")
            
            if attributes:
                with st.expander("📝 查看属性详情", expanded=False):
                    if isinstance(attributes, list):
                        attr_data = []
                        for attr in attributes:
                            if isinstance(attr, dict):
                                attr_name = attr.get("name", attr.get("field", "-"))
                                attr_type = attr.get("type", "unknown")
                                attr_required = "✓" if attr.get("required", False) else ""
                                attr_desc = attr.get("description", "-")
                                attr_data.append({
                                    "属性名": attr_name,
                                    "类型": attr_type,
                                    "必填": attr_required,
                                    "说明": attr_desc
                                })
                            else:
                                attr_data.append({
                                    "属性名": str(attr),
                                    "类型": "-",
                                    "必填": "-",
                                    "说明": "-"
                                })
                        
                        if attr_data:
                            import pandas as pd
                            df = pd.DataFrame(attr_data)
                            st.dataframe(df, width="stretch", hide_index=True)
                        else:
                            st.info("暂无属性详情")
                    
                    elif isinstance(attributes, dict):
                        for attr_name, attr_info in attributes.items():
                            if isinstance(attr_info, dict):
                                attr_type = attr_info.get("type", "unknown")
                                attr_desc = attr_info.get("description", "-")
                                st.markdown(f"- **{attr_name}** ({attr_type}): {attr_desc}")
                            else:
                                st.markdown(f"- **{attr_name}**: {attr_info}")
                    else:
                        st.json(attributes)
            else:
                st.caption("💡 候选属性（未绑定实体）")
                if attributes and isinstance(attributes, list):
                    for attr in attributes[:5]:
                        if isinstance(attr, dict):
                            attr_name = attr.get("name", attr.get("field", "-"))
                            attr_type = attr.get("type", "unknown")
                            st.markdown(f"- {attr_name} ({attr_type})")
                        else:
                            st.markdown(f"- {str(attr)}")
                    if len(attributes) > 5:
                        st.caption(f"... 还有 {len(attributes) - 5} 个属性")


def render_requirement_validation(data: dict):
    """需求校验渲染器
    
    渲染需求校验阶段的结果，包括关键指标、校验结果分类展示和原始数据收纳。
    按照校验结果类型（通过/警告/错误）分别使用不同的视觉样式展示。
    
    展示结构：
    1. L1指标行：校验通过项数、警告数、错误数
    2. 通过项：使用st.success展示绿色成功提示
    3. 警告项：使用st.warning展示黄色警告提示
    4. 错误项：使用st.error展示红色错误提示
    5. L3原始数据：折叠收纳原始JSON数据
    
    Args:
        data: 需求校验结果字典，格式为 {
            "passed": [{"item": "字段名", "message": "校验通过"}],
            "warnings": [{"item": "字段名", "message": "警告信息"}],
            "errors": [{"item": "字段名", "message": "错误信息"}],
            "summary": {"total": 10, "passed": 8, "warnings": 1, "errors": 1}
        }
        - passed: 通过的校验项列表
        - warnings: 警告项列表
        - errors: 错误项列表
        - summary: 汇总统计（可选）
    
    Example:
        >>> validation_data = {
        ...     "passed": [{"item": "需求标题", "message": "格式正确"}],
        ...     "warnings": [{"item": "功能描述", "message": "描述过于简短"}],
        ...     "errors": [{"item": "接口定义", "message": "缺少必要字段"}],
        ...     "summary": {"total": 3, "passed": 1, "warnings": 1, "errors": 1}
        ... }
        >>> render_requirement_validation(validation_data)
    """
    st.markdown("### ✅ 需求校验结果")
    
    metrics = extract_requirement_validation_metrics(data)
    render_l1_metrics(metrics)
    
    passed_items = data.get("passed", [])
    warnings = data.get("warnings", [])
    errors = data.get("errors", [])
    
    st.markdown("---")
    
    if passed_items:
        with st.expander(f"✅ 通过项 ({len(passed_items)})", expanded=True):
            for item in passed_items:
                if isinstance(item, dict):
                    item_name = item.get("item", "未知项")
                    message = item.get("message", "")
                    st.success(f"**{item_name}**: {message}")
                else:
                    st.success(str(item))
    
    if warnings:
        with st.expander(f"⚠️ 警告项 ({len(warnings)})", expanded=(len(errors) == 0)):
            for item in warnings:
                if isinstance(item, dict):
                    item_name = item.get("item", "未知项")
                    message = item.get("message", "")
                    st.warning(f"**{item_name}**: {message}")
                else:
                    st.warning(str(item))
    
    if errors:
        with st.expander(f"❌ 错误项 ({len(errors)})", expanded=True):
            for item in errors:
                if isinstance(item, dict):
                    item_name = item.get("item", "未知项")
                    message = item.get("message", "")
                    st.error(f"**{item_name}**: {message}")
                else:
                    st.error(str(item))
    
    if not passed_items and not warnings and not errors:
        st.info("📭 暂无校验结果")
    
    render_l3_raw_stub(data, "需求校验原始数据")


def render_visualization_generation(data: dict):
    """可视化汇报阶段专属渲染器
    
    渲染三个结构化ASCII流可视化：业务流程图、领域关系图、模块依赖图
    
    Args:
        data: 可视化汇报数据字典，格式为 {
            "ascii_flows": str,      # 业务流程图ASCII流
            "ascii_entities": str,   # 领域关系图ASCII流
            "ascii_modules": str     # 模块依赖图ASCII流
        }
    """
    if not data:
        st.warning("📭 暂无可视化汇报数据")
        return
    
    ascii_flows = data.get("ascii_flows", "")
    ascii_entities = data.get("ascii_entities", "")
    ascii_modules = data.get("ascii_modules", "")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔄 业务流程图")
        if ascii_flows:
            st.code(ascii_flows, language=None)
        else:
            st.info("暂无业务流程图")
    
    with col2:
        st.markdown("### 📊 领域关系图")
        if ascii_entities:
            st.code(ascii_entities, language=None)
        else:
            st.info("暂无领域关系图")
    
    st.markdown("---")
    st.markdown("### 🏗️ 模块依赖图")
    if ascii_modules:
        st.code(ascii_modules, language=None)
    else:
        st.info("暂无模块依赖图")
    
    render_l3_raw_stub(data, "可视化汇报原始数据")


def render_landing_plan(data: dict):
    """落地方案渲染器
    
    渲染落地方案生成阶段的结果，包括关键指标、Markdown方案内容和模块拆分详情。
    适用于展示项目拆分、模块依赖等落地执行信息。
    
    展示结构：
    1. L1指标行：模块数、文件数
    2. 方案内容：使用st.markdown展示Markdown格式的落地方案
    3. 模块拆分详情：使用st.expander展示各模块的详细信息
    4. L3原始数据：折叠收纳原始JSON数据
    
    Args:
        data: 落地方案数据字典，格式为 {
            "modules": [
                {"name": "模块1_用户模块", "files": 5, "description": "用户管理相关功能"}
            ],
            "total_files": 25,
            "markdown_content": "# 落地方案\\n## 模块拆分...",
            "dependencies": {"模块1": ["模块2"]}
        }
        - modules: 模块列表，包含名称、文件数、描述等
        - total_files: 总文件数
        - markdown_content: Markdown格式的方案内容
        - dependencies: 模块依赖关系（可选）
    
    Example:
        >>> landing_data = {
        ...     "modules": [
        ...         {"name": "模块0_全局调度", "files": 3, "description": "全局调度面板"},
        ...         {"name": "模块1_用户模块", "files": 5, "description": "用户管理"}
        ...     ],
        ...     "total_files": 8,
        ...     "markdown_content": "# 落地方案\\n本次拆分为2个模块..."
        ... }
        >>> render_landing_plan(landing_data)
    """
    st.markdown("### 📋 落地方案")
    
    metrics = extract_landing_plan_metrics(data)
    render_l1_metrics(metrics)
    
    modules = data.get("modules", [])
    markdown_content = data.get("markdown_content", "")
    dependencies = data.get("dependencies", {})
    
    st.markdown("---")
    
    if markdown_content:
        st.markdown(markdown_content)
    else:
        st.info("📭 暂无方案内容")
    
    if modules:
        with st.expander(f"📦 模块拆分详情 ({len(modules)}个模块)", expanded=False):
            for i, module in enumerate(modules):
                if isinstance(module, dict):
                    module_name = module.get("name", f"模块{i+1}")
                    files_count = module.get("files", 0)
                    description = module.get("description", "暂无描述")
                    
                    st.markdown(f"#### {module_name}")
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.metric("文件数", files_count)
                    with col2:
                        st.markdown(f"**描述**: {description}")
                    
                    if i < len(modules) - 1:
                        st.divider()
                else:
                    st.write(module)
    
    if dependencies:
        with st.expander("🔗 模块依赖关系", expanded=False):
            for module, deps in dependencies.items():
                if isinstance(deps, list):
                    deps_str = " → ".join(deps) if deps else "无依赖"
                    st.markdown(f"**{module}**: {deps_str}")
                else:
                    st.markdown(f"**{module}**: {deps}")
    
    render_l3_raw_stub(data, "落地方案原始数据")


def render_ide_bundle(data: dict):
    """IDE引导包渲染器
    
    渲染IDE引导包生成阶段的结果，包括关键指标、内容摘要卡片、文件清单表格和下载功能。
    适用于展示生成的IDE规则文件、配置模板等引导包内容。
    
    展示结构：
    1. L1指标行：文件数、规则数
    2. 内容摘要卡片：使用st.container展示引导包概览
    3. 文件清单表格：使用st.dataframe展示文件列表
    4. 下载按钮：提供阶段结果导出功能
    5. L3原始数据：折叠收纳原始JSON数据
    
    Args:
        data: IDE引导包数据字典，格式为 {
            "files": [
                {"name": "AGENT.md", "type": "规则", "size": "2.5KB", "path": ".trae/rules/"}
            ],
            "rules_count": 5,
            "total_size": "15.2KB",
            "bundle_content": "...",
            "download_filename": "ide_bundle.json"
        }
        - files: 文件列表，包含名称、类型、大小、路径等
        - rules_count: 规则文件数量
        - total_size: 总大小（可选）
        - bundle_content: 完整包内容（用于下载）
        - download_filename: 下载文件名（可选）
    
    Example:
        >>> bundle_data = {
        ...     "files": [
        ...         {"name": "AGENT.md", "type": "规则", "size": "2.5KB"}
        ...     ],
        ...     "rules_count": 1,
        ...     "total_size": "2.5KB",
        ...     "bundle_content": "完整包内容..."
        ... }
        >>> render_ide_bundle(bundle_data)
    """
    st.markdown("### 📦 IDE引导包")
    
    metrics = extract_ide_bundle_metrics(data)
    render_l1_metrics(metrics)
    
    files = data.get("files", [])
    total_size = data.get("total_size", "-")
    download_filename = data.get("download_filename", "ide_bundle.json")
    
    file_count = len(files)
    rules_count = metrics.get("规则数", {}).get("value", 0)
    
    st.markdown("---")
    
    with st.container(border=True):
        st.markdown("#### 📋 引导包摘要")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**总文件数**: {file_count}")
        with col2:
            st.markdown(f"**规则文件**: {rules_count}")
        st.caption(f"总大小: {total_size}")
    
    if files:
        st.markdown("#### 📁 文件清单")
        
        import pandas as pd
        
        display_files = []
        for f in files:
            if isinstance(f, dict):
                display_files.append({
                    "文件名": f.get("name", "-"),
                    "类型": f.get("type", "-"),
                    "大小": f.get("size", "-"),
                    "路径": f.get("path", "-")
                })
            else:
                display_files.append({"文件名": str(f), "类型": "-", "大小": "-", "路径": "-"})
        
        if display_files:
            df = pd.DataFrame(display_files)
            st.dataframe(df, width="stretch", hide_index=True)
    
    st.markdown("#### ⬇️ 导出阶段结果")
    
    export_data = data
    if isinstance(export_data, (dict, list)):
        download_data = json.dumps(export_data, ensure_ascii=False, indent=2)
        mime_type = "application/json"
        if not download_filename.endswith(".json"):
            download_filename = download_filename.rsplit(".", 1)[0] + ".json" if "." in download_filename else download_filename + ".json"
    else:
        download_data = str(export_data)
        mime_type = "text/plain"
    
    st.download_button(
        label="📥 导出阶段结果",
        data=download_data,
        file_name=download_filename,
        mime=mime_type,
        key=f"download_ide_bundle_{id(data)}"
    )
    
    render_l3_raw_stub(data, "IDE引导包原始数据")


def render_contract_generation(data: dict):
    """契约生成阶段专属渲染器
    
    按照L1→L2→L3的层级结构渲染契约生成阶段的结果：
    1. L1指标层：展示关键指标（接口数、Schema数等）
    2. L2内容层：展示API浏览器和数据模型树
    3. L3原始层：收纳原始契约数据
    
    Args:
        data: 契约生成阶段的结果数据，格式为 {
            "interfaces": [...],  # 接口列表
            "schemas": {...},     # 数据模型
            "metrics": {          # 可选，指标数据
                "interface_count": {"value": 10},
                "schema_count": {"value": 5}
            },
            "raw_data": {...}     # 原始数据
        }
    
    Example:
        >>> data = {
        ...     "interfaces": [
        ...         {"method": "POST", "path": "/api/user", "description": "创建用户"}
        ...     ],
        ...     "schemas": {"User": {"type": "object", "properties": {...}}},
        ...     "metrics": {
        ...         "接口总数": {"value": 10},
        ...         "Schema总数": {"value": 5}
        ...     }
        ... }
        >>> render_contract_generation(data)
    """
    st.markdown("### 📜 契约生成结果")
    
    metrics = extract_contract_generation_metrics(data)
    render_l1_metrics(metrics)
    
    st.markdown("---")
    
    interfaces = data.get("interfaces", [])
    if interfaces:
        st.markdown("#### 🔌 API接口列表")
        render_api_browser(interfaces)
    
    schemas = data.get("schemas", {})
    if schemas:
        st.markdown("#### 📐 数据模型定义")
        for schema_name, schema_def in schemas.items():
            with st.expander(f"📦 {schema_name}", expanded=False):
                render_schema_tree(schema_def)
    
    render_l3_raw_stub(data, "契约原始数据")


def render_api_browser(interfaces: list):
    """API浏览器风格列表渲染器
    
    使用极客熟悉的格式展示API列表，每个API显示方法、路径、描述、
    请求参数和响应格式。使用颜色区分不同的HTTP方法：
    - GET = 绿色
    - POST = 蓝色
    - PUT = 橙色
    - DELETE = 红色
    - PATCH = 紫色
    
    Args:
        interfaces: 接口列表，格式为 [
            {
                "method": "POST",
                "path": "/api/user",
                "description": "创建用户",
                "parameters": [...],      # 可选，请求参数
                "request_body": {...},    # 可选，请求体
                "response": {...}         # 可选，响应格式
            },
            ...
        ]
    
    Example:
        >>> interfaces = [
        ...     {
        ...         "method": "GET",
        ...         "path": "/api/users",
        ...         "description": "获取用户列表",
        ...         "parameters": [
        ...             {"name": "page", "type": "integer", "description": "页码"}
        ...         ],
        ...         "response": {"type": "array", "items": {"$ref": "User"}}
        ...     },
        ...     {
        ...         "method": "POST",
        ...         "path": "/api/user",
        ...         "description": "创建新用户",
        ...         "request_body": {"$ref": "CreateUserRequest"}
        ...     }
        ... ]
        >>> render_api_browser(interfaces)
    """
    if not interfaces:
        st.info("📭 暂无接口定义")
        return
    
    method_colors = {
        "GET": ("#4CAF50", "#E8F5E9"),
        "POST": ("#2196F3", "#E3F2FD"),
        "PUT": ("#FF9800", "#FFF3E0"),
        "DELETE": ("#F44336", "#FFEBEE"),
        "PATCH": ("#9C27B0", "#F3E5F5"),
        "HEAD": ("#607D8B", "#ECEFF1"),
        "OPTIONS": ("#795548", "#EFEBE9")
    }
    
    method_default = ("#757575", "#FAFAFA")
    
    for api in interfaces:
        if not isinstance(api, dict):
            st.warning(f"接口数据格式错误: {api}")
            continue
        
        method = api.get("method", "GET").upper()
        path = api.get("path", api.get("endpoint", "/unknown"))
        description = api.get("description", api.get("desc", "暂无描述"))
        
        text_color, bg_color = method_colors.get(method, method_default)
        
        header_html = f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            background-color: {bg_color};
            border-radius: 6px;
            border-left: 4px solid {text_color};
            margin-bottom: 8px;
        ">
            <span style="
                background-color: {text_color};
                color: white;
                padding: 4px 10px;
                border-radius: 4px;
                font-family: monospace;
                font-weight: bold;
                font-size: 12px;
            ">{method}</span>
            <span style="
                font-family: monospace;
                font-size: 14px;
                font-weight: 500;
                color: #333;
            ">{path}</span>
        </div>
        """
        
        with st.expander("", expanded=False):
            st.markdown(header_html, unsafe_allow_html=True)
            
            st.markdown(f"**描述:** {description}")
            
            parameters = api.get("parameters", api.get("params", []))
            if parameters:
                st.markdown("**请求参数:**")
                if isinstance(parameters, list):
                    param_data = []
                    for param in parameters:
                        if isinstance(param, dict):
                            param_data.append({
                                "参数名": param.get("name", param.get("param", "-")),
                                "类型": param.get("type", "string"),
                                "必填": "是" if param.get("required", False) else "否",
                                "描述": param.get("description", param.get("desc", "-"))
                            })
                    if param_data:
                        import pandas as pd
                        st.dataframe(pd.DataFrame(param_data), width="stretch", hide_index=True)
                else:
                    st.json(parameters)
            
            request_body = api.get("request_body", api.get("requestBody", api.get("body")))
            if request_body:
                st.markdown("**请求体:**")
                if isinstance(request_body, dict):
                    render_schema_tree(request_body, level=0)
                else:
                    st.code(str(request_body), language="json")
            
            response = api.get("response", api.get("responses", api.get("resp")))
            if response:
                st.markdown("**响应格式:**")
                if isinstance(response, dict):
                    render_schema_tree(response, level=0)
                else:
                    st.code(str(response), language="json")


def render_schema_tree(schema: dict, level: int = 0):
    """数据模型树渲染器
    
    使用Markdown列表格式展示数据模型的层级关系，每个字段显示：
    名称、类型、是否必填、描述。支持递归处理嵌套对象。
    
    Args:
        schema: 数据模型定义，格式为 {
            "type": "object",
            "properties": {
                "field_name": {
                    "type": "string",
                    "description": "字段描述",
                    "required": true
                }
            },
            "required": ["field_name"]
        }
        level: 当前层级深度，用于控制缩进，默认为0
    
    Example:
        >>> schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "id": {"type": "integer", "description": "用户ID"},
        ...         "name": {"type": "string", "description": "用户名"},
        ...         "profile": {
        ...             "type": "object",
        ...             "properties": {
        ...                 "avatar": {"type": "string", "description": "头像URL"},
        ...                 "bio": {"type": "string", "description": "个人简介"}
        ...             }
        ...         }
        ...     },
        ...     "required": ["id", "name"]
        ... }
        >>> render_schema_tree(schema)
    """
    if not schema:
        st.info("暂无数据模型定义")
        return
    
    if not isinstance(schema, dict):
        st.code(str(schema), language="json")
        return
    
    indent = "    " * level
    
    schema_type = schema.get("type", "unknown")
    
    if schema_type == "array":
        items = schema.get("items", {})
        item_desc = items.get("description", "")
        st.markdown(f"{indent}📦 **数组类型** {f'- {item_desc}' if item_desc else ''}")
        if items:
            st.markdown(f"{indent}*数组元素:*")
            render_schema_tree(items, level + 1)
        return
    
    if schema_type != "object":
        description = schema.get("description", schema.get("desc", ""))
        default_value = schema.get("default")
        enum_values = schema.get("enum", [])
        
        type_str = f"`{schema_type}`"
        if enum_values:
            type_str += f" (枚举: {', '.join(map(str, enum_values))})"
        
        desc_str = f" - {description}" if description else ""
        default_str = f" [默认: `{default_value}`]" if default_value is not None else ""
        
        st.markdown(f"{indent}🔹 类型: {type_str}{desc_str}{default_str}")
        return
    
    properties = schema.get("properties", schema.get("fields", {}))
    required_fields = set(schema.get("required", []))
    
    if not properties:
        description = schema.get("description", "")
        st.markdown(f"{indent}📦 **对象类型** {f'- {description}' if description else ''}")
        return
    
    for field_name, field_def in properties.items():
        if not isinstance(field_def, dict):
            st.markdown(f"{indent}- **{field_name}**: `{field_def}`")
            continue
        
        field_type = field_def.get("type", "unknown")
        field_desc = field_def.get("description", field_def.get("desc", ""))
        is_required = field_name in required_fields or field_def.get("required", False)
        
        required_badge = '<span style="color: #F44336; font-weight: bold;">*</span>' if is_required else ""
        
        if field_type == "object":
            nested_props = field_def.get("properties", field_def.get("fields", {}))
            if nested_props:
                st.markdown(f"{indent}- **{field_name}** {required_badge} `object` {f'- {field_desc}' if field_desc else ''}")
                render_schema_tree(field_def, level + 1)
            else:
                st.markdown(f"{indent}- **{field_name}** {required_badge} `object` {f'- {field_desc}' if field_desc else ''}")
        elif field_type == "array":
            items = field_def.get("items", {})
            item_type = items.get("type", "unknown") if isinstance(items, dict) else "unknown"
            st.markdown(f"{indent}- **{field_name}** {required_badge} `array<{item_type}>` {f'- {field_desc}' if field_desc else ''}")
            if isinstance(items, dict) and items.get("type") == "object":
                render_schema_tree(items, level + 1)
        else:
            enum_values = field_def.get("enum", [])
            type_display = f"`{field_type}`"
            if enum_values:
                type_display += f" (枚举)"
            
            default_value = field_def.get("default")
            default_str = f" [默认: `{default_value}`]" if default_value is not None else ""
            
            st.markdown(f"{indent}- **{field_name}** {required_badge} {type_display} {f'- {field_desc}' if field_desc else ''}{default_str}")


def render_architecture_iteration(data: dict):
    """架构迭代阶段专属渲染器
    
    按照层级结构展示架构迭代阶段的完整结果：
    1. L1层：关键指标行（方案数、评审意见数、融合耗时等）
    2. L2层：三方案决策要点矩阵
    3. L2层：对抗评审摘要
    4. L2层：最终决策高亮区
    5. L3层：原始数据收纳器
    
    适用于架构迭代阶段的Pipeline结果展示，提供结构化、层次化的
    可视化呈现，帮助用户快速理解多方案对比与最终决策。
    
    Args:
        data: 架构迭代阶段数据字典，格式为 {
            "metrics": {
                "方案数": {"value": 3},
                "评审意见数": {"value": 12},
                "融合耗时": {"value": "15.2s"},
                "迭代轮次": {"value": 2}
            },
            "solutions": [
                {
                    "name": "整洁架构方案",
                    "core_goal": "高内聚低耦合",
                    "design_points": ["分层架构", "依赖倒置"],
                    "pros": ["可维护性强", "易于测试"],
                    "cons": ["初期成本高", "学习曲线陡"]
                },
                ...
            ],
            "critiques": [
                {
                    "reviewer_paradigm": "边界防腐与高度解耦",
                    "summary": "评审摘要",
                    "critique": {...}
                }
            ],
            "final_decision": {
                "adopted": "融合方案",
                "reason": "综合各方案优势...",
                "key_points": ["要点1", "要点2"]
            },
            "raw_data": {...}
        }
    
    Example:
        >>> data = {
        ...     "metrics": {"方案数": {"value": 3}, "评审意见数": {"value": 12}},
        ...     "solutions": [...],
        ...     "critiques": [...],
        ...     "final_decision": {"adopted": "融合方案", "reason": "..."}
        ... }
        >>> render_architecture_iteration(data)
    """
    st.markdown("## 🏗️ 架构迭代结果")
    
    metrics = data.get("metrics", {})
    if metrics:
        st.markdown("### 📊 关键指标")
        render_l1_metrics(metrics)
    
    solutions = data.get("solutions", [])
    if solutions:
        st.markdown("### 🔄 决策要点矩阵")
        render_decision_points_matrix(solutions)
    
    critiques = data.get("critiques", [])
    if critiques:
        st.markdown("### 🎯 对抗评审摘要")
        render_critiques_summary(critiques)
    
    decision = data.get("final_decision", {})
    if decision:
        st.markdown("### 🎯 最终决策")
        render_final_decision_highlight(decision)
    
    raw_data = data.get("raw_data", data)
    other_keys = set(data.keys()) - {"metrics", "solutions", "critiques", "final_decision", "raw_data"}
    if other_keys:
        additional_data = {k: data[k] for k in other_keys}
        if additional_data:
            raw_data = {**raw_data, **additional_data} if raw_data != data else data
    
    render_l3_raw_stub(raw_data, "架构迭代原始数据")


def render_decision_points_matrix(solutions: list):
    """决策要点矩阵渲染器
    
    使用三栏布局展示架构方案的决策要点矩阵，每栏展示一个方案的
    设计哲学，包括方案名称、核心设计目标、设计要点、主要风险。
    使用容器和边框增强视觉效果，提供清晰的方案对比视图。
    
    Args:
        solutions: 方案列表，每个方案为字典格式，包含：
            - name: 方案名称（如"整洁架构方案"、"响应式方案"）
            - core_goal: 核心设计目标描述
            - design_points: 设计要点列表
            - pros: 优点列表
            - cons: 缺点列表
    """
    if not solutions:
        st.info("📭 暂无方案数据")
        return
    
    display_solutions = solutions[:3]
    
    while len(display_solutions) < 3:
        display_solutions.append({
            "name": f"方案{len(display_solutions) + 1}",
            "core_goal": "-",
            "design_points": [],
            "pros": [],
            "cons": []
        })
    
    cols = st.columns(3)
    
    solution_colors = ["#E3F2FD", "#E8F5E9", "#FFF3E0"]
    solution_border_colors = ["#1976D2", "#388E3C", "#F57C00"]
    solution_icons = ["🔷", "📗", "🔶"]
    
    for i, (col, solution) in enumerate(zip(cols, display_solutions)):
        with col:
            name = solution.get("name", f"方案{i + 1}")
            core_goal = solution.get("core_goal", "暂无描述")
            design_points = solution.get("design_points", [])
            pros = solution.get("pros", [])
            cons = solution.get("cons", [])
            
            container_html = f"""
            <div style="
                border: 2px solid {solution_border_colors[i]};
                border-radius: 12px;
                padding: 15px;
                background-color: {solution_colors[i]};
                margin-bottom: 10px;
            ">
                <div style="
                    font-size: 18px;
                    font-weight: bold;
                    color: {solution_border_colors[i]};
                    margin-bottom: 10px;
                ">{solution_icons[i]} {name}</div>
            """
            st.markdown(container_html, unsafe_allow_html=True)
            
            st.markdown(f"**🎯 核心目标**")
            st.caption(core_goal)
            
            st.markdown("**📝 设计要点**")
            if design_points:
                for dp in design_points:
                    st.markdown(f"- {dp}")
            else:
                st.caption("暂无")
            
            st.markdown("**⚠️ 主要风险**")
            if cons:
                for con in cons[:3]:
                    st.markdown(f"- {con}")
            else:
                st.caption("暂无")
            
            st.markdown("</div>", unsafe_allow_html=True)


def render_critiques_summary(critiques: list):
    """对抗评审摘要渲染器
    
    展示对抗评审的摘要内容，按评审视角分组展示。
    
    Args:
        critiques: 对抗评审列表，每个评审为字典格式
    """
    if not critiques:
        st.info("📭 暂无对抗评审数据")
        return
    
    for idx, critique in enumerate(critiques):
        reviewer_paradigm = critique.get("reviewer_paradigm", f"评审者{idx + 1}")
        summary = critique.get("summary", "")
        critique_data = critique.get("critique", {})
        
        with st.expander(f"🎯 {reviewer_paradigm}", expanded=(idx == 0)):
            if summary:
                st.markdown(f"**摘要**: {summary}")
            
            if critique_data:
                critique_of_a = critique_data.get("critique_of_a", {})
                critique_of_b = critique_data.get("critique_of_b", {})
                
                if critique_of_a:
                    st.markdown("**对方案A的评审**:")
                    fatal_flaws = critique_of_a.get("fatal_flaws", [])
                    potential_bottlenecks = critique_of_a.get("potential_bottlenecks", [])
                    technical_debt = critique_of_a.get("technical_debt", [])
                    
                    if fatal_flaws:
                        st.markdown("*致命缺陷*:")
                        for flaw in fatal_flaws[:2]:
                            st.markdown(f"- {flaw}")
                    
                    if potential_bottlenecks:
                        st.markdown("*潜在瓶颈*:")
                        for bottleneck in potential_bottlenecks[:2]:
                            st.markdown(f"- {bottleneck}")
                    
                    if technical_debt:
                        st.markdown("*技术债务*:")
                        for debt in technical_debt[:2]:
                            st.markdown(f"- {debt}")
                
                if critique_of_b:
                    st.markdown("**对方案B的评审**:")
                    fatal_flaws = critique_of_b.get("fatal_flaws", [])
                    potential_bottlenecks = critique_of_b.get("potential_bottlenecks", [])
                    technical_debt = critique_of_b.get("technical_debt", [])
                    
                    if fatal_flaws:
                        st.markdown("*致命缺陷*:")
                        for flaw in fatal_flaws[:2]:
                            st.markdown(f"- {flaw}")
                    
                    if potential_bottlenecks:
                        st.markdown("*潜在瓶颈*:")
                        for bottleneck in potential_bottlenecks[:2]:
                            st.markdown(f"- {bottleneck}")
                    
                    if technical_debt:
                        st.markdown("*技术债务*:")
                        for debt in technical_debt[:2]:
                            st.markdown(f"- {debt}")


def render_solution_comparison_matrix(solutions: list):
    """三方案对比矩阵渲染器
    
    使用三栏布局展示架构方案的对比矩阵，每栏展示一个方案的
    设计哲学，包括方案名称、核心设计目标、优点列表、缺点列表。
    使用容器和边框增强视觉效果，提供清晰的方案对比视图。
    
    Args:
        solutions: 方案列表，每个方案为字典格式，包含：
            - name: 方案名称（如"整洁架构方案"、"响应式方案"）
            - core_goal: 核心设计目标描述
            - pros: 优点列表
            - cons: 缺点列表
    
    Example:
        >>> solutions = [
        ...     {
        ...         "name": "整洁架构方案",
        ...         "core_goal": "高内聚低耦合，分层解耦",
        ...         "pros": ["可维护性强", "易于测试", "职责清晰"],
        ...         "cons": ["初期成本高", "学习曲线陡"]
        ...     },
        ...     {
        ...         "name": "响应式方案",
        ...         "core_goal": "高并发、低延迟响应",
        ...         "pros": ["性能优异", "资源利用率高"],
        ...         "cons": ["调试复杂", "代码可读性降低"]
        ...     },
        ...     {
        ...         "name": "垂直切片方案",
        ...         "core_goal": "按业务功能垂直切分",
        ...         "pros": ["开发效率高", "部署灵活"],
        ...         "cons": ["代码重复", "跨切片协调难"]
        ...     }
        ... ]
        >>> render_solution_comparison_matrix(solutions)
    """
    if not solutions:
        st.info("📭 暂无方案数据")
        return
    
    display_solutions = solutions[:3]
    
    while len(display_solutions) < 3:
        display_solutions.append({
            "name": f"方案{len(display_solutions) + 1}",
            "core_goal": "-",
            "pros": [],
            "cons": []
        })
    
    cols = st.columns(3)
    
    solution_colors = ["#E3F2FD", "#E8F5E9", "#FFF3E0"]
    solution_border_colors = ["#1976D2", "#388E3C", "#F57C00"]
    solution_icons = ["🔷", "📗", "🔶"]
    
    for i, (col, solution) in enumerate(zip(cols, display_solutions)):
        with col:
            name = solution.get("name", f"方案{i + 1}")
            core_goal = solution.get("core_goal", "暂无描述")
            pros = solution.get("pros", [])
            cons = solution.get("cons", [])
            
            container_html = f"""
            <div style="
                border: 2px solid {solution_border_colors[i]};
                border-radius: 12px;
                padding: 15px;
                background-color: {solution_colors[i]};
                margin-bottom: 10px;
            ">
                <div style="
                    font-size: 18px;
                    font-weight: bold;
                    color: {solution_border_colors[i]};
                    margin-bottom: 10px;
                ">{solution_icons[i]} {name}</div>
            """
            st.markdown(container_html, unsafe_allow_html=True)
            
            st.markdown(f"**🎯 核心目标**")
            st.caption(core_goal)
            
            st.markdown("**✅ 优点**")
            if pros:
                for pro in pros:
                    st.markdown(f"- {pro}")
            else:
                st.caption("暂无")
            
            st.markdown("**⚠️ 缺点**")
            if cons:
                for con in cons:
                    st.markdown(f"- {con}")
            else:
                st.caption("暂无")
            
            st.markdown("</div>", unsafe_allow_html=True)


def render_final_decision_highlight(decision: dict):
    """最终决策高亮区渲染器
    
    使用高亮区域展示最终采纳的架构决策，包括决策名称、
    决策理由和关键要点。使用st.success或st.info创建视觉
    高亮效果，配合st.expander展示详细的决策说明。
    
    Args:
        decision: 决策字典，包含：
            - adopted: 最终采纳的方案名称
            - reason: 决策理由说明
            - key_points: 关键要点列表（可选）
            - details: 详细决策说明（可选，用于展开区域）
            - confidence: 决策置信度（可选，如"高"、"中"）
    
    Example:
        >>> decision = {
        ...     "adopted": "融合方案",
        ...     "reason": "综合整洁架构的可维护性与响应式方案的高性能优势",
        ...     "key_points": [
        ...         "核心业务采用整洁架构分层",
        ...         "高并发场景引入响应式模式",
        ...         "渐进式迁移降低风险"
        ...     ],
        ...     "confidence": "高",
        ...     "details": "详细的技术选型分析和实施路径..."
        ... }
        >>> render_final_decision_highlight(decision)
    """
    if not decision:
        st.info("📭 暂无决策数据")
        return
    
    adopted = decision.get("adopted", "未确定")
    reason = decision.get("reason", "暂无说明")
    key_points = decision.get("key_points", [])
    details = decision.get("details", "")
    confidence = decision.get("confidence", "")
    
    confidence_map = {
        "高": ("🟢", "high"),
        "中": ("🟡", "medium"),
        "低": ("🔴", "low")
    }
    confidence_icon, confidence_level = confidence_map.get(confidence, ("⚪", "unknown"))
    
    highlight_html = f"""
    <div style="
        border: 2px solid #4CAF50;
        border-radius: 12px;
        padding: 20px;
        background-color: #E8F5E9;
        margin-bottom: 15px;
    ">
        <div style="
            font-size: 20px;
            font-weight: bold;
            color: #2E7D32;
            margin-bottom: 10px;
        ">✅ 最终采纳：{adopted}</div>
    """
    st.markdown(highlight_html, unsafe_allow_html=True)
    
    if confidence:
        st.markdown(f"**决策置信度：** {confidence_icon} {confidence}")
    
    st.markdown(f"**决策理由：**")
    st.info(reason)
    
    if key_points:
        st.markdown("**📋 关键要点：**")
        for i, point in enumerate(key_points, 1):
            st.markdown(f"{i}. {point}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if details:
        with st.expander("📄 查看详细决策说明", expanded=False):
            st.markdown(details)


def extract_requirement_anchoring_metrics(data):
    """从需求锚定结果中提取指标
    
    从需求锚定阶段的结果数据中提取关键指标，包括实体数、流程数和属性数。
    支持多种数据结构格式，包括嵌套的structured_requirement结构。
    
    数据结构适配：
    1. 优先使用标准格式：data["entities"], data["flows"], data["attributes"]
    2. 其次使用计数格式：data["metrics"]["entity_count"]
    3. 然后使用requirements层级列表格式：data["requirements"][{level: 2/3/4}]
    4. 从structured_requirement中提取
    5. 提供fallback：如果都失败，返回默认值
    
    Args:
        data: 需求锚定结果字典，可能包含以下字段：
            - requirements: 层级需求列表（level 2=实体, level 3=流程, level 4=属性）
            - entities: 实体列表或实体数据字典
            - flows: 流程列表或流程数据字典
            - attributes: 属性列表或属性数据字典
            - structured_requirement: 嵌套的结构化需求数据
            - metrics: 预计算的指标字典
    
    Returns:
        dict: 标准化的指标字典，格式为 {
            "识别实体数": {"value": N},
            "业务流程数": {"value": N},
            "属性总数": {"value": N}
        }
        如果数据缺失或格式错误，对应指标值为0
    
    Example:
        >>> data = {
        ...     "entities": [{"name": "用户"}, {"name": "订单"}],
        ...     "flows": [{"name": "下单流程"}],
        ...     "attributes": [{"name": "用户名"}, {"name": "订单号"}]
        ... }
        >>> extract_requirement_anchoring_metrics(data)
        {'识别实体数': {'value': 2}, '业务流程数': {'value': 1}, '属性总数': {'value': 2}}
    """
    entity_count = 0
    flow_count = 0
    attribute_count = 0
    
    if not isinstance(data, dict):
        return {
            "识别实体数": {"value": 0},
            "业务流程数": {"value": 0},
            "属性总数": {"value": 0}
        }
    
    entities = data.get("entities", [])
    flows = data.get("flows", [])
    attributes = data.get("attributes", [])
    
    if entities and isinstance(entities, list):
        entity_count = len(entities)
    if flows and isinstance(flows, list):
        flow_count = len(flows)
    if attributes and isinstance(attributes, list):
        attribute_count = len(attributes)
    
    if "metrics" in data and isinstance(data["metrics"], dict):
        metrics = data["metrics"]
        if entity_count == 0:
            entity_count = metrics.get("entity_count", metrics.get("识别实体数", {}).get("value", 0))
            if isinstance(entity_count, dict):
                entity_count = entity_count.get("value", 0)
        if flow_count == 0:
            flow_count = metrics.get("flow_count", metrics.get("业务流程数", {}).get("value", 0))
            if isinstance(flow_count, dict):
                flow_count = flow_count.get("value", 0)
        if attribute_count == 0:
            attribute_count = metrics.get("attribute_count", metrics.get("属性总数", {}).get("value", 0))
            if isinstance(attribute_count, dict):
                attribute_count = attribute_count.get("value", 0)
    
    requirements = data.get("requirements", [])
    if (entity_count == 0 or flow_count == 0 or attribute_count == 0) and requirements and isinstance(requirements, list):
        level_2_count = len([r for r in requirements if isinstance(r, dict) and r.get("level") == 2])
        level_3_count = len([r for r in requirements if isinstance(r, dict) and r.get("level") == 3])
        level_4_count = len([r for r in requirements if isinstance(r, dict) and r.get("level") == 4])
        
        if entity_count == 0:
            entity_count = level_2_count
        if flow_count == 0:
            flow_count = level_3_count
        if attribute_count == 0:
            attribute_count = level_4_count
    
    structured_req = data.get("structured_requirement", {})
    if (entity_count == 0 or flow_count == 0 or attribute_count == 0) and isinstance(structured_req, dict):
        requirements_sr = structured_req.get("requirements", [])
        if requirements_sr and isinstance(requirements_sr, list):
            level_2_count = len([r for r in requirements_sr if isinstance(r, dict) and r.get("level") == 2])
            level_3_count = len([r for r in requirements_sr if isinstance(r, dict) and r.get("level") == 3])
            level_4_count = len([r for r in requirements_sr if isinstance(r, dict) and r.get("level") == 4])
            
            if entity_count == 0:
                entity_count = level_2_count
            if flow_count == 0:
                flow_count = level_3_count
            if attribute_count == 0:
                attribute_count = level_4_count
        
        if entity_count == 0:
            entities_sr = structured_req.get("entities", [])
            if isinstance(entities_sr, list):
                entity_count = len(entities_sr)
            elif isinstance(entities_sr, dict):
                entity_count = len(entities_sr.keys())
        
        if flow_count == 0:
            flows_sr = structured_req.get("flows", structured_req.get("flow", []))
            if isinstance(flows_sr, list):
                flow_count = len(flows_sr)
            elif isinstance(flows_sr, dict):
                flow_count = len(flows_sr.keys())
        
        if attribute_count == 0:
            attributes_sr = structured_req.get("attributes", [])
            if isinstance(attributes_sr, list):
                attribute_count = len(attributes_sr)
            elif isinstance(attributes_sr, dict):
                attribute_count = len(attributes_sr.keys())
    
    if entity_count == 0 and "domain_entities" in data:
        domain_entities = data["domain_entities"]
        if isinstance(domain_entities, list):
            entity_count = len(domain_entities)
    
    if flow_count == 0 and "business_flows" in data:
        business_flows = data["business_flows"]
        if isinstance(business_flows, list):
            flow_count = len(business_flows)
    
    return {
        "识别实体数": {"value": int(entity_count) if entity_count else 0},
        "业务流程数": {"value": int(flow_count) if flow_count else 0},
        "属性总数": {"value": int(attribute_count) if attribute_count else 0}
    }


def extract_requirement_validation_metrics(data: dict) -> dict:
    """从需求校验结果中提取指标
    
    从需求校验阶段的结果数据中提取关键指标，包括通过项数、警告数和错误数。
    如果原始数据不包含这些标准字段，会尝试从其他字段中提取有意义的指标。
    
    数据结构适配：
    1. check_results维度评分格式：data["check_results"][{dimension, score, issues, suggestions}]
    2. 标准格式：data["passed"], data["warnings"], data["errors"]
    3. 汇总格式：data["summary"]["passed"], data["summary"]["warnings"]
    4. 嵌套格式：data["validation_result"]["passed"]
    5. 替代字段：data["valid_items"], data["warning_items"], data["error_items"]
    
    Args:
        data: 需求校验结果字典，可能包含以下字段：
            - check_results: 维度评分列表，每项包含 dimension, score, issues, suggestions
            - passed: 通过的校验项列表
            - warnings: 警告项列表
            - errors: 错误项列表
            - summary: 汇总统计字典
            - validation_result: 嵌套的校验结果
    
    Returns:
        dict: 标准化的指标字典，格式为 {
            "校验维度": {"value": N},
            "平均得分": {"value": N},
            "问题数": {"value": N}
        }
        或传统格式 {
            "校验通过项": {"value": N},
            "警告数": {"value": N},
            "错误数": {"value": N}
        }
        如果数据缺失或格式错误，对应指标值为0
    
    Example:
        >>> data = {
        ...     "check_results": [
        ...         {"dimension": "完整性", "score": 80, "issues": [...], "suggestions": [...]},
        ...         {"dimension": "一致性", "score": 95, "issues": [], "suggestions": [...]}
        ...     ]
        ... }
        >>> extract_requirement_validation_metrics(data)
        {'校验维度': {'value': 2}, '平均得分': {'value': 87}, '问题数': {'value': 1}}
    """
    if not isinstance(data, dict):
        return {
            "校验维度": {"value": 0},
            "平均得分": {"value": 0},
            "问题数": {"value": 0}
        }
    
    validation_result = data.get("validation_result", data)
    
    check_results = validation_result.get("check_results", data.get("check_results", []))
    if check_results and isinstance(check_results, list):
        total_issues = 0
        total_score = 0
        valid_count = 0
        
        for result in check_results:
            if isinstance(result, dict):
                score = result.get("score", 0)
                if isinstance(score, (int, float)):
                    total_score += score
                    valid_count += 1
                issues = result.get("issues", [])
                if isinstance(issues, list):
                    total_issues += len(issues)
        
        avg_score = int(total_score / valid_count) if valid_count > 0 else 0
        
        return {
            "校验维度": {"value": len(check_results)},
            "平均得分": {"value": avg_score},
            "问题数": {"value": total_issues}
        }
    
    passed_count = 0
    warning_count = 0
    error_count = 0
    
    if "summary" in validation_result and isinstance(validation_result["summary"], dict):
        summary = validation_result["summary"]
        passed_count = summary.get("passed", summary.get("passed_count", 0))
        warning_count = summary.get("warnings", summary.get("warning_count", 0))
        error_count = summary.get("errors", summary.get("error_count", 0))
        
        if passed_count or warning_count or error_count:
            return {
                "校验通过项": {"value": int(passed_count)},
                "警告数": {"value": int(warning_count)},
                "错误数": {"value": int(error_count)}
            }
    
    passed_items = validation_result.get("passed", data.get("valid_items", data.get("passed_items", [])))
    if isinstance(passed_items, list):
        passed_count = len(passed_items)
    elif isinstance(passed_items, (int, float)):
        passed_count = int(passed_items)
    
    warning_items = validation_result.get("warnings", data.get("warning_items", data.get("warning_list", [])))
    if isinstance(warning_items, list):
        warning_count = len(warning_items)
    elif isinstance(warning_items, (int, float)):
        warning_count = int(warning_items)
    
    error_items = validation_result.get("errors", data.get("error_items", data.get("error_list", [])))
    if isinstance(error_items, list):
        error_count = len(error_items)
    elif isinstance(error_items, (int, float)):
        error_count = int(error_items)
    
    if passed_count == 0 and warning_count == 0 and error_count == 0:
        if "check_results" in data:
            check_results = data["check_results"]
            if isinstance(check_results, list):
                for item in check_results:
                    if isinstance(item, dict):
                        status = item.get("status", item.get("level", "")).lower()
                        if status in ["pass", "passed", "success", "ok"]:
                            passed_count += 1
                        elif status in ["warning", "warn"]:
                            warning_count += 1
                        elif status in ["error", "fail", "failed"]:
                            error_count += 1
    
    return {
        "校验通过项": {"value": passed_count},
        "警告数": {"value": warning_count},
        "错误数": {"value": error_count}
    }


def extract_contract_generation_metrics(data):
    """从契约生成结果中提取指标
    
    从契约生成阶段的结果数据中提取关键指标，包括接口总数和Schema总数。
    支持多种数据结构格式，能够处理嵌套的契约数据。
    
    数据结构适配：
    1. 优先使用标准格式：data["interfaces"], data["schemas"]
    2. 其次使用计数格式：data["metrics"]["interface_count"]
    3. 从contracts嵌套结构中提取：data["contracts"]["interface"], data["contracts"]["data"]
    4. 最后使用实际LLM输出格式
    
    Args:
        data: 契约生成结果字典，可能包含以下字段：
            - interfaces: 接口列表
            - schemas: Schema字典或列表
            - contracts: 嵌套的契约数据
            - metrics: 预计算的指标字典
    
    Returns:
        dict: 标准化的指标字典，格式为 {
            "接口总数": {"value": N},
            "Schema总数": {"value": N}
        }
        如果数据缺失或格式错误，对应指标值为0
    
    Example:
        >>> data = {
        ...     "interfaces": [
        ...         {"method": "GET", "path": "/api/users"},
        ...         {"method": "POST", "path": "/api/user"}
        ...     ],
        ...     "schemas": {"User": {...}, "Order": {...}}
        ... }
        >>> extract_contract_generation_metrics(data)
        {'接口总数': {'value': 2}, 'Schema总数': {'value': 2}}
    """
    interface_count = 0
    schema_count = 0
    
    if not isinstance(data, dict):
        return {
            "接口总数": {"value": 0},
            "Schema总数": {"value": 0}
        }
    
    contracts = data.get("contracts", {})
    
    interfaces = data.get("interfaces", [])
    schemas = data.get("schemas", {})
    
    if interfaces and isinstance(interfaces, list):
        interface_count = len(interfaces)
    if schemas and isinstance(schemas, (dict, list)):
        if isinstance(schemas, dict):
            schema_count = len(schemas.keys())
        else:
            schema_count = len(schemas)
    
    if interface_count == 0 and isinstance(contracts, dict):
        interface_data = contracts.get("interface", {})
        if isinstance(interface_data, str):
            if "Protocol" in interface_data or "def " in interface_data:
                interface_count = 1
        elif isinstance(interface_data, dict):
            interface_count = len(interface_data.keys())
    
    if schema_count == 0 and isinstance(contracts, dict):
        data_contracts = contracts.get("data", {}).get("data_contracts", [])
        if isinstance(data_contracts, list):
            schema_count = len(data_contracts)
    
    if "metrics" in data and isinstance(data["metrics"], dict):
        metrics = data["metrics"]
        if interface_count == 0:
            interface_count = metrics.get("interface_count", metrics.get("接口总数", {}).get("value", 0))
            if isinstance(interface_count, dict):
                interface_count = interface_count.get("value", 0)
        if schema_count == 0:
            schema_count = metrics.get("schema_count", metrics.get("Schema总数", {}).get("value", 0))
            if isinstance(schema_count, dict):
                schema_count = schema_count.get("value", 0)
    
    return {
        "接口总数": {"value": int(interface_count) if interface_count else 0},
        "Schema总数": {"value": int(schema_count) if schema_count else 0}
    }


def extract_landing_plan_metrics(data):
    """从落地方案结果中提取指标
    
    从落地方案生成阶段的结果数据中提取关键指标，包括模块数和文件数。
    不包含预计工期指标。支持多种数据结构格式。
    
    数据结构适配：
    1. 优先使用标准格式：data["modules"], data["total_files"]
    2. 其次使用计数格式：data["metrics"]["module_count"]
    3. 从landing_plan嵌套结构中提取：data["landing_plan"]
    4. 最后使用其他格式
    
    Args:
        data: 落地方案结果字典，可能包含以下字段：
            - modules: 模块列表
            - total_files: 总文件数
            - landing_plan: 嵌套的落地方案数据
            - metrics: 预计算的指标字典
    
    Returns:
        dict: 标准化的指标字典，格式为 {
            "模块数": {"value": N},
            "文件数": {"value": N}
        }
        如果数据缺失或格式错误，对应指标值为0
    
    Example:
        >>> data = {
        ...     "modules": [
        ...         {"name": "模块0_全局调度", "files": 3},
        ...         {"name": "模块1_用户模块", "files": 5}
        ...     ],
        ...     "total_files": 8
        ... }
        >>> extract_landing_plan_metrics(data)
        {'模块数': {'value': 2}, '文件数': {'value': 8}}
    """
    module_count = 0
    file_count = 0
    
    if not isinstance(data, dict):
        return {
            "模块数": {"value": 0},
            "文件数": {"value": 0}
        }
    
    landing_plan = data.get("landing_plan", {})
    
    modules = data.get("modules", [])
    total_files = data.get("total_files", 0)
    
    if modules and isinstance(modules, list):
        module_count = len(modules)
    if total_files and isinstance(total_files, (int, float)):
        file_count = int(total_files)
    
    if module_count == 0 and isinstance(landing_plan, dict):
        for key, value in landing_plan.items():
            if "module" in key.lower() or "模块" in key:
                module_count += 1
    
    if file_count == 0:
        file_count = module_count * 3
    
    if "metrics" in data and isinstance(data["metrics"], dict):
        metrics = data["metrics"]
        if module_count == 0:
            module_count = metrics.get("module_count", 0)
        if file_count == 0:
            file_count = metrics.get("file_count", 0)
    
    return {
        "模块数": {"value": int(module_count) if module_count else 0},
        "文件数": {"value": int(file_count) if file_count else 0}
    }


def extract_ide_bundle_metrics(data):
    """从IDE引导包结果中提取指标
    
    从IDE引导包生成阶段的结果数据中提取关键指标，包括文件数和规则数。
    支持多种数据结构格式，能够处理嵌套的引导包数据。
    
    数据结构适配：
    1. 优先使用标准格式：data["files"], data["rules_count"]
    2. 其次使用计数格式：data["metrics"]["file_count"]
    3. 从ide_bundle嵌套结构中提取：data["ide_bundle"]
    4. 最后使用其他格式
    
    Args:
        data: IDE引导包结果字典，可能包含以下字段：
            - files: 文件列表
            - rules_count: 规则文件数量
            - ide_bundle: 嵌套的引导包数据
            - metrics: 预计算的指标字典
    
    Returns:
        dict: 标准化的指标字典，格式为 {
            "文件数": {"value": N},
            "规则数": {"value": N}
        }
        如果数据缺失或格式错误，对应指标值为0
    
    Example:
        >>> data = {
        ...     "files": ["file1.md", "file2.md"],
        ...     "rules_count": 2
        ... }
        >>> extract_ide_bundle_metrics(data)
        {'文件数': {'value': 2}, '规则数': {'value': 2}}
    """
    file_count = 0
    rules_count = 0
    
    if not isinstance(data, dict):
        return {
            "文件数": {"value": 0},
            "规则数": {"value": 0}
        }
    
    ide_bundle = data.get("ide_bundle", {})
    
    files = data.get("files", [])
    if files and isinstance(files, list):
        file_count = len(files)
    
    rules_count_val = data.get("rules_count", 0)
    if isinstance(rules_count_val, (int, float)):
        rules_count = int(rules_count_val)
    
    if file_count == 0 and isinstance(ide_bundle, dict):
        global_bundle = ide_bundle.get("global", {})
        modules_bundle = ide_bundle.get("modules", [])
        
        if global_bundle:
            file_count += 1
            rules_count += 1
        
        if isinstance(modules_bundle, list):
            file_count += len(modules_bundle)
            rules_count += len(modules_bundle)
    
    if rules_count == 0:
        rules_count = sum(1 for f in files if "规则" in str(f) or "AGENT" in str(f))
    
    if "metrics" in data and isinstance(data["metrics"], dict):
        metrics = data["metrics"]
        if file_count == 0:
            file_count = metrics.get("file_count", 0)
        if rules_count == 0:
            rules_count = metrics.get("rules_count", 0)
    
    return {
        "文件数": {"value": int(file_count) if file_count else 0},
        "规则数": {"value": int(rules_count) if rules_count else 0}
    }

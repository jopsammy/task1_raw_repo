
file_path = r'd:\2024备份和迁移\2024备份和迁移\f复旭文件\h彗星计划相关\彗星计划\需求结构化分析工具\v1\modules\模块4_交互层模块\streamlit\ui_renderer.py'

content = '''import os
import sys
import json
import streamlit as st
import streamlit_antd_components as sac

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../../..'))
sys.path.insert(0, project_root)


def render_pipeline_steps(stages, current_stage):
    steps = []
    for idx, stage in enumerate(stages):
        status = 'wait'
        if idx == current_stage:
            status = 'process'
        elif idx + 1 &lt;= current_stage:
            status = 'finish'
        steps.append(sac.StepsItem(
            title=stage.get('title', '阶段 ' + str(idx+1)),
            description=stage.get('description', ''),
            status=status
        ))
    sac.steps(items=steps, color='blue', key='pipeline_steps_' + str(current_stage))


def render_result(result_data):
    if result_data is None:
        st.info("暂无结果")
        return
    if isinstance(result_data, dict):
        if result_data.get('success'):
            st.success(result_data.get('message', '操作成功'))
            if 'data' in result_data:
                render_json_as_card(result_data['data'], '结果数据')
        else:
            st.error(result_data.get('error', '操作失败'))
    elif isinstance(result_data, list):
        st.markdown("### 列表结果 (" + str(len(result_data)) + " 项)")
        for idx, item in enumerate(result_data, 1):
            with st.expander("项 " + str(idx), expanded=False):
                if isinstance(item, (dict, list)):
                    st.json(item)
                else:
                    st.text(item)
    elif isinstance(result_data, str):
        try:
            parsed = json.loads(result_data)
            render_json_as_card(parsed, 'JSON结果')
        except json.JSONDecodeError:
            st.markdown("### 文本结果")
            st.text(result_data)
    else:
        st.markdown("### 结果")
        st.text(str(result_data
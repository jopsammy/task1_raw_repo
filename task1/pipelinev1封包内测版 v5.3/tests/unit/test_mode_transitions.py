"""
模态切换逻辑单元测试
"""

import pytest
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from modules.模块3_UI状态代理模块.state_proxy import (
    StateProxy, 
    PipelineStatus, 
    UIMode,
    reset_state_proxy
)


class TestModeTransitions:
    """模态切换测试"""
    
    def setup_method(self):
        """每个测试方法前重置单例"""
        reset_state_proxy()
    
    def test_input_to_monitor_transition(self, mock_session_state):
        """测试INPUT -> MONITOR转换"""
        proxy = StateProxy()
        
        assert proxy.get_ui_mode() == UIMode.INPUT
        
        proxy.transition_to_mode(UIMode.MONITOR)
        
        assert proxy.get_ui_mode() == UIMode.MONITOR
    
    def test_monitor_to_review_transition(self, mock_session_state):
        """测试MONITOR -> REVIEW转换"""
        proxy = StateProxy()
        
        proxy.transition_to_mode(UIMode.MONITOR)
        proxy.transition_to_mode(UIMode.REVIEW)
        
        assert proxy.get_ui_mode() == UIMode.REVIEW
    
    def test_review_to_input_transition(self, mock_session_state):
        """测试REVIEW -> INPUT转换"""
        proxy = StateProxy()
        
        proxy.transition_to_mode(UIMode.MONITOR)
        proxy.transition_to_mode(UIMode.REVIEW)
        proxy.transition_to_mode(UIMode.INPUT)
        
        assert proxy.get_ui_mode() == UIMode.INPUT
    
    def test_full_cycle_transition(self, mock_session_state):
        """测试完整转换周期"""
        proxy = StateProxy()
        
        assert proxy.get_ui_mode() == UIMode.INPUT
        
        proxy.transition_to_mode(UIMode.MONITOR)
        assert proxy.get_ui_mode() == UIMode.MONITOR
        
        proxy.transition_to_mode(UIMode.REVIEW)
        assert proxy.get_ui_mode() == UIMode.REVIEW
        
        proxy.transition_to_mode(UIMode.INPUT)
        assert proxy.get_ui_mode() == UIMode.INPUT


class TestModeTransitionSideEffects:
    """模态转换副作用测试"""
    
    def setup_method(self):
        """每个测试方法前重置单例"""
        reset_state_proxy()
    
    def test_monitor_transition_clears_logs(self, mock_session_state):
        """测试MONITOR转换清空日志"""
        proxy = StateProxy()
        
        proxy.add_pipeline_log("旧日志", "INFO")
        assert len(proxy.get_pipeline_status()["logs"]) == 1
        
        proxy.transition_to_mode(UIMode.MONITOR)
        
        assert len(proxy.get_pipeline_status()["logs"]) == 0
    
    def test_input_transition_resets_progress(self, mock_session_state):
        """测试INPUT转换重置进度"""
        proxy = StateProxy()
        
        proxy.transition_to_mode(UIMode.MONITOR)
        proxy.update_pipeline_status(PipelineStatus.RUNNING, "测试阶段", 50, "测试")
        
        proxy.transition_to_mode(UIMode.INPUT)
        
        status = proxy.get_pipeline_status()
        assert status["status"] == PipelineStatus.IDLE.value
        assert status["progress"] == 0
        assert status["stage"] == ""


class TestModeBasedButtonVisibility:
    """基于模态的按钮可见性测试"""
    
    def setup_method(self):
        """每个测试方法前重置单例"""
        reset_state_proxy()
    
    def test_start_button_visible_in_input_mode(self, mock_session_state):
        """测试启动按钮在INPUT模式可见"""
        proxy = StateProxy()
        
        assert proxy.get_ui_mode() == UIMode.INPUT
        start_visible = (proxy.get_ui_mode() == UIMode.INPUT)
        assert start_visible is True
    
    def test_stop_button_visible_in_monitor_mode(self, mock_session_state):
        """测试停止按钮在MONITOR模式可见"""
        proxy = StateProxy()
        proxy.transition_to_mode(UIMode.MONITOR)
        
        stop_visible = (proxy.get_ui_mode() == UIMode.MONITOR)
        assert stop_visible is True
    
    def test_reset_button_visible_in_review_mode(self, mock_session_state):
        """测试重置按钮在REVIEW模式可见"""
        proxy = StateProxy()
        proxy.transition_to_mode(UIMode.MONITOR)
        proxy.transition_to_mode(UIMode.REVIEW)
        
        reset_visible = (proxy.get_ui_mode() == UIMode.REVIEW)
        assert reset_visible is True


class TestModeWithPipelineStatus:
    """模态与Pipeline状态同步测试"""
    
    def setup_method(self):
        """每个测试方法前重置单例"""
        reset_state_proxy()
    
    def test_running_pipeline_sets_monitor_mode(self, mock_session_state):
        """测试运行中Pipeline设置MONITOR模式"""
        proxy = StateProxy()
        
        proxy.transition_to_mode(UIMode.MONITOR)
        proxy.update_pipeline_status(PipelineStatus.RUNNING, "执行中", 30, "运行中")
        
        assert proxy.get_ui_mode() == UIMode.MONITOR
        assert proxy.get_pipeline_status()["status"] == PipelineStatus.RUNNING.value
    
    def test_completed_pipeline_sets_review_mode(self, mock_session_state):
        """测试完成Pipeline设置REVIEW模式"""
        proxy = StateProxy()
        
        proxy.transition_to_mode(UIMode.MONITOR)
        proxy.update_pipeline_status(PipelineStatus.COMPLETED, "完成", 100, "执行完成")
        proxy.transition_to_mode(UIMode.REVIEW)
        
        assert proxy.get_ui_mode() == UIMode.REVIEW
        assert proxy.get_pipeline_status()["status"] == PipelineStatus.COMPLETED.value
    
    def test_failed_pipeline_sets_review_mode(self, mock_session_state):
        """测试失败Pipeline设置REVIEW模式"""
        proxy = StateProxy()
        
        proxy.transition_to_mode(UIMode.MONITOR)
        proxy.update_pipeline_status(PipelineStatus.FAILED, "失败", 0, "执行失败")
        proxy.transition_to_mode(UIMode.REVIEW)
        
        assert proxy.get_ui_mode() == UIMode.REVIEW
        assert proxy.get_pipeline_status()["status"] == PipelineStatus.FAILED.value

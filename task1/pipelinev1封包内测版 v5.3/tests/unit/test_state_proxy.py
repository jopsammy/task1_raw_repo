"""
StateProxy UI状态机单元测试
"""

import pytest
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)


class TestUIModeEnum:
    """UIMode枚举测试"""
    
    def test_ui_mode_values(self):
        """测试UIMode枚举值"""
        from modules.模块3_UI状态代理模块.state_proxy import UIMode
        assert UIMode.INPUT.value == "input"
        assert UIMode.MONITOR.value == "monitor"
        assert UIMode.REVIEW.value == "review"
    
    def test_ui_mode_count(self):
        """测试UIMode枚举数量"""
        from modules.模块3_UI状态代理模块.state_proxy import UIMode
        assert len(UIMode) == 3


class TestPipelineStatusEnum:
    """PipelineStatus枚举测试"""
    
    def test_pipeline_status_values(self):
        """测试PipelineStatus枚举值"""
        from modules.模块3_UI状态代理模块.state_proxy import PipelineStatus
        assert PipelineStatus.IDLE.value == "idle"
        assert PipelineStatus.RUNNING.value == "running"
        assert PipelineStatus.PAUSED.value == "paused"
        assert PipelineStatus.COMPLETED.value == "completed"
        assert PipelineStatus.FAILED.value == "failed"


class TestStateProxyUIMode:
    """StateProxy UI模态测试"""
    
    def test_initial_ui_mode(self, mock_session_state):
        """测试初始UI模态为INPUT"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, UIMode, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        proxy.set_ui_mode(UIMode.INPUT)
        assert proxy.get_ui_mode() == UIMode.INPUT
    
    def test_set_ui_mode_to_monitor(self, mock_session_state):
        """测试设置UI模态为MONITOR"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, UIMode, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        proxy.set_ui_mode(UIMode.MONITOR)
        assert proxy.get_ui_mode() == UIMode.MONITOR
    
    def test_set_ui_mode_to_review(self, mock_session_state):
        """测试设置UI模态为REVIEW"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, UIMode, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        proxy.set_ui_mode(UIMode.REVIEW)
        assert proxy.get_ui_mode() == UIMode.REVIEW
    
    def test_transition_to_monitor(self, mock_session_state):
        """测试转换到MONITOR模态"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, UIMode, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        proxy.set_ui_mode(UIMode.INPUT)
        proxy.transition_to_mode(UIMode.MONITOR)
        assert proxy.get_ui_mode() == UIMode.MONITOR
    
    def test_transition_to_review(self, mock_session_state):
        """测试转换到REVIEW模态"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, UIMode, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        proxy.set_ui_mode(UIMode.INPUT)
        proxy.transition_to_mode(UIMode.MONITOR)
        proxy.transition_to_mode(UIMode.REVIEW)
        assert proxy.get_ui_mode() == UIMode.REVIEW
    
    def test_transition_to_input_resets_status(self, mock_session_state):
        """测试转换到INPUT模态重置状态"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, PipelineStatus, UIMode, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        proxy.set_ui_mode(UIMode.INPUT)
        proxy.transition_to_mode(UIMode.MONITOR)
        proxy.update_pipeline_status(PipelineStatus.RUNNING, "测试", 50, "测试日志")
        proxy.transition_to_mode(UIMode.INPUT)
        
        status = proxy.get_pipeline_status()
        assert status["status"] == PipelineStatus.IDLE.value
        assert status["progress"] == 0


class TestStateProxyPipelineStatus:
    """StateProxy Pipeline状态测试"""
    
    def test_update_pipeline_status(self, mock_session_state):
        """测试更新Pipeline状态"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, PipelineStatus, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        
        proxy.update_pipeline_status(
            PipelineStatus.RUNNING, 
            "需求锚定", 
            20, 
            "开始需求锚定"
        )
        
        status = proxy.get_pipeline_status()
        assert status["status"] == PipelineStatus.RUNNING.value
        assert status["stage"] == "需求锚定"
        assert status["progress"] == 20
    
    def test_add_pipeline_log(self, mock_session_state):
        """测试添加Pipeline日志"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        proxy.clear_pipeline_logs()
        
        proxy.add_pipeline_log("测试日志", "INFO", "测试阶段")
        
        status = proxy.get_pipeline_status()
        assert len(status["logs"]) >= 1
        assert status["logs"][-1]["message"] == "测试日志"
        assert status["logs"][-1]["level"] == "INFO"
    
    def test_clear_pipeline_logs(self, mock_session_state):
        """测试清空Pipeline日志"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        proxy.clear_pipeline_logs()
        proxy.add_pipeline_log("日志1", "INFO")
        proxy.add_pipeline_log("日志2", "INFO")
        proxy.clear_pipeline_logs()
        
        status = proxy.get_pipeline_status()
        assert len(status["logs"]) == 0


class TestStateProxyResults:
    """StateProxy结果存储测试"""
    
    def test_store_and_get_pipeline_result(self, mock_session_state):
        """测试存储和获取Pipeline结果"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        result = {"success": True, "data": "测试数据"}
        
        proxy.store_pipeline_result("requirement_anchoring", result)
        retrieved = proxy.get_pipeline_result("requirement_anchoring")
        
        assert retrieved == result
    
    def test_clear_pipeline_results(self, mock_session_state):
        """测试清空Pipeline结果"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        proxy.store_pipeline_result("stage1", {"data": 1})
        proxy.store_pipeline_result("stage2", {"data": 2})
        proxy.clear_pipeline_results()
        
        assert proxy.get_pipeline_result("stage1") is None
        assert proxy.get_pipeline_result("stage2") is None


class TestStateProxyMetrics:
    """StateProxy指标测试"""
    
    def test_update_tokens(self, mock_session_state):
        """测试更新Token统计"""
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        proxy.update_tokens(100)
        proxy.update_tokens(50)
        
        assert proxy.get_total_tokens() == 150
    
    def test_get_elapsed_time(self, mock_session_state):
        """测试获取耗时"""
        import time
        from modules.模块3_UI状态代理模块.state_proxy import StateProxy, UIMode, reset_state_proxy
        reset_state_proxy()
        proxy = StateProxy()
        proxy.set_ui_mode(UIMode.INPUT)
        proxy.transition_to_mode(UIMode.MONITOR)
        
        time.sleep(0.1)
        elapsed = proxy.get_elapsed_time()
        
        assert elapsed >= 0.1

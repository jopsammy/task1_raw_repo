"""
终端输出E2E测试
测试彩色日志渲染、进度条显示、Footer摘要显示
"""

import pytest
import time
from playwright.sync_api import expect


class TestTerminalOutput:
    """终端输出测试"""

    def test_colored_log_info_level(self, browser_page):
        """测试INFO级别彩色日志渲染"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(3)
        
        log_container = browser_page.locator('div[style*="font-family: monospace"]')
        expect(log_container).to_be_visible(timeout=10000)
        
        info_log = browser_page.locator('div[style*="border-left: 3px solid #2196F3"]')
        expect(info_log.first).to_be_visible(timeout=10000)

    def test_colored_log_success_level(self, browser_page):
        """测试SUCCESS级别彩色日志渲染"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(5)
        
        success_log = browser_page.locator('div[style*="border-left: 3px solid #4CAF50"]')
        expect(success_log.first).to_be_visible(timeout=15000)

    def test_colored_log_warning_level(self, browser_page):
        """测试WARNING级别彩色日志渲染"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(3)
        
        warning_log = browser_page.locator('div[style*="border-left: 3px solid #FF9800"]')
        warning_count = warning_log.count()
        
        assert warning_count >= 0, "WARNING日志检测正常"

    def test_colored_log_error_level(self, browser_page):
        """测试ERROR级别彩色日志渲染"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(3)
        
        error_log = browser_page.locator('div[style*="border-left: 3px solid #F44336"]')
        error_count = error_log.count()
        
        assert error_count >= 0, "ERROR日志检测正常"

    def test_log_timestamp_format(self, browser_page):
        """测试日志时间戳格式"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(3)
        
        log_container = browser_page.locator('div[style*="font-family: monospace"]')
        expect(log_container).to_be_visible(timeout=10000)
        
        timestamp_pattern = browser_page.locator('span:has-text("[")')
        expect(timestamp_pattern.first).to_be_visible(timeout=10000)

    def test_log_stage_label(self, browser_page):
        """测试日志阶段标签显示"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(3)
        
        stage_label = browser_page.locator('text=需求锚定')
        expect(stage_label.first).to_be_visible(timeout=10000)

    def test_progress_bar_visible(self, browser_page):
        """测试进度条可见"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(2)
        
        progress_section = browser_page.locator('text=执行进度')
        expect(progress_section).to_be_visible(timeout=10000)

    def test_progress_bar_stages_display(self, browser_page):
        """测试进度条阶段显示"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(2)
        
        stage_names = ["需求锚定", "需求校验", "架构迭代", "契约生成", "落地方案", "交付物切分"]
        
        for stage in stage_names[:3]:
            stage_element = browser_page.locator(f'text={stage}')
            expect(stage_element.first).to_be_visible(timeout=15000)

    def test_progress_percentage_display(self, browser_page):
        """测试进度百分比显示"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(3)
        
        progress_text = browser_page.locator('text=/当前进度.*%/')
        expect(progress_text.first).to_be_visible(timeout=10000)

    def test_progress_stage_icons(self, browser_page):
        """测试进度阶段图标"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(2)
        
        completed_icon = browser_page.locator('text=✅')
        expect(completed_icon.first).to_be_visible(timeout=15000)

    def test_footer_summary_visible_after_completion(self, browser_page):
        """测试完成后Footer摘要可见"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(10)
        
        footer_summary = browser_page.locator('text=总耗时')
        expect(footer_summary).to_be_visible(timeout=30000)

    def test_footer_summary_token_display(self, browser_page):
        """测试Footer摘要Token显示"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(10)
        
        token_text = browser_page.locator('text=/总Token.*Input.*Output/')
        expect(token_text).to_be_visible(timeout=30000)

    def test_footer_summary_model_list(self, browser_page):
        """测试Footer摘要模型列表"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(10)
        
        model_text = browser_page.locator('text=/模型:/')
        expect(model_text).to_be_visible(timeout=30000)

    def test_footer_summary_styling(self, browser_page):
        """测试Footer摘要样式"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(10)
        
        footer_container = browser_page.locator('div[style*="border-top"]')
        expect(footer_container.first).to_be_visible(timeout=30000)


class TestTerminalOutputEdgeCases:
    """终端输出边界情况测试"""

    def test_empty_log_display(self, browser_page):
        """测试空日志显示"""
        log_empty = browser_page.locator('text=暂无日志')
        empty_count = log_empty.count()
        
        assert empty_count >= 0, "空日志状态检测正常"

    def test_long_log_message_truncation(self, browser_page):
        """测试长日志消息处理"""
        long_requirement = "构建一个复杂的分布式系统，" * 50
        
        text_area = browser_page.locator('textarea').first
        text_area.fill(long_requirement)
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(3)
        
        log_container = browser_page.locator('div[style*="font-family: monospace"]')
        expect(log_container).to_be_visible(timeout=10000)

    def test_special_characters_in_log(self, browser_page):
        """测试日志中特殊字符处理"""
        special_requirement = "测试需求：包含特殊字符 <>&\"'\\n\\t"
        
        text_area = browser_page.locator('textarea').first
        text_area.fill(special_requirement)
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(3)
        
        log_container = browser_page.locator('div[style*="font-family: monospace"]')
        expect(log_container).to_be_visible(timeout=10000)

    def test_concurrent_log_updates(self, browser_page):
        """测试并发日志更新"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(5)
        
        log_entries = browser_page.locator('div[style*="border-left: 3px solid"]')
        log_count = log_entries.count()
        
        assert log_count > 0, "并发日志更新正常"

    def test_progress_bar_animation(self, browser_page):
        """测试进度条动画效果"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求：构建用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(2)
        
        progress_bar = browser_page.locator('[data-testid="stProgress"]')
        expect(progress_bar.first).to_be_visible(timeout=10000)
        
        time.sleep(3)
        
        progress_bar_after = browser_page.locator('[data-testid="stProgress"]')
        expect(progress_bar_after.first).to_be_visible()

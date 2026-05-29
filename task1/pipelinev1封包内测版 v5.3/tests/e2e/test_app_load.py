"""
应用加载E2E测试
"""

import pytest
from playwright.sync_api import expect


class TestAppLoad:
    """应用加载测试"""
    
    def test_app_loads_successfully(self, browser_page):
        """测试应用成功加载"""
        expect(browser_page).to_have_title("需求结构化分析管道")
    
    def test_sidebar_visible(self, browser_page):
        """测试侧边栏可见"""
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
    
    def test_initial_mode_is_input(self, browser_page):
        """测试初始模态为INPUT"""
        heading = browser_page.get_by_role("heading", name="需求锚定台")
        expect(heading).to_be_visible()
    
    def test_start_button_visible_in_input_mode(self, browser_page):
        """测试INPUT模式下启动按钮可见"""
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        expect(start_button).to_be_visible()
    
    def test_requirement_text_area_visible(self, browser_page):
        """测试需求输入框可见"""
        text_area = browser_page.locator('textarea').first
        expect(text_area).to_be_visible()
    
    def test_api_management_visible(self, browser_page):
        """测试API管理可见"""
        api_management = browser_page.get_by_text("API 管理")
        expect(api_management).to_be_visible()
        
        save_button = browser_page.get_by_role("button", name="保存配置")
        expect(save_button).to_be_visible()
    
    def test_old_config_options_not_visible(self, browser_page):
        """测试旧配置选项不可见"""
        old_config_section = browser_page.get_by_text("配置选项")
        expect(old_config_section).not_to_be_visible()

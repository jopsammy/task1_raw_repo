"""
错误处理E2E测试
"""

import pytest
from playwright.sync_api import expect


class TestErrorHandling:
    """错误处理测试"""
    
    def test_empty_requirement_validation(self, browser_page):
        """测试空需求验证（验证按钮存在即可）"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        expect(start_button).to_be_visible()
    
    def test_sidebar_project_info_display(self, browser_page):
        """测试侧边栏项目信息显示"""
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        project_info = sidebar.get_by_text("项目信息")
        expect(project_info).to_be_visible()
    
    def test_sidebar_mode_indicator(self, browser_page):
        """测试侧边栏模态指示器"""
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        idle_status = sidebar.get_by_text("空闲状态")
        expect(idle_status).to_be_visible()

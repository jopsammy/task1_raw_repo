"""
应用模式E2E测试
测试三态模态架构：INPUT/MONITOR/REVIEW
"""

import pytest
from playwright.sync_api import expect


class TestAppModes:
    """三态模态架构测试"""

    def test_input_mode_render(self, browser_page):
        """测试INPUT模态渲染"""
        heading = browser_page.get_by_role("heading", name="需求锚定台")
        expect(heading).to_be_visible()
        
        requirement_label = browser_page.get_by_text("输入您的需求")
        expect(requirement_label).to_be_visible()
        
        text_area = browser_page.locator('textarea').first
        expect(text_area).to_be_visible()
        
        api_management = browser_page.get_by_text("API 管理")
        expect(api_management).to_be_visible()
        
        save_button = browser_page.get_by_role("button", name="保存配置")
        expect(save_button).to_be_visible()
        
        old_config_section = browser_page.get_by_text("配置选项")
        expect(old_config_section).not_to_be_visible()

    def test_sidebar_no_api_management(self, browser_page):
        """测试侧边栏不显示API管理"""
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        sidebar_api_management = sidebar.get_by_text("API 管理")
        expect(sidebar_api_management).not_to_be_visible()
        
        control_heading = sidebar.get_by_text("全局控制")
        expect(control_heading).to_be_visible()
        
        project_info = sidebar.get_by_text("项目信息")
        expect(project_info).to_be_visible()

    def test_input_to_monitor_transition(self, browser_page):
        """测试INPUT → MONITOR状态流转"""
        text_area = browser_page.locator('textarea').first
        test_requirement = "构建一个用户管理系统，包含用户注册、登录、权限管理功能"
        text_area.fill(test_requirement)
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        expect(start_button).to_be_visible()
        start_button.click()
        
        browser_page.wait_for_timeout(2000)
        
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        running_indicator = browser_page.locator('text=运行中')
        expect(running_indicator).to_be_visible(timeout=5000)

    def test_monitor_to_review_transition(self, browser_page):
        """测试MONITOR → REVIEW状态流转"""
        text_area = browser_page.locator('textarea').first
        test_requirement = "构建一个简单的用户登录功能"
        text_area.fill(test_requirement)
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=10000)
        
        progress_section = browser_page.locator('text=执行进度')
        expect(progress_section).to_be_visible()
        
        log_section = browser_page.locator('text=实时日志流')
        expect(log_section).to_be_visible()

    def test_sidebar_controls(self, browser_page):
        """测试侧边栏控制按钮交互"""
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        control_heading = sidebar.get_by_text("全局控制")
        expect(control_heading).to_be_visible()
        
        idle_status = sidebar.locator('text=空闲状态')
        expect(idle_status).to_be_visible()
        
        start_button = sidebar.get_by_role("button", name="启动 Pipeline")
        expect(start_button).to_be_visible()
        
        project_info = sidebar.get_by_text("项目信息")
        expect(project_info).to_be_visible()

    def test_reset_functionality(self, browser_page):
        """测试重置功能"""
        text_area = browser_page.locator('textarea').first
        test_requirement = "测试需求内容"
        text_area.fill(test_requirement)
        
        expect(text_area).to_have_value(test_requirement)
        
        text_area.fill("")
        expect(text_area).to_have_value("")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        expect(start_button).to_be_visible()

    def test_mode_state_persistence(self, browser_page):
        """测试模态状态持久化"""
        heading = browser_page.get_by_role("heading", name="需求锚定台")
        expect(heading).to_be_visible()
        
        test_requirement = "持久化测试需求"
        text_area = browser_page.locator('textarea').first
        text_area.fill(test_requirement)

    def test_input_validation(self, browser_page):
        """测试输入验证"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        expect(start_button).to_be_visible()
        
        text_area.fill("   ")
        expect(text_area).to_have_value("   ")
        
        text_area.fill("有效的需求描述")
        expect(text_area).to_have_value("有效的需求描述")

    def test_character_counter(self, browser_page):
        """测试字符计数器"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试")
        
        char_count = browser_page.get_by_text("字符数:")
        expect(char_count).to_be_visible()
        
        text_area.fill("更长的测试需求内容")
        expect(char_count).to_be_visible()

    def test_api_management_visibility(self, browser_page):
        """测试API管理可见性"""
        api_management = browser_page.get_by_text("API 管理")
        expect(api_management).to_be_visible()
        
        save_button = browser_page.get_by_role("button", name="保存配置")
        expect(save_button).to_be_visible()

    def test_pipeline_start_from_input_mode(self, browser_page):
        """测试从INPUT模式启动Pipeline"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试启动Pipeline的需求")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(1500)
        
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()

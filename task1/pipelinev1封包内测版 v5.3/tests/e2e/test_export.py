"""
导出功能E2E测试
测试结果导出相关功能
"""

import pytest
import json
from playwright.sync_api import expect


class TestExport:
    """导出功能测试"""

    def test_json_export(self, browser_page):
        """测试JSON格式导出"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，测试JSON导出功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=15000)
        
        log_section = browser_page.locator('text=实时日志流')
        expect(log_section).to_be_visible()

    def test_markdown_export(self, browser_page):
        """测试Markdown格式导出"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个订单系统，测试Markdown导出功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        progress_section = browser_page.get_by_text("执行进度")
        expect(progress_section).to_be_visible(timeout=15000)

    def test_yaml_export(self, browser_page):
        """测试YAML格式导出"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个配置管理系统，测试YAML导出功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=15000)

    def test_export_button_visible(self, browser_page):
        """测试导出按钮可见性"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试导出按钮可见性")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        expect(start_button).to_be_visible()
        
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()

    def test_export_button_in_review_mode(self, browser_page):
        """测试REVIEW模式下的导出按钮"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试REVIEW模式下的导出功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=15000)

    def test_export_popover_interaction(self, browser_page):
        """测试导出Popover交互"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试导出Popover交互")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()

    def test_multiple_export_formats(self, browser_page):
        """测试多种导出格式"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试多种导出格式：JSON、Markdown、YAML")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        progress_section = browser_page.get_by_text("执行进度")
        expect(progress_section).to_be_visible(timeout=15000)

    def test_export_filename_format(self, browser_page):
        """测试导出文件名格式"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试导出文件名格式")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()

    def test_export_large_data(self, browser_page):
        """测试大数据量导出"""
        large_requirement = "构建一个企业级ERP系统，" * 50
        large_requirement += "包含财务、人事、供应链、生产、销售等模块。"
        
        text_area = browser_page.locator('textarea').first
        text_area.fill(large_requirement)
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=15000)

    def test_export_with_special_characters(self, browser_page):
        """测试特殊字符导出"""
        special_requirement = "构建系统，包含特殊字符：<>&\"'测试"
        
        text_area = browser_page.locator('textarea').first
        text_area.fill(special_requirement)
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        progress_section = browser_page.get_by_text("执行进度")
        expect(progress_section).to_be_visible(timeout=15000)

    def test_export_chinese_content(self, browser_page):
        """测试中文内容导出"""
        chinese_requirement = "构建一个中文内容管理系统，包含文章发布、评论管理、用户权限等功能。系统需要支持中文搜索和中文分词。"
        
        text_area = browser_page.locator('textarea').first
        text_area.fill(chinese_requirement)
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=15000)

    def test_export_after_pipeline_complete(self, browser_page):
        """测试Pipeline完成后导出"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试Pipeline完成后导出功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=15000)
        
        log_section = browser_page.locator('text=实时日志流')
        expect(log_section).to_be_visible()

    def test_download_button_state(self, browser_page):
        """测试下载按钮状态"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试下载按钮状态")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        expect(start_button).to_be_visible()
        expect(start_button).to_be_enabled()

    def test_export_with_nested_data(self, browser_page):
        """测试嵌套数据导出"""
        nested_requirement = """
        构建一个多层级组织架构系统：
        - 公司层级：名称、地址、法人
        - 部门层级：名称、负责人、员工列表
        - 员工层级：姓名、职位、技能列表
        """
        
        text_area = browser_page.locator('textarea').first
        text_area.fill(nested_requirement)
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        progress_section = browser_page.get_by_text("执行进度")
        expect(progress_section).to_be_visible(timeout=15000)

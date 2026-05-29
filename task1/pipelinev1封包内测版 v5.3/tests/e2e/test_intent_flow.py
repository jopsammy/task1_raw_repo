"""
意图定义模态E2E测试
"""

import pytest
from playwright.sync_api import expect


class TestIntentMode:
    """意图定义模态测试"""
    
    def test_requirement_input(self, browser_page):
        """测试需求输入"""
        text_area = browser_page.locator('textarea').first
        
        test_requirement = "构建一个用户管理系统，包含用户注册、登录、权限管理功能"
        text_area.fill(test_requirement)
        
        expect(text_area).to_have_value(test_requirement)
    
    def test_provider_selection(self, browser_page):
        """测试提供商选择（Streamlit使用自定义combobox）"""
        provider_combobox = browser_page.get_by_label("LLM 提供商")
        expect(provider_combobox).to_be_visible()
    
    def test_model_input(self, browser_page):
        """测试模型输入"""
        model_input = browser_page.get_by_label("模型名称")
        
        model_input.fill("gpt-4")
        expect(model_input).to_have_value("gpt-4")
    
    def test_character_count_display(self, browser_page):
        """测试字符数显示"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试需求")
        
        caption = browser_page.get_by_text("字符数:")
        expect(caption).to_be_visible()
    
    def test_start_button_disabled_without_requirement(self, browser_page):
        """测试无需求时启动按钮状态"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        expect(start_button).to_be_visible()

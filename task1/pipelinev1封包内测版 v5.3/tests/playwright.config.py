"""
Playwright配置文件
用于E2E测试的浏览器自动化配置
"""

import os
from playwright.sync_api import sync_playwright

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

PLAYWRIGHT_CONFIG = {
    "headless": True,
    "browser_type": "chromium",
    "slow_mo": 0,
    "timeout": 30000,
    "viewport": {
        "width": 1280,
        "height": 720
    },
    "screenshot_on_failure": True,
    "video_on_failure": False,
    "trace_on_failure": True,
    "base_url": "http://localhost:8501",
    "test_dirs": [
        os.path.join(PROJECT_ROOT, "tests", "e2e")
    ]
}


def get_browser_context_options():
    """
    获取浏览器上下文配置选项
    
    Returns:
        dict: 浏览器上下文配置
    """
    return {
        "viewport": PLAYWRIGHT_CONFIG["viewport"],
        "base_url": PLAYWRIGHT_CONFIG["base_url"],
        "ignore_https_errors": True,
        "java_script_enabled": True,
    }


def get_launch_options():
    """
    获取浏览器启动配置选项
    
    Returns:
        dict: 浏览器启动配置
    """
    return {
        "headless": PLAYWRIGHT_CONFIG["headless"],
        "slow_mo": PLAYWRIGHT_CONFIG["slow_mo"],
        "timeout": PLAYWRIGHT_CONFIG["timeout"],
    }


def create_browser_context(playwright):
    """
    创建浏览器上下文
    
    Args:
        playwright: Playwright实例
        
    Returns:
        tuple: (browser, context, page)
    """
    browser_type = getattr(playwright, PLAYWRIGHT_CONFIG["browser_type"])
    browser = browser_type.launch(**get_launch_options())
    context = browser.new_context(**get_browser_context_options())
    page = context.new_page()
    page.set_default_timeout(PLAYWRIGHT_CONFIG["timeout"])
    return browser, context, page


class PlaywrightTestHelper:
    """
    Playwright测试辅助类
    提供常用的E2E测试操作封装
    """
    
    def __init__(self, page):
        """
        初始化测试辅助类
        
        Args:
            page: Playwright页面对象
        """
        self.page = page
    
    def wait_for_streamlit_ready(self, timeout=30000):
        """
        等待Streamlit应用加载完成
        
        Args:
            timeout: 超时时间（毫秒）
        """
        self.page.wait_for_selector('[data-testid="stApp"]', timeout=timeout)
        self.page.wait_for_load_state("networkidle", timeout=timeout)
    
    def click_button(self, button_text, timeout=10000):
        """
        点击指定文本的按钮
        
        Args:
            button_text: 按钮文本
            timeout: 超时时间（毫秒）
        """
        self.page.click(f'button:has-text("{button_text}")', timeout=timeout)
    
    def fill_input(self, label, value, timeout=10000):
        """
        填充输入框
        
        Args:
            label: 输入框标签
            value: 填充值
            timeout: 超时时间（毫秒）
        """
        self.page.fill(f'label:has-text("{label}") + input', value, timeout=timeout)
    
    def get_element_text(self, selector, timeout=10000):
        """
        获取元素文本内容
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            str: 元素文本内容
        """
        element = self.page.wait_for_selector(selector, timeout=timeout)
        return element.text_content() if element else ""
    
    def take_screenshot(self, name):
        """
        截取屏幕截图
        
        Args:
            name: 截图文件名
        """
        screenshots_dir = os.path.join(PROJECT_ROOT, "tests", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshots_dir, f"{name}.png")
        self.page.screenshot(path=screenshot_path)
        return screenshot_path
    
    def wait_for_text(self, text, timeout=10000):
        """
        等待文本出现
        
        Args:
            text: 等待的文本
            timeout: 超时时间（毫秒）
        """
        self.page.wait_for_selector(f'text={text}', timeout=timeout)
    
    def is_element_visible(self, selector, timeout=5000):
        """
        检查元素是否可见
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            bool: 元素是否可见
        """
        try:
            element = self.page.wait_for_selector(selector, timeout=timeout, state="visible")
            return element is not None
        except Exception:
            return False

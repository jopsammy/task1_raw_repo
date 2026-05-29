"""
评审可视化E2E测试
测试成果审查台的视觉展示功能
"""

import pytest
from playwright.sync_api import expect


class TestReviewVisual:
    """成果审查台视觉测试"""

    def test_tabs_render(self, browser_page):
        """测试Tab页面正确渲染"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=15000)
        
        progress_bar = browser_page.locator('[data-testid="stProgress"]')
        expect(progress_bar).to_be_visible()

    def test_l1_metrics_visible(self, browser_page):
        """测试L1指标区域可见性"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试L1指标显示")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        metrics_section = sidebar.locator('[data-testid="stMetric"]')
        expect(metrics_section.first).to_be_visible(timeout=10000)

    def test_l3_raw_stub_collapsed(self, browser_page):
        """测试L3原始数据expander默认折叠"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试原始数据折叠")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        expander = browser_page.locator('[data-testid="stExpander"]')
        expect(expander.first).to_be_visible(timeout=10000)

    def test_metadata_badges_display(self, browser_page):
        """测试元数据徽章显示"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试元数据徽章")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        token_metric = sidebar.get_by_text("Token消耗")
        expect(token_metric).to_be_visible(timeout=10000)

    def test_mermaid_flow_render(self, browser_page):
        """测试Mermaid流程图渲染"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个订单处理系统，包含下单、支付、发货流程")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=15000)
        
        log_section = browser_page.locator('text=实时日志流')
        expect(log_section).to_be_visible()

    def test_api_browser_style(self, browser_page):
        """测试API浏览器风格展示"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个RESTful API服务")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        running_status = sidebar.locator('text=运行中')
        expect(running_status).to_be_visible(timeout=10000)

    def test_progress_bar_animation(self, browser_page):
        """测试进度条动画"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试进度条动画")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(2000)
        
        progress = browser_page.locator('[data-testid="stProgress"]')
        expect(progress).to_be_visible(timeout=10000)

    def test_colored_logs_display(self, browser_page):
        """测试彩色日志展示"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试彩色日志展示")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        log_section = browser_page.get_by_text("实时日志流")
        expect(log_section).to_be_visible(timeout=10000)

    def test_stage_progress_indicators(self, browser_page):
        """测试阶段进度指示器"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试阶段进度指示器")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        progress_heading = browser_page.get_by_text("执行进度")
        expect(progress_heading).to_be_visible(timeout=10000)

    def test_footer_summary_display(self, browser_page):
        """测试Footer摘要显示"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试Footer摘要")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        elapsed_metric = sidebar.get_by_text("运行耗时")
        expect(elapsed_metric).to_be_visible(timeout=10000)

    def test_solution_comparison_matrix(self, browser_page):
        """测试方案对比矩阵渲染"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个高并发系统，需要对比多种架构方案")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=15000)

    def test_domain_objects_table(self, browser_page):
        """测试领域对象表格渲染"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个电商系统，包含用户、商品、订单等实体")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        progress_section = browser_page.get_by_text("执行进度")
        expect(progress_section).to_be_visible(timeout=15000)

    def test_schema_tree_render(self, browser_page):
        """测试数据模型树渲染"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个数据模型，包含嵌套对象和数组")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()

    def test_review_mode_complete_flow(self, browser_page):
        """测试REVIEW模式完整流程"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("完整测试REVIEW模式流程")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(5000)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=15000)
        
        log_section = browser_page.locator('text=实时日志流')
        expect(log_section).to_be_visible()

    def test_export_buttons_in_tabs(self, browser_page):
        """测试Tab页中的导出按钮"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("测试导出按钮")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        browser_page.wait_for_timeout(3000)
        
        sidebar = browser_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()

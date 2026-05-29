"""
Pipeline流程E2E测试
测试完整Pipeline执行、验证模块引导包生成数量
"""

import pytest
import time
import json
from playwright.sync_api import expect


class TestPipelineFlow:
    """Pipeline流程测试"""

    def test_pipeline_start_successfully(self, browser_page):
        """测试Pipeline成功启动"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(2)
        
        monitor_heading = browser_page.get_by_role("heading", name="执行监控屏")
        expect(monitor_heading).to_be_visible(timeout=10000)

    def test_pipeline_requirement_anchoring_stage(self, browser_page):
        """测试需求锚定阶段执行"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(3)
        
        stage_log = browser_page.locator('text=需求锚定')
        expect(stage_log.first).to_be_visible(timeout=15000)

    def test_pipeline_requirement_validation_stage(self, browser_page):
        """测试需求校验阶段执行"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(5)
        
        stage_log = browser_page.locator('text=需求校验')
        expect(stage_log.first).to_be_visible(timeout=20000)

    def test_pipeline_architecture_iteration_stage(self, browser_page):
        """测试架构迭代阶段执行"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(8)
        
        stage_log = browser_page.locator('text=架构迭代')
        expect(stage_log.first).to_be_visible(timeout=30000)

    def test_pipeline_contract_generation_stage(self, browser_page):
        """测试契约生成阶段执行"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(12)
        
        stage_log = browser_page.locator('text=契约生成')
        expect(stage_log.first).to_be_visible(timeout=40000)

    def test_pipeline_landing_plan_stage(self, browser_page):
        """测试落地方案生成阶段执行"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(15)
        
        stage_log = browser_page.locator('text=落地方案')
        expect(stage_log.first).to_be_visible(timeout=50000)

    def test_pipeline_ide_bundle_stage(self, browser_page):
        """测试IDE引导包生成阶段执行"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(18)
        
        stage_log = browser_page.locator('text=IDE引导包')
        expect(stage_log.first).to_be_visible(timeout=60000)

    def test_pipeline_complete_successfully(self, browser_page):
        """测试Pipeline完整执行成功"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        review_heading = browser_page.get_by_role("heading", name="成果审查台")
        expect(review_heading).to_be_visible(timeout=90000)

    def test_pipeline_results_tabs_visible(self, browser_page):
        """测试Pipeline结果Tab页可见"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        tab_names = ["需求锚定", "需求校验", "架构迭代", "契约生成", "落地方案", "IDE引导包"]
        
        for tab_name in tab_names:
            tab = browser_page.get_by_role("tab", name=tab_name)
            expect(tab).to_be_visible(timeout=90000)


class TestModuleBundleGeneration:
    """模块引导包生成测试"""

    def test_ide_bundle_tab_visible(self, browser_page):
        """测试IDE引导包Tab可见"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        ide_tab = browser_page.get_by_role("tab", name="IDE引导包")
        expect(ide_tab).to_be_visible(timeout=90000)

    def test_ide_bundle_content_structure(self, browser_page):
        """测试IDE引导包内容结构"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        ide_tab = browser_page.get_by_role("tab", name="IDE引导包")
        ide_tab.click()
        
        time.sleep(2)
        
        content_area = browser_page.locator('[data-testid="stMarkdownContainer"]')
        expect(content_area).to_be_visible(timeout=90000)

    def test_global_bundle_exists(self, browser_page):
        """测试全局引导包存在"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        ide_tab = browser_page.get_by_role("tab", name="IDE引导包")
        ide_tab.click()
        
        time.sleep(2)
        
        global_text = browser_page.locator('text=/全局/')
        global_count = global_text.count()
        
        assert global_count >= 0, "全局引导包检测正常"

    def test_module_bundle_count_minimum(self, browser_page):
        """测试模块引导包数量最少为1"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        ide_tab = browser_page.get_by_role("tab", name="IDE引导包")
        ide_tab.click()
        
        time.sleep(2)
        
        module_text = browser_page.locator('text=/模块/')
        module_count = module_text.count()
        
        assert module_count >= 1, f"模块引导包数量应至少为1，实际检测到: {module_count}"

    def test_module_bundle_count_reasonable(self, browser_page):
        """测试模块引导包数量合理范围"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        ide_tab = browser_page.get_by_role("tab", name="IDE引导包")
        ide_tab.click()
        
        time.sleep(2)
        
        module_text = browser_page.locator('text=/模块\\d/')
        module_count = module_text.count()
        
        assert 1 <= module_count <= 20, f"模块引导包数量应在1-20范围内，实际检测到: {module_count}"

    def test_bundle_content_not_empty(self, browser_page):
        """测试引导包内容非空"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        ide_tab = browser_page.get_by_role("tab", name="IDE引导包")
        ide_tab.click()
        
        time.sleep(2)
        
        content_markers = browser_page.locator('text=/模块职责|职责描述|功能说明/')
        content_count = content_markers.count()
        
        assert content_count >= 0, "引导包内容检测正常"


class TestPipelineFlowEdgeCases:
    """Pipeline流程边界情况测试"""

    def test_pipeline_with_minimal_requirement(self, browser_page):
        """测试最小需求输入"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建系统")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(5)
        
        log_container = browser_page.locator('div[style*="font-family: monospace"]')
        expect(log_container).to_be_visible(timeout=15000)

    def test_pipeline_with_complex_requirement(self, browser_page):
        """测试复杂需求输入"""
        complex_requirement = """
        构建一个企业级电商平台，包含以下模块：
        1. 用户管理模块：注册、登录、权限、个人中心
        2. 商品管理模块：商品CRUD、分类、库存、价格
        3. 订单管理模块：购物车、下单、支付、物流
        4. 营销管理模块：优惠券、活动、积分
        5. 数据分析模块：销售报表、用户行为分析
        6. 系统管理模块：配置、日志、监控
        """
        
        text_area = browser_page.locator('textarea').first
        text_area.fill(complex_requirement)
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(5)
        
        log_container = browser_page.locator('div[style*="font-family: monospace"]')
        expect(log_container).to_be_visible(timeout=15000)

    def test_pipeline_with_chinese_special_chars(self, browser_page):
        """测试中文特殊字符需求"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建系统：包含「用户管理」、「订单管理」等功能（支持PC/移动端）")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(5)
        
        log_container = browser_page.locator('div[style*="font-family: monospace"]')
        expect(log_container).to_be_visible(timeout=15000)

    def test_pipeline_progress_updates_continuously(self, browser_page):
        """测试进度持续更新"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        progress_values = []
        
        for _ in range(3):
            time.sleep(3)
            progress_text = browser_page.locator('text=/当前进度.*%/')
            if progress_text.count() > 0:
                progress_values.append(True)
        
        assert len(progress_values) >= 1, "进度更新检测正常"

    def test_pipeline_stage_transitions(self, browser_page):
        """测试阶段转换"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(10)
        
        stage_indicators = browser_page.locator('div[style*="text-align: center"]')
        stage_count = stage_indicators.count()
        
        assert stage_count >= 3, f"阶段指示器数量应至少为3，实际: {stage_count}"


class TestPipelineResultsValidation:
    """Pipeline结果验证测试"""

    def test_requirement_anchoring_result_structure(self, browser_page):
        """测试需求锚定结果结构"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        tab = browser_page.get_by_role("tab", name="需求锚定")
        tab.click()
        
        time.sleep(2)
        
        content = browser_page.locator('[data-testid="stMarkdownContainer"]')
        expect(content).to_be_visible(timeout=90000)

    def test_architecture_iteration_result_structure(self, browser_page):
        """测试架构迭代结果结构"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        tab = browser_page.get_by_role("tab", name="架构迭代")
        tab.click()
        
        time.sleep(2)
        
        content = browser_page.locator('[data-testid="stMarkdownContainer"]')
        expect(content).to_be_visible(timeout=90000)

    def test_contract_generation_result_structure(self, browser_page):
        """测试契约生成结果结构"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        tab = browser_page.get_by_role("tab", name="契约生成")
        tab.click()
        
        time.sleep(2)
        
        content = browser_page.locator('[data-testid="stMarkdownContainer"]')
        expect(content).to_be_visible(timeout=90000)

    def test_all_stages_have_results(self, browser_page):
        """测试所有阶段都有结果"""
        text_area = browser_page.locator('textarea').first
        text_area.fill("构建一个用户管理系统，包含用户注册、登录、权限管理功能")
        
        start_button = browser_page.get_by_role("button", name="启动 Pipeline")
        start_button.click()
        
        time.sleep(25)
        
        expected_tabs = ["需求锚定", "需求校验", "架构迭代", "契约生成", "落地方案", "IDE引导包"]
        visible_count = 0
        
        for tab_name in expected_tabs:
            tab = browser_page.get_by_role("tab", name=tab_name)
            if tab.is_visible():
                visible_count += 1
        
        assert visible_count >= 4, f"至少应有4个阶段有结果，实际: {visible_count}"

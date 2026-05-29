"""
模拟 CLI 测试脚本
用于快速测试 rich_console 和 cli_handler 的新功能
"""

import os
import sys
import time
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from modules.模块4_交互层模块.cli.rich_console import get_rich_console


def test_live_display():
    """测试 live_display 功能"""
    console = get_rich_console()
    
    console.show_banner()
    console.log_info("开始模拟 Pipeline 执行...")
    
    final_metrics = {
        "total_tokens": 154200,
        "input_tokens": 98000,
        "output_tokens": 56200,
        "files_generated": 12,
        "models_used": ["seed2.0", "gemini3", "qwen3max"],
        "providers_used": ["LLM1", "LLM2", "LLM3"],
        "provider_models": {"LLM1": ["doubao-seed-1-6-flash-250828"], "LLM2": ["qwen3.5-plus"], "LLM3": ["gemini-3.1-pro"]}
    }
    
    with console.live_display(mode="auto", description="模拟Pipeline执行中...") as (update_log, update_progress, update_metrics):
        update_log("开始执行Pipeline...", "INFO")
        update_log("需求长度: 16 字符", "INFO")
        update_log("项目ID: 20260309_test", "INFO")
        
        update_metrics(final_metrics)
        
        stages = [
            ("pipeline_start", "Pipeline启动", 0, 10),
            ("requirement_anchoring", "需求锚定阶段", 10, 30),
            ("requirement_validation", "需求校验阶段", 30, 50),
            ("architecture_iteration", "架构迭代阶段", 50, 70),
            ("contract_generation", "契约生成阶段", 70, 90),
            ("landing_plan_generation", "落地方案生成阶段", 90, 98),
            ("ide_bundle_generation", "IDE引导包生成阶段", 98, 100)
        ]
        
        for stage_name, stage_desc, start_p, end_p in stages:
            update_log(f"开始{stage_desc}", "INFO", stage_name)
            
            for p in range(start_p, end_p + 1):
                update_progress(p)
                time.sleep(0.1)
            
            update_log(f"{stage_desc}完成", "SUCCESS", stage_name)
    
    console.log_success("模拟 Pipeline 执行成功！耗时: 33.48 秒")
    
    results = {
        "requirement_anchoring": {"success": True},
        "requirement_validation": {"success": True},
        "architecture_iteration": {"success": True},
        "contract_generation": {"success": True},
        "landing_plan_generation": {"success": True},
        "ide_bundle_generation": {"success": True}
    }
    
    summary_data = []
    for stage, stage_result in results.items():
        status = "✅" if stage_result.get("success") else "❌"
        summary_data.append({"阶段": stage, "状态": status})
    console.show_table(summary_data, title="执行摘要")
    
    console.print_footer_summary(33.48, final_metrics)


def test_plain_mode():
    """测试 plain 模式"""
    print("\n" + "="*80)
    print("测试 PLAIN 模式")
    print("="*80)
    
    console = get_rich_console()
    
    with console.live_display(mode="plain", description="测试") as (update_log, update_progress, update_metrics):
        update_log("这是 plain 模式的日志", "INFO")
        update_log("Plain 模式适合 CI/CD 环境", "SUCCESS")
    
    print("PLAIN 模式测试完成")


def test_quiet_mode():
    """测试 quiet 模式"""
    print("\n" + "="*80)
    print("测试 QUIET 模式")
    print("="*80)
    
    console = get_rich_console()
    
    with console.live_display(mode="quiet", description="测试") as (update_log, update_progress, update_metrics):
        update_log("这条日志不会显示", "INFO")
        update_progress(50)
        update_metrics({"total_tokens": 1000})
    
    print("QUIET 模式测试完成（无输出是正常的）")


def test_print_footer_summary():
    """单独测试 print_footer_summary"""
    print("\n" + "="*80)
    print("测试 PRINT_FOOTER_SUMMARY")
    print("="*80)
    
    console = get_rich_console()
    
    metrics1 = {
        "total_tokens": 154200,
        "input_tokens": 98000,
        "output_tokens": 56200,
        "models_used": ["seed2.0", "gemini3", "qwen3max"]
    }
    console.print_footer_summary(2028.71, metrics1)
    
    metrics2 = {
        "total_tokens": 154200,
        "input_tokens": 98000,
        "output_tokens": 56200,
        "models_used": ["seed2.0", "gemini3", "qwen3max"],
        "providers_used": ["LLM1", "LLM2", "LLM3"],
        "provider_models": {"LLM1": ["doubao-seed-1-6-flash-250828"], "LLM2": ["qwen3.5-plus"], "LLM3": ["gemini-3.1-pro"]}
    }
    console.print_footer_summary(2028.71, metrics2)
    
    metrics3 = {
        "total_tokens": 154200,
        "input_tokens": 98000,
        "output_tokens": 56200,
        "models_used": ["seed2.0", "gemini3", "qwen3max"],
        "providers_used": [],
        "provider_models": {}
    }
    console.print_footer_summary(2028.71, metrics3)


if __name__ == "__main__":
    print("开始模拟 CLI 测试...\n")
    
    test_print_footer_summary()
    test_plain_mode()
    test_quiet_mode()
    test_live_display()
    
    print("\n" + "="*80)
    print("所有测试完成！")
    print("="*80)

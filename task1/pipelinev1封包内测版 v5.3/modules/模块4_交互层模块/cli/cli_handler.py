"""
模块职责：CLI入口模块
提供命令行接口，支持Pipeline执行、项目管理等功能
"""

import os
import sys
import argparse
import json
from datetime import datetime

from rich_argparse import RichHelpFormatter

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, project_root)

from modules.模块1_数据锚点与存储模块.data_anchor_manager import DataAnchorManager
from modules.模块1_数据锚点与存储模块.run_record_manager import get_run_record_manager
from modules.模块0_全局调度面板.pipeline_controller import get_pipeline_controller
from modules.模块4_交互层模块.cli.rich_console import get_rich_console

console = get_rich_console()


def create_project_command(args):
    data_manager = DataAnchorManager()
    project_id = data_manager.create_requirement_project(args.name)
    console.log_success(f"项目创建成功！")
    console.print_panel(f"项目ID: [cyan]{project_id}[/cyan]\n项目名称: [magenta]{args.name}[/magenta]", title="项目信息")
    return project_id


def list_projects_command(args):
    data_manager = DataAnchorManager()
    projects = data_manager.list_requirement_projects()
    
    if not projects:
        console.log_warning("暂无项目")
        return
    
    console.show_table(projects, title=f"项目列表 ({len(projects)} 个)")


def run_pipeline_command(args):
    console.show_banner()
    
    controller = get_pipeline_controller()
    
    if args.file:
        if not os.path.exists(args.file):
            console.log_error(f"文件不存在: {args.file}")
            return
        with open(args.file, 'r', encoding='utf-8') as f:
            requirement_text = f.read()
    elif args.text:
        requirement_text = args.text
    else:
        console.log_error("请提供需求文本（--text 或 --file）")
        return
    
    start_time = datetime.now()
    
    log_buffer = []
    final_metrics = {}
    
    with console.live_display(mode=args.progress, description="Pipeline执行中...") as (update_log, update_progress, update_metrics):
        
        if args.progress == "auto":
            update_log("开始执行Pipeline...", "INFO")
            update_log(f"需求长度: {len(requirement_text)} 字符", "INFO")
            if args.project:
                update_log(f"项目ID: {args.project}", "INFO")
        else:
            console.log_info(f"开始执行Pipeline...")
            console.log_info(f"需求长度: {len(requirement_text)} 字符")
            if args.project:
                console.log_info(f"项目ID: {args.project}")
        
        def log_callback(log_entry):
            level = log_entry.get("level", "INFO")
            message = log_entry.get("message", "")
            stage = log_entry.get("stage", "")
            
            log_buffer.append(log_entry)
            update_log(message, level, stage)
        
        def metrics_callback(metrics):
            nonlocal final_metrics
            final_metrics = metrics
            update_metrics(metrics)
        
        controller.set_log_callback(log_callback)
        controller.set_progress_callback(update_progress)
        controller.set_metrics_callback(metrics_callback)
        
        result = controller.start_pipeline(requirement_text, args.project)
        
        controller.set_log_callback(None)
        controller.set_progress_callback(None)
        controller.set_metrics_callback(None)
    
    end_time = datetime.now()
    
    if result["success"]:
        duration = (end_time - start_time).total_seconds()
        
        if args.progress != "quiet":
            console.log_success(f"Pipeline执行成功！耗时: {duration:.2f} 秒")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            if args.progress != "quiet":
                console.log_info(f"结果已保存到: {args.output}")
        
        results = result.get("results", {})
        if results and args.progress != "quiet":
            summary_data = []
            for stage, stage_result in results.items():
                status = "✅" if stage_result.get("success") else "❌"
                summary_data.append({"阶段": stage, "状态": status})
            console.show_table(summary_data, title="执行摘要")
        
        providers_used = []
        provider_models = {}
        try:
            current_run_id = controller.current_run_id
            if current_run_id:
                run_manager = get_run_record_manager()
                run_record = run_manager.load_run_record(current_run_id)
                if run_record:
                    llm_calls = run_record.get('llm_calls', [])
                    for call in llm_calls:
                        provider = call.get('provider')
                        model = call.get('model')
                        if provider and provider not in providers_used:
                            providers_used.append(provider)
                        if provider and model:
                            if provider not in provider_models:
                                provider_models[provider] = []
                            if model not in provider_models[provider]:
                                provider_models[provider].append(model)
        except:
            pass
        
        final_metrics['providers_used'] = providers_used
        final_metrics['provider_models'] = provider_models
        
        if args.progress != "quiet":
            console.print_footer_summary(duration, final_metrics)
    else:
        if args.progress != "quiet":
            console.log_error(f"Pipeline执行失败！")
            console.log_error(f"错误: {result.get('error')}")


def show_status_command(args):
    controller = get_pipeline_controller()
    status = controller.get_status()
    
    status_map = {
        "idle": "🟢 空闲",
        "running": "🔵 运行中",
        "paused": "🟡 已暂停",
        "stopped": "🔴 已停止"
    }
    status_text = status_map.get(status["status"], "⚪ 未知")
    
    status_data = [
        {"项": "状态", "值": status_text},
        {"项": "当前阶段", "值": status["current_stage"] or "-"},
        {"项": "进度", "值": f"{status['progress']}%"},
        {"项": "日志数", "值": str(status["log_count"])}
    ]
    if status['start_time']:
        status_data.append({"项": "开始时间", "值": status['start_time']})
    if status['end_time']:
        status_data.append({"项": "结束时间", "值": status['end_time']})
    
    console.show_table(status_data, title="Pipeline状态")


def show_logs_command(args):
    controller = get_pipeline_controller()
    logs = controller.get_logs(limit=args.limit, level=args.level)
    
    if not logs:
        console.log_warning("暂无日志")
        return
    
    console.log_info(f"日志 ({len(logs)} 条):")
    for log in logs:
        level = log.get("level", "INFO")
        message = log.get("message", "")
        stage = log.get("stage", "")
        timestamp = log.get("timestamp", "")
        
        if level == "INFO":
            console.log_info(f"[{timestamp}] {message}", stage)
        elif level == "SUCCESS":
            console.log_success(f"[{timestamp}] {message}", stage)
        elif level == "WARNING":
            console.log_warning(f"[{timestamp}] {message}", stage)
        elif level == "ERROR":
            console.log_error(f"[{timestamp}] {message}", stage)


def list_runs_command(args):
    run_manager = get_run_record_manager()
    runs = run_manager.list_run_records(limit=args.limit)
    
    if not runs:
        console.log_warning("暂无运行记录")
        return
    
    status_map = {
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "stopped": "⏹️"
    }
    
    display_data = []
    for run in runs:
        status_icon = status_map.get(run.get("status"), "📌")
        display_data.append({
            "状态": status_icon,
            "运行ID": run['run_id'][:16] + "...",
            "项目ID": run.get('project_id', '-'),
            "开始时间": run.get('start_time', '-')[:19],
            "耗时": f"{run.get('duration_seconds', 0):.2f}s"
        })
    
    console.show_table(display_data, title=f"运行记录 ({len(runs)} 条)")


def show_run_command(args):
    run_manager = get_run_record_manager()
    run = run_manager.load_run_record(args.run_id, args.date)
    
    if not run:
        console.log_error(f"运行记录不存在: {args.run_id}")
        return
    
    status_map = {
        "running": "🔄 运行中",
        "completed": "✅ 已完成",
        "failed": "❌ 失败",
        "stopped": "⏹️ 已停止"
    }
    status_text = status_map.get(run.get("status", "unknown"), "⚪ 未知")
    
    console.print_panel(
        f"运行ID: [cyan]{run['run_id']}[/cyan]\n"
        f"项目ID: [magenta]{run.get('project_id', '-')}[/magenta]\n"
        f"状态: {status_text}\n"
        f"开始时间: {run.get('start_time', '-')}\n"
        f"结束时间: {run.get('end_time', '-')}\n"
        f"耗时: [yellow]{run.get('duration_seconds', 0):.2f}[/yellow] 秒",
        title="运行记录详情"
    )
    
    console.log_info(f"需求文本: {run.get('requirement_text', '').strip()[:100]}...")
    
    results = run.get('results', {})
    if results:
        summary_data = []
        for stage, result in results.items():
            status = "✅" if result.get('success') else "❌"
            summary_data.append({"阶段": stage, "状态": status})
        console.show_table(summary_data, title="阶段结果")
    
    llm_calls = run.get('llm_calls', [])
    if llm_calls:
        console.log_info(f"LLM调用记录 ({len(llm_calls)} 次):")
        for i, call in enumerate(llm_calls, 1):
            status = "✅" if call.get('success') else "❌"
            console.print(f"  {i}. {status} {call.get('provider')} - {call.get('model')} | 响应时间: {call.get('response_time', 0):.2f}s")


def show_run_logs_command(args):
    run_manager = get_run_record_manager()
    run = run_manager.load_run_record(args.run_id, args.date)
    
    if not run:
        console.log_error(f"运行记录不存在: {args.run_id}")
        return
    
    logs = run.get('logs', [])
    if not logs:
        console.log_warning("暂无日志")
        return
    
    console.log_info(f"运行日志 ({len(logs)} 条):")
    for log in logs:
        level = log.get("level", "INFO")
        message = log.get("message", "")
        stage = log.get("stage", "")
        timestamp = log.get("timestamp", "")
        
        if level == "INFO":
            console.log_info(f"[{timestamp}] {message}", stage)
        elif level == "SUCCESS":
            console.log_success(f"[{timestamp}] {message}", stage)
        elif level == "WARNING":
            console.log_warning(f"[{timestamp}] {message}", stage)
        elif level == "ERROR":
            console.log_error(f"[{timestamp}] {message}", stage)


def main():
    parser = argparse.ArgumentParser(
        description="需求结构化分析管道 - CLI入口",
        formatter_class=RichHelpFormatter,
        epilog="""
示例:
  # 创建项目
  python cli_handler.py create --name "我的项目"
  
  # 列出项目
  python cli_handler.py list
  
  # 运行Pipeline（从文本）
  python cli_handler.py run --text "这是一个需求" --project 20260301_123456
  
  # 运行Pipeline（从文件）
  python cli_handler.py run --file requirement.txt --output result.json
  
  # 查看状态
  python cli_handler.py status
  
  # 查看日志
  python cli_handler.py logs --limit 50 --level INFO
        """
    )
    
    subparsers = parser.add_subparsers(title="命令", dest="command")
    
    create_parser = subparsers.add_parser("create", help="创建新项目", formatter_class=RichHelpFormatter)
    create_parser.add_argument("--name", "-n", required=True, help="项目名称")
    
    list_parser = subparsers.add_parser("list", help="列出所有项目", formatter_class=RichHelpFormatter)
    
    run_parser = subparsers.add_parser("run", help="运行Pipeline", formatter_class=RichHelpFormatter)
    run_parser.add_argument("--text", "-t", help="需求文本")
    run_parser.add_argument("--file", "-f", help="需求文件路径")
    run_parser.add_argument("--project", "-p", help="项目ID")
    run_parser.add_argument("--output", "-o", help="输出结果文件路径")
    run_parser.add_argument("--progress", help="进度显示模式 (auto/plain/quiet)", choices=["auto", "plain", "quiet"], default="auto")
    
    status_parser = subparsers.add_parser("status", help="显示Pipeline状态", formatter_class=RichHelpFormatter)
    
    logs_parser = subparsers.add_parser("logs", help="显示Pipeline日志", formatter_class=RichHelpFormatter)
    logs_parser.add_argument("--limit", "-l", type=int, default=100, help="显示日志数量限制")
    logs_parser.add_argument("--level", help="日志级别过滤 (INFO/SUCCESS/WARNING/ERROR)")
    
    runs_parser = subparsers.add_parser("runs", help="运行记录管理", formatter_class=RichHelpFormatter)
    runs_subparsers = runs_parser.add_subparsers(title="运行记录命令", dest="runs_command")
    
    runs_list_parser = runs_subparsers.add_parser("list", help="列出运行记录", formatter_class=RichHelpFormatter)
    runs_list_parser.add_argument("--limit", "-l", type=int, default=20, help="显示记录数量限制")
    
    runs_show_parser = runs_subparsers.add_parser("show", help="显示运行记录详情", formatter_class=RichHelpFormatter)
    runs_show_parser.add_argument("run_id", help="运行记录ID")
    runs_show_parser.add_argument("--date", help="日期 (YYYYMMDD)")
    
    runs_logs_parser = runs_subparsers.add_parser("logs", help="显示运行记录日志", formatter_class=RichHelpFormatter)
    runs_logs_parser.add_argument("run_id", help="运行记录ID")
    runs_logs_parser.add_argument("--date", help="日期 (YYYYMMDD)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    command_handlers = {
        "create": create_project_command,
        "list": list_projects_command,
        "run": run_pipeline_command,
        "status": show_status_command,
        "logs": show_logs_command
    }
    
    if args.command == "runs":
        runs_handlers = {
            "list": list_runs_command,
            "show": show_run_command,
            "logs": show_run_logs_command
        }
        if args.runs_command in runs_handlers:
            runs_handlers[args.runs_command](args)
        else:
            console.log_error(f"未知运行记录命令: {args.runs_command}")
            runs_parser.print_help()
    elif args.command in command_handlers:
        command_handlers[args.command](args)
    else:
        console.log_error(f"未知命令: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()

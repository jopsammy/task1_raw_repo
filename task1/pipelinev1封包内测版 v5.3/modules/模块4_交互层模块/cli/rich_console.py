"""
RichConsole 类：提供基于 rich 库的美观控制台输出功能
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional, Union
from contextlib import contextmanager

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax
from rich.box import Box, DOUBLE
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.live import Live
from rich.traceback import install


class RichConsole:
    """基于 rich 库的美观控制台输出类"""

    def __init__(self):
        """初始化控制台"""
        self.console = Console()
        self._install_traceback()

    def _install_traceback(self):
        """安装 rich 异常回溯"""
        install(show_locals=False, width=120)

    def show_banner(self, title="需求结构化分析管道", subtitle="Requirements Structuring Pipeline", version="v5.2"):
        """
        显示横幅

        Args:
            title: 主标题
            subtitle: 副标题
            version: 版本号
        """
        banner_text = Text()
        banner_text.append("\n  " + title + "  \n", style="bold magenta")
        banner_text.append("  " + subtitle + "  \n", style="dim cyan")
        banner_text.append("  " + version + "  ", style="bold yellow")

        panel = Panel(
            banner_text,
            border_style="cyan",
            padding=(1, 4),
            box=DOUBLE
        )
        self.console.print(panel)

    def log_info(self, message, stage=None):
        """
        输出 INFO 级别日志

        Args:
            message: 日志消息
            stage: 阶段名称
        """
        prefix = Text("[INFO]", style="bold blue")
        self._log(prefix, message, stage)

    def log_success(self, message, stage=None):
        """
        输出 SUCCESS 级别日志

        Args:
            message: 日志消息
            stage: 阶段名称
        """
        prefix = Text("[SUCCESS]", style="bold green")
        self._log(prefix, message, stage)

    def log_warning(self, message, stage=None):
        """
        输出 WARNING 级别日志

        Args:
            message: 日志消息
            stage: 阶段名称
        """
        prefix = Text("[WARNING]", style="bold yellow")
        self._log(prefix, message, stage)

    def log_error(self, message, stage=None):
        """
        输出 ERROR 级别日志

        Args:
            message: 日志消息
            stage: 阶段名称
        """
        prefix = Text("[ERROR]", style="bold red")
        self._log(prefix, message, stage)

    def _log(self, prefix, message, stage=None):
        """
        内部日志输出方法

        Args:
            prefix: 日志前缀
            message: 日志消息
            stage: 阶段名称
        """
        log_text = Text()
        log_text.append(prefix)
        log_text.append(" ")
        if stage:
            log_text.append("[" + stage + "] ", style="dim")
        log_text.append(message)
        self.console.print(log_text)

    def show_table(self, data, title=None, columns=None):
        """
        显示表格

        Args:
            data: 数据列表，每个元素是一个字典
            title: 表格标题
            columns: 列名列表，如果为 None 则使用字典的键
        """
        if not data:
            self.log_warning("表格数据为空")
            return

        table = Table(title=title, show_header=True, header_style="bold magenta")

        if columns is None:
            columns = list(data[0].keys())

        for col in columns:
            table.add_column(str(col), style="cyan")

        for row in data:
            table.add_row(*[str(row.get(col, "")) for col in columns])

        self.console.print(table)

    def show_json(self, data, title=None):
        """
        显示高亮的 JSON

        Args:
            data: JSON 数据
            title: 标题
        """
        if title:
            self.console.print("\n[bold]" + title + "[/bold]", style="magenta")

        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        self.console.print(syntax)

    @contextmanager
    def progress_bar(self, total, description="处理中..."):
        """
        进度条上下文管理器

        Args:
            total: 总进度
            description: 描述文本

        Yields:
            progress: Progress 对象，用于更新进度
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console
        )

        task_id = progress.add_task(description, total=total)

        with Live(progress, refresh_per_second=10):
            yield progress, task_id

    @contextmanager
    def live_display(self, mode="auto", description="Pipeline执行中..."):
        """
        Live Display 上下文管理器 - 简单版本

        Args:
            mode: 显示模式 (auto/plain/quiet)
            description: 进度条描述文本

        Yields:
            update_log: 函数用于添加日志
            update_progress: 函数用于更新进度
            update_metrics: 函数用于更新 metrics
        """
        if mode == "quiet":
            def quiet_update_log(message, level="INFO", stage=""):
                pass
            def quiet_update_progress(value):
                pass
            def quiet_update_metrics(metrics):
                pass
            yield quiet_update_log, quiet_update_progress, quiet_update_metrics
            return

        if mode == "plain":
            def plain_update_log(message, level="INFO", stage=""):
                prefix = "[" + level + "]"
                if stage:
                    prefix += " [" + stage + "]"
                print(prefix + " " + message)
            def plain_update_progress(value):
                pass
            def plain_update_metrics(metrics):
                pass
            yield plain_update_log, plain_update_progress, plain_update_metrics
            return

        with self.progress_bar(total=100, description=description) as (p, tid):
            def simple_update_log(message, level="INFO", stage=""):
                if level == "INFO":
                    self.log_info(message, stage)
                elif level == "SUCCESS":
                    self.log_success(message, stage)
                elif level == "WARNING":
                    self.log_warning(message, stage)
                elif level == "ERROR":
                    self.log_error(message, stage)
            def update_progress_wrapper(value):
                p.update(tid, completed=value)
            def simple_update_metrics(metrics):
                pass
            yield simple_update_log, update_progress_wrapper, simple_update_metrics

    def print_footer_summary(self, duration_seconds, metrics):
        """
        打印灰度 Footer Summary

        Args:
            duration_seconds: 总耗时（秒）
            metrics: 指标字典
        """
        def format_token(num):
            if num is None:
                return "0.0k"
            return f"{num / 1000:.1f}k"

        total_tokens = metrics.get("total_tokens", 0)
        input_tokens = metrics.get("input_tokens", 0)
        output_tokens = metrics.get("output_tokens", 0)

        providers_used = metrics.get("providers_used", [])
        provider_models = metrics.get("provider_models", {})
        models_used = metrics.get("models_used", [])

        if providers_used:
            providers_text = "槽位: " + ", ".join(providers_used)
        else:
            providers_text = "槽位: -"

        if provider_models:
            model_parts = []
            for slot, models in provider_models.items():
                if isinstance(models, list):
                    model_str = "/".join(models)
                else:
                    model_str = str(models)
                model_parts.append(f"{slot}→{model_str}")
            models_text = "模型: " + " | ".join(model_parts)
        elif models_used:
            models_text = "模型: " + ", ".join(models_used)
        else:
            models_text = "模型: -"

        self.console.print()
        self.console.print(Text("  ════════════════════════════════════════════════════════════════", style="dim"))
        self.console.print(Text(f"  总耗时: {round(duration_seconds)}s", style="dim"))
        self.console.print(Text(f"  总Token: {format_token(total_tokens)} (Input: {format_token(input_tokens)} / Output: {format_token(output_tokens)})", style="dim"))
        self.console.print(Text(f"  {providers_text}", style="dim"))
        self.console.print(Text(f"  {models_text}", style="dim"))
        self.console.print(Text("  ════════════════════════════════════════════════════════════════", style="dim"))
        self.console.print()

    def print(self, *objects, sep=" ", end="\n", style=None):
        """
        通用打印方法

        Args:
            *objects: 要打印的对象
            sep: 分隔符
            end: 结束符
            style: 样式
        """
        self.console.print(*objects, sep=sep, end=end, style=style)

    def print_panel(self, content, title=None, border_style="cyan"):
        """
        打印面板

        Args:
            content: 内容
            title: 标题
            border_style: 边框样式
        """
        panel = Panel(
            content,
            title=title,
            border_style=border_style,
            padding=(1, 2)
        )
        self.console.print(panel)


_rich_console_instance = None


def get_rich_console():
    """
    获取 RichConsole 单例

    Returns:
        RichConsole 实例
    """
    global _rich_console_instance
    if _rich_console_instance is None:
        _rich_console_instance = RichConsole()
    return _rich_console_instance

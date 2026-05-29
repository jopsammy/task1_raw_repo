"""
模块职责：统一启动入口
支持通过命令行选择启动Streamlit UI或CLI
"""

import os
import sys
import argparse
import subprocess
import socket

# 路径处理
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)


def is_port_available(port):
    """
    检查指定端口是否可用
    Windows 平台尝试 bind 到 0.0.0.0:port，避免只测 localhost 但实际监听冲突
    
    Args:
        port: 要检查的端口号
        
    Returns:
        bool: 端口是否可用
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False


def find_available_port(start_port, end_port):
    """
    在指定范围内查找可用端口
    
    Args:
        start_port: 起始端口（包含）
        end_port: 结束端口（包含）
        
    Returns:
        int: 找到的可用端口，若范围内无可用端口则返回 None
    """
    for port in range(start_port, end_port + 1):
        if is_port_available(port):
            return port
    return None


def parse_port_range(port_range_str):
    """
    解析端口范围字符串，格式为 START-END
    
    Args:
        port_range_str: 端口范围字符串，如 "8501-8600"
        
    Returns:
        tuple: (start_port, end_port)
        
    Raises:
        ValueError: 格式非法或 START > END
    """
    try:
        start_str, end_str = port_range_str.split('-', 1)
        start_port = int(start_str.strip())
        end_port = int(end_str.strip())
        if start_port > end_port:
            raise ValueError(f"起始端口 {start_port} 不能大于结束端口 {end_port}")
        if start_port < 1 or end_port > 65535:
            raise ValueError(f"端口范围必须在 1-65535 之间")
        return start_port, end_port
    except ValueError as e:
        raise ValueError(f"端口范围格式错误: {port_range_str}，应为 START-END 格式（如 8501-8600）: {e}")


def print_banner():
    """打印横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    需求结构化分析管道 v5.2                      ║
║                Requirements Structuring Pipeline             ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def start_ui(preferred_port=8501, port_start=8501, port_end=8600):
    """
    启动Streamlit UI
    
    Args:
        preferred_port: 首选端口
        port_start: 端口范围起始
        port_end: 端口范围结束
    """
    print_banner()
    print("🚀 启动Streamlit UI...")
    print(f"📂 项目根目录: {project_root}")
    print("-" * 60)
    
    app_ui_path = os.path.join(project_root, "interfaces", "app_ui.py")
    
    current_port = preferred_port
    tried_ports = []
    
    while True:
        tried_ports.append(current_port)
        
        if not is_port_available(current_port):
            print(f"⚠️  端口 {current_port} 已被占用，尝试下一个...")
            current_port += 1
            if current_port > port_end:
                print(f"\n❌ 错误：端口范围 {port_start}-{port_end} 内无可用端口")
                print(f"   已尝试端口: {', '.join(map(str, tried_ports))}")
                print(f"   建议：使用 --port-range 参数扩大端口范围")
                return
            continue
        
        print(f"✅ 找到可用端口: {current_port}")
        print(f"🌐 访问地址: http://localhost:{current_port}")
        print("-" * 60)
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "streamlit", "run", app_ui_path,
                "--server.port", str(current_port)
            ], cwd=project_root)
            
            if result.returncode != 0:
                print(f"\n⚠️  Streamlit 启动失败，返回码: {result.returncode}")
                current_port += 1
                if current_port > port_end:
                    print(f"\n❌ 错误：端口范围 {port_start}-{port_end} 内所有端口均尝试失败")
                    print(f"   已尝试端口: {', '.join(map(str, tried_ports))}")
                    return
                print(f"🔄 尝试下一个端口: {current_port}")
                continue
            
            break
        except KeyboardInterrupt:
            print("\n👋 已停止")
            break
        except Exception as e:
            print(f"\n❌ 启动失败: {e}")
            current_port += 1
            if current_port > port_end:
                print(f"\n❌ 错误：端口范围 {port_start}-{port_end} 内所有端口均尝试失败")
                print(f"   已尝试端口: {', '.join(map(str, tried_ports))}")
                return
            print(f"🔄 尝试下一个端口: {current_port}")


def start_cli():
    """启动CLI"""
    from modules.模块4_交互层模块.cli.cli_handler import main
    main()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="需求结构化分析工具 - 统一启动入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动Streamlit UI（默认）
  python boot.py
  
  # 启动Streamlit UI
  python boot.py ui
  
  # 自定义首选端口
  python boot.py ui --port 8502
  
  # 自定义端口范围
  python boot.py ui --port-range 8501-8600
  
  # 启动CLI
  python boot.py cli
  
  # 运行Pipeline
  python boot.py cli run --file requirement.txt
  
  # CLI帮助
  python boot.py cli --help
        """
    )
    
    parser.add_argument(
        "mode", nargs="?", default="ui",
        choices=["ui", "cli"],
        help="启动模式: ui (Streamlit UI) 或 cli (命令行)"
    )
    
    parser.add_argument(
        "--port", type=int, default=8501,
        help="UI模式: 首选端口（默认: 8501）"
    )
    
    parser.add_argument(
        "--port-range", type=str, default="8501-8600",
        help="UI模式: 端口范围，格式为 START-END（默认: 8501-8600）"
    )
    
    # 解析已知参数
    args, remaining = parser.parse_known_args()
    
    if args.mode == "ui":
        try:
            port_start, port_end = parse_port_range(args.port_range)
            
            if not (port_start <= args.port <= port_end):
                print(f"❌ 错误: 首选端口 {args.port} 不在端口范围 {port_start}-{port_end} 内")
                sys.exit(1)
            
            start_ui(
                preferred_port=args.port,
                port_start=port_start,
                port_end=port_end
            )
        except ValueError as e:
            print(f"❌ {e}")
            sys.exit(1)
    elif args.mode == "cli":
        if remaining:
            sys.argv = [sys.argv[0]] + remaining
        start_cli()


if __name__ == "__main__":
    main()

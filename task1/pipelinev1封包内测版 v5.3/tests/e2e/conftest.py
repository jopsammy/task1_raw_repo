"""
Playwright E2E测试配置
"""

import os
import sys
import pytest
import subprocess
import time
import signal
import socket

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)


def is_port_available(port):
    """
    检查指定端口是否可用
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def streamlit_server():
    """启动Streamlit服务器"""
    port = 8501
    
    if not is_port_available(port):
        pytest.fail(f"端口 {port} 已被占用，请清理后再运行测试")
    
    app_path = os.path.join(project_root, "modules", "模块4_交互层模块", "streamlit", "app.py")
    
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", app_path, "--server.port", str(port), "--server.headless", "true"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(5)
    
    yield f"http://localhost:{port}"
    
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture
def browser_page(browser, streamlit_server):
    """获取浏览器页面"""
    page = browser.new_page()
    page.goto(streamlit_server)
    yield page
    page.close()

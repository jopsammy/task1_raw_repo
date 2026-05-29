"""
模块职责：Streamlit UI启动入口
从模块4_交互层模块导入并启动Streamlit UI
"""

import os
import sys

# 路径处理 - 使用绝对路径规范
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

# 导入模块4的Streamlit UI
from modules.模块4_交互层模块.streamlit.app import main

if __name__ == "__main__":
    main()

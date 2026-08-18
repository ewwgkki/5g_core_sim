# utils/path.py

import os
import sys

def init_sys_path():
    """
    将项目根目录添加到 sys.path，确保所有模块都可以被正确导入。
    """
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

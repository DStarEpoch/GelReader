#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/4/3 14:49
# @Author : yuyeqing
# @File   : resource.py
# @IDE    : PyCharm
import os
import sys


def resource_path(relative_path):
    """获取资源文件的绝对路径，无论是在打包前还是打包后"""
    try:
        # PyInstaller 创建的临时目录
        base_path = sys._MEIPASS
    except Exception:
        # 源代码运行时的目录
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

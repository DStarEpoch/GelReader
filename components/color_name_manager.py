#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/3/26 10:16
# @Author : yuyeqing
# @File   : color_name_manager.py
# @IDE    : PyCharm
from share.consts import CONTOUR_COLOR_LIST
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel


class ColorNameManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QHBoxLayout()
        self.color_widgets = []

    def update_colors(self, results):
        # 清空旧组件
        for w in self.color_widgets:
            self.layout.removeWidget(w)
            w.deleteLater()

        # 创建新颜色标签
        for idx, group in enumerate(results):
            color = group['children'][0]['color']  # 取第一个子元素颜色
            lbl = QLabel(f"Group {idx + 1}")
            lbl.setStyleSheet(f"background-color: rgb({color[0]},{color[1]},{color[2]});")
            self.layout.addWidget(lbl)
            self.color_widgets.append(lbl)

        self.setLayout(self.layout)

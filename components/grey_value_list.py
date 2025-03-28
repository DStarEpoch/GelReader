#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/3/26 10:16
# @Author : yuyeqing
# @File   : grey_value_list.py
# @IDE    : PyCharm
from share.consts import CONTOUR_COLOR_LIST
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class GreyValueList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)  # 设置间距
        self.layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        self.setLayout(self.layout)
        self.items = []  # 用于存储所有 QLabel，便于后续更新

    def update_values(self, results):
        # 清空旧的 QLabel
        for item in self.items:
            item.deleteLater()
        self.items.clear()

        # 根据新的结果创建新的 QLabel
        for group_idx, group in enumerate(results):
            group_label = QLabel(f"Group {group_idx + 1}:")
            self.layout.addWidget(group_label)
            self.items.append(group_label)
            for idx, child in enumerate(group):
                if child is None:
                    continue
                label = QLabel(f"Contour {idx}: Gray Integral = {child[4]}")
                self.layout.addWidget(label)
                self.items.append(label)

        # 确保布局更新
        self.layout.addStretch()

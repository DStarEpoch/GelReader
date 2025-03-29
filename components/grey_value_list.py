#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/3/26 10:16
# @Author : yuyeqing
# @File   : grey_value_list.py
# @IDE    : PyCharm
from share.consts import CONTOUR_COLOR_LIST
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QLabel


class GreyValueList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.labels = []  # 用于存储所有 QLabel，便于后续更新

    def update_values(self, group_result):
        # 清空旧的 QLabel
        for label in self.labels:
            label.deleteLater()
        self.labels.clear()

        y_offset = 0
        for idx, contour_info in enumerate(group_result):
            if contour_info is None:
                continue
            rgba = CONTOUR_COLOR_LIST[idx % len(CONTOUR_COLOR_LIST)]
            color = QColor(rgba[0], rgba[1], rgba[2], rgba[3])

            label = QLabel(f"{contour_info[-1]}", self)
            label.setStyleSheet(f"color: rgb({color.red()}, {color.green()}, {color.blue()});")
            label.move(0, y_offset)
            self.labels.append(label)
            y_offset += label.height()

        # 更新整个 GreyValueList 的大小
        self.resize(self.width(), y_offset)

    def update_data_for_contour_idx(self, idx, value):
        if idx >= len(self.labels):
            return
        label = self.labels[idx]
        label.setText(f"{value}")

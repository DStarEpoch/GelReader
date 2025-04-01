#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/3/26 10:16
# @Author : yuyeqing
# @File   : grey_value_list.py
# @IDE    : PyCharm
from functools import partial
from share.consts import CONTOUR_COLOR_LIST
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton


class GreyValueList(QWidget):
    def __init__(self, group_idx: int, parent=None, delete_cb=None):
        super().__init__(parent=parent)
        self.labels = []  # 用于存储所有 QLabel，便于后续更新
        self.buttons = []  # 用于存储所有 QPushButton，便于后续更新
        self.delete_cb = delete_cb
        self.group_idx = group_idx

    def update_values(self, group_result):
        # 清空旧的 QLabel
        for label in self.labels:
            label.deleteLater()
        for button in self.buttons:
            if button:
                button.deleteLater()
        self.labels.clear()
        self.buttons.clear()
        for idx, contour_info in enumerate(group_result):
            if contour_info is None:
                self.labels.append(None)
                self.buttons.append(None)
                continue
            rgba = CONTOUR_COLOR_LIST[idx % len(CONTOUR_COLOR_LIST)]
            color = QColor(rgba[0], rgba[1], rgba[2], rgba[3])
            label = QLabel(f"{contour_info[-1]}", self)
            label.setStyleSheet(f"color: rgb({color.red()}, {color.green()}, {color.blue()});")
            self.labels.append(label)
            button = QPushButton(self)
            button.setIcon(QIcon('assets/delete.png'))
            button.clicked.connect(partial(self.on_delete, idx))
            self.buttons.append(button)
        self.refresh_labels_and_buttons()

    def refresh_labels_and_buttons(self):
        y_offset = 0
        y_steps = 20
        for idx, (label, button) in enumerate(zip(self.labels, self.buttons)):
            if label is None:
                continue
            label.resize(label.sizeHint())  # 自动调整 QLabel 的大小
            label.move(15, y_offset)  # 为按钮留出空间
            button.resize(15, 15)  # 设置按钮大小
            button.move(0, y_offset)  # 设置按钮位置
            y_offset += y_steps
        self.resize(self.width(), y_offset)

    def update_data_for_contour_idx(self, idx, value):
        if idx >= len(self.labels):
            return
        label = self.labels[idx]
        label.setText(f"{value}")
        label.resize(label.sizeHint())

    def on_delete(self, label_idx):
        if self.delete_cb:
            contour_tag = (self.group_idx, label_idx)
            self.delete_cb(contour_tag)
        if self.labels[label_idx]:
            self.labels[label_idx].deleteLater()
            self.labels[label_idx] = None
        if self.buttons[label_idx]:
            self.buttons[label_idx].deleteLater()
            self.buttons[label_idx] = None
        self.refresh_labels_and_buttons()

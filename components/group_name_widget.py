#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/4/2 16:44
# @Author : yuyeqing
# @File   : group_name_widget.py
# @IDE    : PyCharm
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QWidget, QPushButton, QInputDialog


class GroupNameWidget(QWidget):

    def __init__(self, parent, group_idx: int, delete_cb=None, set_name_cb=None):
        super().__init__(parent=parent)
        self.group_idx = group_idx
        self.delete_cb = delete_cb
        self.set_name_cb = set_name_cb
        self._group_name = f"Group{group_idx}"
        self._init_ui()

    @property
    def name(self):
        return self._group_name

    @name.setter
    def name(self, value):
        self._group_name = value
        self.name_button.setText(value)
        self.set_name_cb and self.set_name_cb(self.group_idx, value)

    def _init_ui(self):
        self.delete_button = QPushButton(self)
        self.delete_button.setIcon(QIcon('assets/delete.ico'))
        self.delete_button.clicked.connect(self.delete_group)
        self.delete_button.resize(15, 15)

        color = QColor(*[128, 136, 144, 225])
        self.name_button = QPushButton(self.name, self)
        self.name_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({color.red()}, {color.green()}, {color.blue()});
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 1px 1px;
                text-align: left;
                color: black;
            }}
            QPushButton:hover {{
                background-color: rgb({min(color.red() + 30, 255)}, {min(color.green() + 30, 255)}, {min(color.blue() + 30, 255)});
            }}
        """)
        self.name_button.resize(self.name_button.sizeHint())
        self.name_button.clicked.connect(self.edit_group_name)

        self.delete_button.move(0, 0)
        self.name_button.move(15, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.name_button.resize(self.width() - self.delete_button.width(), self.height())

    def edit_group_name(self):
        group_name, ok = QInputDialog.getText(self, "Edit Group Name", "Enter new group name:",
                                              text=self.name)
        if ok and group_name:
            self.name = group_name

    def delete_group(self):
        if self.delete_cb:
            self.delete_cb(self.group_idx)



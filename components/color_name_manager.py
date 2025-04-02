#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/3/26 10:16
# @Author : yuyeqing
# @File   : color_name_manager.py
# @IDE    : PyCharm
from share.consts import CONTOUR_COLOR_LIST
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton,
                             QFileDialog, QInputDialog, QMessageBox)
from functools import partial


class ColorNames(dict):

    def __getitem__(self, idx):
        if idx not in self:
            self[idx] = f"Contour_{idx}"
        return super().__getitem__(idx)


class ColorNameManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.color_widgets = dict()
        self.color_names = ColorNames()
        self._init_ui()

    def _init_ui(self):
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)
        self.setFixedHeight(40)
        self.update_color_names([])

    def update_color_names(self, results):
        # 清空旧的颜色条
        for _, widget in self.color_widgets.items():
            widget.deleteLater()
        self.color_widgets.clear()

        # 获取最大轮廓数量
        if results:
            available_contour_ids = list()
            for group in results:
                for contour_idx, contour_info in enumerate(group):
                    if contour_idx in available_contour_ids:
                        continue
                    if contour_info is not None:
                        available_contour_ids.append(contour_idx)

            # 创建新的颜色条
            for i in available_contour_ids:
                color = QColor(*CONTOUR_COLOR_LIST[i % len(CONTOUR_COLOR_LIST)])

                # 创建一个按钮，同时显示颜色和名称
                color_button = QPushButton(self.color_names[i])
                
                color_button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: rgb({color.red()}, {color.green()}, {color.blue()});
                        border: 1px solid #666666;
                        border-radius: 3px;
                        padding: 5px 10px;
                        text-align: center;
                        color: white;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: rgb({min(color.red()+30, 255)}, {min(color.green()+30, 255)}, {min(color.blue()+30, 255)});
                    }}
                """)
                
                color_button.setFixedHeight(30)
                color_button.setMinimumWidth(100)
                
                # 连接点击事件到编辑函数
                color_button.clicked.connect(partial(self.edit_color_name, i))
                
                self.main_layout.addWidget(color_button)
                self.color_widgets[i] = color_button

    def edit_color_name(self, idx):
        color_name, ok = QInputDialog.getText(self, "Edit Color Name", "Enter new color name:",
                                              text=self.color_names[idx])
        if ok and color_name:
            self.color_names[idx] = color_name
            color_widget = self.color_widgets.get(idx)
            if color_widget:
                self.color_widgets[idx].setText(color_name)

    def export_color_name_config(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Color Config", "", "Text Files (*.txt)")
        if path:
            with open(path, 'w') as file:
                for idx, name in self.color_names.items():
                    file.write(f"{idx}: {name}\n")
            QMessageBox.information(self, "Success", "Color configuration exported successfully.")

    def load_color_name_config(self, color_name_dict: dict):
        self.color_names.update(color_name_dict)
        self.update_color_names([])


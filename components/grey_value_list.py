#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/3/26 10:16
# @Author : yuyeqing
# @File   : grey_value_list.py
# @IDE    : PyCharm
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem


class GreyValueList(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setColumnCount(3)
        self.setHeaderLabels(["Name", "Color", "ROI"])

    def update_values(self, results):
        self.clear()
        for idx, group in enumerate(results):
            parent = QTreeWidgetItem([f"Group {idx + 1}", "", ""])
            for child in group['children']:
                item = QTreeWidgetItem([
                    "",
                    f"Rect {child['rect'][0]}x{child['rect'][1]}",
                    str(child['rect'][4])
                ])
                parent.addChild(item)
            self.addTopLevelItem(parent)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/3/28 13:24
# @Author : yuyeqing
# @File   : contour_widget.py
# @IDE    : PyCharm
from share.consts import CONTOUR_COLOR_LIST
from PyQt6.QtCore import QRect, Qt, QSize
from PyQt6.QtGui import QColor, QPen, QPainter, QBrush
from PyQt6.QtWidgets import QWidget


class ContourWidget(QWidget):
    def __init__(self, parent=None, color_idx=0, contour_tag=None, changed_cb=None):
        super().__init__(parent=parent)
        self._rect = None
        self._color = None
        self.color = color_idx
        self.contour_tag = contour_tag
        self.dragging = False
        self.resizing = False
        self.resize_handle_size = 6
        self.changed_cb = changed_cb

    @property
    def position(self):
        return self.pos()

    @position.setter
    def position(self, pos):
        if not isinstance(pos, tuple) or len(pos) != 2:
            raise ValueError("Position must be a tuple of (x, y).")
        x, y = pos
        self.move(x, y)
        self.update()

    @property
    def rect(self):
        return self._rect

    def set_rect(self, width, height, offset_x=0, offset_y=0):
        # 使用 setGeometry 直接设置位置和尺寸
        self.setGeometry(offset_x, offset_y, int(width), int(height))
        # Define the rectangle within the widget
        self._rect = QRect(0, 0, int(width), int(height))
        self.update()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color_idx: int):
        if not isinstance(color_idx, int):
            raise ValueError("Color index must be an integer.")
        rgba = CONTOUR_COLOR_LIST[color_idx % len(CONTOUR_COLOR_LIST)]
        self._color = QColor(rgba[0], rgba[1], rgba[2], rgba[3])
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._rect.contains(event.pos()):
                if self.is_on_resize_handle(event.pos()):
                    self.resizing = True
                else:
                    self.dragging = True
                self.drag_start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.pos() - self.drag_start_pos
            self.move(self.pos() + delta)
        elif self.resizing:
            # Calculate new size based on mouse position
            new_width = max(self.resize_handle_size, event.pos().x())
            new_height = max(self.resize_handle_size, event.pos().y())
            self.setGeometry(self.x(), self.y(), new_width, new_height)
            self._rect.setSize(QSize(new_width, new_height))
            self.update()
        if self.changed_cb:
            self.changed_cb(self.contour_tag)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False

    def is_on_resize_handle(self, pos):
        handle_rect = QRect(self.width() - self.resize_handle_size,
                            self.height() - self.resize_handle_size,
                            self.resize_handle_size, self.resize_handle_size)
        return handle_rect.contains(pos)

    def paintEvent(self, event):
        if self._rect:
            painter = QPainter(self)
            pen = QPen(self._color, 3)
            painter.setPen(pen)
            # Draw the rectangle using the defined QRect
            painter.drawRect(self._rect)
            # Draw resize handle
            brush = QBrush(self._color)
            painter.setBrush(brush)
            painter.drawRect(self.width() - self.resize_handle_size,
                             self.height() - self.resize_handle_size,
                             self.resize_handle_size, self.resize_handle_size)
            painter.end()
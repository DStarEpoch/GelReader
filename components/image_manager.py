#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/3/26 10:15
# @Author : yuyeqing
# @File   : image_manager.py
# @IDE    : PyCharm
import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QLabel, QMessageBox, QVBoxLayout, QSizePolicy
from components.contour_widget import ContourWidget
from components.grey_value_list import GreyValueList


class ImageManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.original_image = None
        self.gray = None
        self.inverted_gray = None
        self.results = []
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.image_label.setScaledContents(True)

        # 创建布局并添加 QLabel
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # 记录绘制contours obj
        self.contour_objs: dict[tuple[int, int], ContourWidget] = dict()

        # 记录灰度值列表 obj
        self.grey_value_list_objs: dict[int, GreyValueList] = dict()

        self.scale_factor = 1.0
        self.offset = (0, 0)

    def load_image(self, image_path):
        if not image_path:
            return
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            QMessageBox.warning(self, "Error", "Failed to load image. Please check the file path.")
            return
        self.gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        h, w, ch = self.original_image.shape
        if ch != 3:
            QMessageBox.warning(self, "Error", "Unsupported image format. Only RGB images are supported.")
            self.original_image = None
            self.gray = None
            self.inverted_gray = None
            return
        print(f"Image loaded successfully. Shape: {self.original_image.shape}")
        self._resize_image_label()
        q_img = QImage(self.original_image.data, w, h, ch * w, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(q_img).scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()
        self._resize_image_label()

    def analyze(self):
        blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        self.inverted_gray = cv2.bitwise_not(self.gray)
        rects = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # roi = self.gray[y:y+h, x:x+w]
            roi = self.inverted_gray[y:y+h, x:x+w]
            gray_integral = np.sum(roi)
            rects.append((x, y, w, h, gray_integral))

        self.results = self.group_contours(rects)
        self.update()
        self._resize_image_label()

    def group_contours(self, rects):
        sorted_rects = sorted(rects, key=lambda r: (r[0], r[1]))  # Sort by x, then y
        groups = []
        current_group = []
        for rect in sorted_rects:
            if not current_group:
                current_group.append(rect)
            else:
                last_x, last_w = current_group[-1][0], current_group[-1][2]
                if rect[0] < (last_x + last_w):  # Overlapping width
                    current_group.append(rect)
                else:
                    groups.append(current_group)
                    current_group = [rect]
        if current_group:
            groups.append(current_group)
        return groups

    def update(self):
        self._calculate_scale_offset()
        # Clear old contours
        for _, contour in self.contour_objs.items():
            contour.deleteLater()
        self.contour_objs.clear()
        # Create new contour objects
        for group_idx, group in enumerate(self.results):
            for idx, child in enumerate(group):
                if child is None:
                    continue
                contour_tag = (group_idx, idx)
                contour = ContourWidget(self, contour_tag=contour_tag, changed_cb=self.contour_changed)
                contour.set_rect(child[2] * self.scale_factor, child[3] * self.scale_factor)
                contour.color = idx
                # Correctly position the contour using image to window conversion
                win_x, win_y = self.image_to_window_coord(child[0], child[1])
                contour.position = (win_x, win_y)
                self.contour_objs[contour_tag] = contour
                contour.show()
    
    def contour_changed(self, contour_tag):
        contour = self.contour_objs.get(contour_tag)
        if not contour:
            return
        x, y = self.window_to_image_coord(contour.x(), contour.y())
        w, h = int(contour.rect.width() / self.scale_factor), int(contour.rect.height() / self.scale_factor)
        roi = self.inverted_gray[y:y+h, x:x+w]
        gray_integral = np.sum(roi)
        old_gray_integral = self.results[contour_tag[0]][contour_tag[1]][4]
        print(f"old integral: {old_gray_integral} -> new integral: {gray_integral}")
        self.results[contour_tag[0]][contour_tag[1]] = (x, y, w, h, gray_integral)

    def contour_add(self, group_idx):
        pass

    def contour_delete(self, contour_tag):
        contour = self.contour_objs.get(contour_tag)
        if not contour:
            return
        contour.deleteLater()
        group_idx, idx = contour_tag
        self.results[group_idx][idx] = None # Mark as deleted
        self.contour_objs.pop(contour_tag)

    def update_grey_value_list(self):
        for group_idx, group in enumerate(self.results):
            if group_idx not in self.grey_value_list_objs:
                grey_value_list = GreyValueList(self)
                self.grey_value_list_objs[group_idx] = grey_value_list
            else:
                grey_value_list = self.grey_value_list_objs[group_idx]
            grey_value_list.update_values(group)
            grey_value_list.show()

    def _resize_image_label(self):
        if self.original_image is None:
            return
        h, w, ch = self.original_image.shape
        main_window_width = self.parent().width()
        main_window_height = self.parent().height()
        # Calculate the scale factor to fit the image within the window
        scale_w = main_window_width / w
        scale_h = main_window_height / h
        self.scale_factor = min(scale_w, scale_h)
        scaled_width = int(w * self.scale_factor)
        scaled_height = int(h * self.scale_factor)
        self.image_label.resize(scaled_width, scaled_height)
        self.image_label.move((main_window_width - scaled_width) // 2, 
                              (main_window_height - scaled_height) // 2)
        # print(f"image_label size: {self.image_label.width()} x {self.image_label.height()}")

    def _calculate_scale_offset(self):
        if self.original_image is None:
            return
            # 获取原始图像尺寸
        img_h, img_w = self.original_image.shape[:2]
        # 获取标签显示区域尺寸
        label_w = self.image_label.width()
        label_h = self.image_label.height()

        # 计算保持宽高比的缩放比例
        scale_w = label_w / img_w
        scale_h = label_h / img_h
        self.scale_factor = min(scale_w, scale_h)

        # 计算居中偏移量
        scaled_w = int(img_w * self.scale_factor)
        scaled_h = int(img_h * self.scale_factor)
        image_label_pos = self.image_label.pos()
        self.offset = (
            image_label_pos.x() + (label_w - scaled_w) // 2,
            image_label_pos.y() + (label_h - scaled_h) // 2
        )

    def window_to_image_coord(self, x, y):
        """将窗口坐标转换为原始图像坐标"""
        # 减去偏移量并除以缩放比例
        img_x = int((x - self.offset[0]) / self.scale_factor)
        img_y = int((y - self.offset[1]) / self.scale_factor)
        return img_x, img_y

    def image_to_window_coord(self, x, y):
        """将原始图像坐标转换为窗口坐标"""
        # 乘以缩放比例并加上偏移量
        win_x = int(x * self.scale_factor + self.offset[0])
        win_y = int(y * self.scale_factor + self.offset[1])
        return win_x, win_y


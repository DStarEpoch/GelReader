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
    def __init__(self, parent=None, contour_changed_cb=None):
        super().__init__(parent=parent)
        self.gray = None
        self.original_image = None
        self.contour_changed_cb = contour_changed_cb
        self.results = []
        self.image_position_ratio = 0.2
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
        self._background_threshold = 0

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
        self._background_threshold = self._estimate_background_threshold()
        h, w, ch = self.original_image.shape
        if ch != 3:
            QMessageBox.warning(self, "Error", "Unsupported image format. Only RGB images are supported.")
            self.original_image = None
            self.gray = None
            return
        print(f"Image loaded successfully. Shape: {self.original_image.shape}, "
              f"background threshold: {self._background_threshold}")
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

        rects = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            roi = self.gray[y:y+h, x:x+w]

            # Apply threshold to eliminate white areas more strictly
            _, roi_thresh = cv2.threshold(roi, self._background_threshold,
                                          255, cv2.THRESH_BINARY_INV)  # Lower threshold to eliminate more white areas
            gray_integral = np.sum(roi_thresh)  # Calculate integral on thresholded ROI

            rects.append((x, y, w, h, gray_integral))

        self.results = self.group_contours(rects)
        self.update()
        self._resize_image_label()

    def _estimate_background_threshold(self):
        # 计算图像的直方图
        histogram = cv2.calcHist([self.gray], [0], None, [256], [0, 256])
        histogram = histogram.ravel()  # 将直方图转换为一维数组

        # 找到直方图中最大值的索引
        max_index = np.argmax(histogram)
        # 选择最大值索引前10%的灰度值作为阈值
        threshold = max_index - int(0.1 * len(histogram))

        # 确保阈值在有效范围内
        threshold = max(0, min(threshold, 255))

        return threshold

    def group_contours(self, rects):
        sorted_rects = sorted(rects, key=lambda r: (r[0], r[1]))  # Sort by x, then y

        def is_same_group(group_rects, find_rect):
            for rc in group_rects:
                if max(rc[0] + rc[2], find_rect[0] + find_rect[2]) - min(rc[0], find_rect[0]) < rc[2] + find_rect[2]:
                    return True
            return False

        groups: list[list] = []
        for rect in sorted_rects:
            if not groups:
                groups.append([rect, ])
            else:
                for group in groups:
                    if is_same_group(group, rect):
                        group.append(rect)
                        break
                else:
                    groups.append([rect, ])
        for group_idx, group in enumerate(groups):
            groups[group_idx] = sorted(group, key=lambda r: r[1])
        return groups

    def update(self):
        self.update_position()
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
                contour = ContourWidget(self, contour_tag=contour_tag,
                                        changed_cb=self.contour_changed)
                contour.set_rect(child[2] * self.scale_factor, child[3] * self.scale_factor)
                contour.color = idx
                # Correctly position the contour using image to window conversion
                win_x, win_y = self.image_to_window_coord(child[0], child[1])
                contour.position = (win_x, win_y)
                self.contour_objs[contour_tag] = contour
                contour.show()
        self.init_grey_value_list()
    
    def contour_changed(self, contour_tag):
        contour = self.contour_objs.get(contour_tag)
        if not contour:
            return
        x, y = self.window_to_image_coord(contour.x(), contour.y())
        w, h = int(contour.rect.width() / self.scale_factor), int(contour.rect.height() / self.scale_factor)
        roi = self.gray[y:y+h, x:x+w]
        _, roi_thresh = cv2.threshold(roi, self._background_threshold,
                                      255, cv2.THRESH_BINARY_INV)  # Lower threshold to eliminate more white areas
        gray_integral = np.sum(roi_thresh)
        # old_gray_integral = self.results[contour_tag[0]][contour_tag[1]][4]
        self.results[contour_tag[0]][contour_tag[1]] = (x, y, w, h, gray_integral)
        grey_value_list = self.grey_value_list_objs.get(contour_tag[0])
        if grey_value_list:
            grey_value_list.update_data_for_contour_idx(contour_tag[1], gray_integral)

    def contour_add(self, group_idx):
        group_contours = self.results[group_idx]
        left_x = None
        right_x = None
        upper_y = None
        height = 10
        for contour in group_contours:
            if contour is None:
                continue
            x, y, w, h, _ = contour
            if left_x is None or x < left_x:
                left_x = x
            if right_x is None or x + w > right_x:
                right_x = x + w
            if upper_y is None or y + h > upper_y:
                upper_y = y + h
        self.results[group_idx].append((left_x, int(upper_y + height / 2), right_x - left_x, height, 0))
        self.update()
        self._resize_image_label()
        new_contour_tag = (group_idx, len(self.results[group_idx]) - 1)
        self.contour_changed(new_contour_tag)
        self.contour_changed_cb and self.contour_changed_cb(self.results)

    def contour_delete(self, contour_tag):
        contour = self.contour_objs.get(contour_tag)
        if not contour:
            return
        self.contour_objs.pop(contour_tag)
        contour.deleteLater()
        group_idx, idx = contour_tag
        self.results[group_idx][idx] = None     # Mark as deleted
        for group_info in self.results[group_idx]:
            if group_info is not None:
                break
        else:
            self.results[group_idx] = []  # Remove empty group
            grey_value_list = self.grey_value_list_objs.get(group_idx)
            if grey_value_list:
                grey_value_list.deleteLater()
                self.grey_value_list_objs.pop(group_idx)
        self._refresh_grey_value_list()
        self.contour_changed_cb and self.contour_changed_cb(self.results)

    def init_grey_value_list(self):
        # 清空旧的灰度值列表
        for group_idx in list(self.grey_value_list_objs.keys()):
            self.grey_value_list_objs[group_idx].deleteLater()
        self.grey_value_list_objs.clear()

        # 创建新的灰度值列表
        for group_idx, group in enumerate(self.results):
            if not group:
                continue
            grey_value_list = GreyValueList(group_idx, self, delete_cb=self.contour_delete, add_cb=self.contour_add)
            grey_value_list.update_values(group)
            grey_value_list.show()
            self.grey_value_list_objs[group_idx] = grey_value_list

    def _refresh_grey_value_list(self):
        for group_idx, group in enumerate(self.results):
            grey_value_list = self.grey_value_list_objs.get(group_idx)
            if not grey_value_list:
                continue
            # 将灰度值列表放置在相应轮廓对象的正下方
            if group:
                # 获取轮廓左侧坐标
                lower_x = None
                for contour_idx in range(len(group)):
                    contour_tag = (group_idx, contour_idx)
                    contour = self.contour_objs.get(contour_tag)
                    if not contour:
                        continue
                    if lower_x is None or contour.position.x() < lower_x:
                        lower_x = contour.position.x()
                if lower_x is not None:
                    grey_value_list.move(lower_x,
                                         self.offset[1] + int(self.original_image.shape[0] * self.scale_factor))

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
        self.update_position()
        self._refresh_grey_value_list()
    
    def update_position(self):
        """根据比例值调整图片的位置"""
        if self.original_image is None:
            return
        main_window_height = self.parent().height()
        scaled_height = int(self.original_image.shape[0] * self.scale_factor)
        offset_y = int((main_window_height - scaled_height) * self.image_position_ratio)
        self.image_label.move((self.parent().width() - self.image_label.width()) // 2, offset_y)

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


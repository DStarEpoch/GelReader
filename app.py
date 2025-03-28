#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/3/25 10:43
# @Author : yuyeqing
# @File   : app.py
# @IDE    : PyCharm
import sys
import csv
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, \
    QFileDialog, QMessageBox, QApplication
from PyQt6.QtGui import QAction, QIcon
from components.image_manager import ImageManager
from components.color_name_manager import ColorNameManager


class Application(QMainWindow):
    def __init__(self):
        super(Application, self).__init__()
        self.image_mgr = ImageManager(self)
        # self.color_mgr = ColorNameManager(self)
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Gel Picture Analyzer")
        self.setGeometry(150, 150, 1024, 640)

        # menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        img_load = QAction(QIcon('assets/import.png'), "Load Image", self)
        img_load.triggered.connect(self.load_image)
        file_menu.addAction(img_load)
        data_export = QAction(QIcon('assets/export.png'), "Export Data", self)
        data_export.triggered.connect(self.export_to_csv)
        file_menu.addAction(data_export)

        # tools bar
        tb = self.addToolBar("Tools")
        analyze_act = QAction(QIcon('assets/analyze.png'), 'analyze', self)
        analyze_act.triggered.connect(self.analyze_image)
        tb.addAction(analyze_act)

        # add components
        top_panel = QWidget()
        top_layout = QVBoxLayout()
        # top_layout.addWidget(self.color_mgr)
        top_layout.addWidget(self.image_mgr)
        top_panel.setLayout(top_layout)
        self.setCentralWidget(top_panel)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.image_mgr.resizeEvent(event)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Gel Picture', '', 'Images (*.png *.jpg)')
        if path:
            self.image_mgr.load_image(path)

    def analyze_image(self):
        if self.image_mgr.original_image is None:
            # popup
            QMessageBox.warning(self, "Warning", "Please open an image first.")
            return
        self.image_mgr.analyze()
        # self.color_mgr.update_colors(self.image_mgr.results)

    def export_to_csv(self):
        if not self.image_mgr.results:
            QMessageBox.warning(self, "Warning", "No analyzed data to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if path:
            max_contour_idx = max([len(self.image_mgr.results[group_idx]) for group_idx in
                                   range(len(self.image_mgr.results))])
            with open(path, 'w', newline='') as csvfile:
                fieldnames = ['Group', ] + [f'Contour_{i}' for i in range(max_contour_idx)]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for group_idx in range(len(self.image_mgr.results)):
                    group_data = {
                        'Group': group_idx
                    }
                    for contour_idx in range(len(self.image_mgr.results[group_idx])):
                        res = self.image_mgr.results[group_idx][contour_idx]
                        if res is None:
                            gray_data = None
                        else:
                            gray_data = res[-1]
                        group_data[f'Contour_{contour_idx}'] = gray_data
                    writer.writerow(group_data)



def main():
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

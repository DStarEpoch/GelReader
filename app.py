#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025/3/25 10:43
# @Author : yuyeqing
# @File   : app.py
# @IDE    : PyCharm
import sys
import csv
import yaml
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, \
    QFileDialog, QMessageBox, QApplication
from PyQt6.QtGui import QAction, QIcon
from share.resource import resource_path
from components.image_manager import ImageManager
from components.color_name_manager import ColorNameManager


class Application(QMainWindow):
    def __init__(self):
        super(Application, self).__init__()
        self.image_mgr = ImageManager(self, contour_changed_cb=self.on_contour_changed)
        self.color_mgr = ColorNameManager(self)
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Gel Picture Analyzer")
        self.setGeometry(150, 150, 1024, 640)

        # menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        img_load = QAction(QIcon(resource_path('assets/import.png')), "Load Image", self)
        img_load.triggered.connect(self.load_image)
        file_menu.addAction(img_load)
        data_export = QAction(QIcon(resource_path('assets/export.png')), "Export Data", self)
        data_export.triggered.connect(self.export_to_csv)
        file_menu.addAction(data_export)

        # config menu
        config_menu = menubar.addMenu("Config")
        config_load = QAction(QIcon(resource_path('assets/import.png')), "Load Config", self)
        config_load.triggered.connect(self.load_config)
        config_menu.addAction(config_load)
        config_export = QAction(QIcon(resource_path('assets/export.png')), "Export Config", self)
        config_export.triggered.connect(self.export_config)
        config_menu.addAction(config_export)

        # tools bar
        tb = self.addToolBar("Tools")
        analyze_act = QAction(QIcon(resource_path('assets/analyze.png')), 'analyze', self)
        analyze_act.triggered.connect(self.analyze_image)
        tb.addAction(analyze_act)

        # add components
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 添加顶部颜色管理器
        main_layout.addWidget(self.color_mgr)
        # 添加图像管理器
        main_layout.addWidget(self.image_mgr)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

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
            QMessageBox.warning(self, "Warning", "Please load an image first.")
            return
        self.image_mgr.analyze()
        self.color_mgr.update_color_names(self.image_mgr.results)

    def on_contour_changed(self, results):
        self.color_mgr.update_color_names(results)

    def export_to_csv(self):
        if not self.image_mgr.results:
            QMessageBox.warning(self, "Warning", "No analyzed data to export.")
            return
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
            if path:
                color_name_dict = self.color_mgr.color_names
                with open(path, 'w', newline='') as csvfile:
                    fieldnames = ['Group', ] + [color_name for _, color_name in color_name_dict.items()]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for group_idx in range(len(self.image_mgr.results)):
                        if not self.image_mgr.results[group_idx]:
                            continue
                        group_data = {
                            'Group': self.image_mgr.group_names.get(group_idx, f"Group{group_idx}"),
                        }
                        for contour_idx in range(len(self.image_mgr.results[group_idx])):
                            res = self.image_mgr.results[group_idx][contour_idx]
                            if res is None:
                                gray_data = None
                            else:
                                gray_data = res[-1]
                            group_data[color_name_dict[contour_idx]] = gray_data
                        writer.writerow(group_data)
                QMessageBox.information(self, "Success", "Data exported successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {e}")

    def export_config(self):
        if not self.color_mgr.color_names:
            QMessageBox.warning(self, "Warning", "No config data to export.")
            return
        config = self.color_mgr.export_color_name_config()
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Save Config", "", "Yaml Files (*.yaml)")
            if path:
                with open(path, 'w') as f:
                    yaml.dump(config, f)
                QMessageBox.information(self, "Success", "Config exported successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export config: {e}")

    def load_config(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Contour Color Name Config", "", "Yaml Files (*.yaml *.yml)")
        if path:
            try:
                with open(path, 'r') as f:
                    config = yaml.load(f, Loader=yaml.FullLoader)
                self.color_mgr.load_color_name_config(config)
                QMessageBox.information(self, "Success", "Config loaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load config: {e}")


def main():
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

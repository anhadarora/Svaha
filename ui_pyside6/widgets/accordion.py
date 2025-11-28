from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)
import json


class AccordionItem(QFrame):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setObjectName("accordion-item")
        self.setFrameShape(QFrame.StyledPanel)

        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 10, 10, 10)

        self.toggle_button = QPushButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                background-color: transparent;
                font-weight: bold;
                text-align: left;
                padding: 5px;
            }
        """
        )

        self.share_button = QPushButton("Share")
        self.share_button.setStyleSheet(
            """
            QPushButton {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
        """
        )

        header_layout.addWidget(self.toggle_button)
        header_layout.addStretch()
        header_layout.addWidget(self.share_button)

        self.content_area = QWidget()
        self.content_area.setLayout(QVBoxLayout())
        self.content_area.layout().addWidget(content)
        self.content_area.setMaximumHeight(0)
        self.content_area.setVisible(False)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.content_area)
        main_layout.addStretch()

        self.toggle_animation = QParallelAnimationGroup(self)
        self.content_animation = QPropertyAnimation(
            self.content_area, b"maximumHeight")
        self.content_animation.setDuration(300)
        self.content_animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.toggle_button.clicked.connect(self.toggle)
        self.share_button.clicked.connect(self.share_content)

    def toggle(self, checked):
        self.content_area.setVisible(checked)
        self.toggle_animation.setDirection(
            QPropertyAnimation.Forward if checked else QPropertyAnimation.Backward
        )
        self.toggle_animation.start()

    def set_content_height(self, height):
        self.content_animation.setStartValue(0)
        self.content_animation.setEndValue(height)
        self.toggle_animation.addAnimation(self.content_animation)

    def share_content(self):
        content_data = {"title": self.toggle_button.text(), "content": "dummy content"}

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "JSON Files (*.json)"
        )
        if file_path:
            with open(file_path, "w") as f:
                json.dump(content_data, f, indent=4)


class Accordion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)

    def add_item(self, title, widget):
        item = AccordionItem(title, widget)
        self.layout.addWidget(item)
        item.set_content_height(widget.sizeHint().height())
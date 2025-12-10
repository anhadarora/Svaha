import json
import os
import markdown
from PySide6.QtCore import QObject, QEvent, Qt, QTimer, QPoint
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from PySide6.QtGui import QPalette, QColor, QScreen


class CustomTooltip(QLabel):
    """A custom QLabel styled to look like a modern tooltip."""
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.setAttribute(Qt.WA_TranslucentBackground) # This was causing issues
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWordWrap(True)
        self.setMargin(10)
        
        self.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            h3 {
                color: #0d6efd;
                font-weight: bold;
            }
            strong {
                color: #ffc107;
            }
        """)

    def show_at(self, pos: QPoint, text: str):
        self.setText(text)
        self.adjustSize()

        screen = QApplication.screenAt(pos)
        if not screen:
            screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        final_pos = pos
        if final_pos.x() + self.width() > screen_geometry.right():
            final_pos.setX(pos.x() - self.width() - 15)
        if final_pos.y() + self.height() > screen_geometry.bottom():
            final_pos.setY(pos.y() - self.height() - 15)
            
        self.move(final_pos)
        self.show()


class TooltipManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TooltipManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.tooltip_data = {}
            self.custom_tooltip = CustomTooltip()
            self._initialized = True

    def load_tooltips(self, filepath="tooltips.json"):
        try:
            with open(filepath, "r") as f:
                self.tooltip_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[ERROR] Could not load or parse tooltip file: {e}")
            self.tooltip_data = {}

    def get_tooltip_for_widget(self, widget: QWidget):
        if not widget:
            return None
        
        current_widget = widget
        while current_widget:
            object_name = current_widget.objectName()
            if object_name and object_name in self.tooltip_data:
                return self.tooltip_data[object_name]
            current_widget = current_widget.parentWidget()
        return None

    def format_tooltip(self, data: dict):
        title = data.get("title", "")
        content = data.get("content", "")
        options = data.get("options", {})

        html = f"<h3>{title}</h3><p>{content}</p>"
        if options:
            html += "<hr><strong>Options:</strong><ul>"
            for key, value in options.items():
                html += f"<li><strong>{key}:</strong> {value}</li>"
            html += "</ul>"
        
        return markdown.markdown(html, extensions=['extra'])

    def show_tooltip(self, pos: QPoint, widget: QWidget):
        tooltip_data = self.get_tooltip_for_widget(widget)
        if tooltip_data:
            formatted_text = self.format_tooltip(tooltip_data)
            self.custom_tooltip.show_at(pos, formatted_text)
        else:
            self.hide_tooltip()

    def hide_tooltip(self):
        self.custom_tooltip.hide()


class TooltipEventFilter(QObject):
    def __init__(self, manager: TooltipManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.hover_widget = None

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.MouseMove:
            modifiers = QApplication.keyboardModifiers()
            is_hotkey_pressed = bool(modifiers & Qt.ControlModifier) or bool(modifiers & Qt.AltModifier)

            if is_hotkey_pressed:
                widget_under_cursor = QApplication.widgetAt(event.globalPos())
                
                if widget_under_cursor != self.hover_widget:
                    self.hover_widget = widget_under_cursor
                    if self.hover_widget:
                        self.manager.show_tooltip(event.globalPos() + QPoint(15, 15), self.hover_widget)
            else:
                if self.hover_widget is not None:
                    self.hover_widget = None
                    self.manager.hide_tooltip()

        elif event.type() == QEvent.KeyRelease:
            if event.key() in [Qt.Key_Control, Qt.Key_Alt]:
                self.hover_widget = None
                self.manager.hide_tooltip()
        
        elif event.type() == QEvent.Leave:
            self.hover_widget = None
            self.manager.hide_tooltip()

        return super().eventFilter(watched, event)

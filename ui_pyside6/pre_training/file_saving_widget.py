from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QLineEdit,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QSizePolicy,
)
from PySide6.QtCore import Signal
import os

class FileSavingWidget(QWidget):
    configuration_changed = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("file_saving")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("File Saving Parameters")
        group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.layout.addWidget(group)

        layout = QVBoxLayout(group)

        self.model_path_edit = self._create_path_selector(
            layout, 
            "Model Save Path:", 
            os.path.abspath("./build/models"),
            "model_save_path"
        )
        self.training_data_path_edit = self._create_path_selector(
            layout, 
            "Training Data (Images) Path:", 
            os.path.abspath("./build/data/training"),
            "training_data_path"
        )
        self.augmented_data_path_edit = self._create_path_selector(
            layout, 
            "Augmented Data Path:", 
            os.path.abspath("./build/data/augmented"),
            "augmented_data_path"
        )

    def connect_signals(self):
        self.model_path_edit.textChanged.connect(self.configuration_changed)
        self.training_data_path_edit.textChanged.connect(self.configuration_changed)
        self.augmented_data_path_edit.textChanged.connect(self.configuration_changed)

    def _create_path_selector(self, parent_layout, label_text, default_path, object_name_base):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        layout.addWidget(label)
        
        line_edit = QLineEdit(default_path)
        line_edit.setObjectName(f"file_saving.{object_name_base}_input")
        label.setBuddy(line_edit)
        layout.addWidget(line_edit)
        
        button = QPushButton("Browse...")
        button.setObjectName(f"file_saving.{object_name_base}_browse_button")
        button.clicked.connect(lambda: self._open_directory_dialog(line_edit))
        layout.addWidget(button)
        
        parent_layout.addLayout(layout)
        return line_edit

    def _open_directory_dialog(self, line_edit):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", line_edit.text())
        if directory:
            line_edit.setText(directory)

    def get_parameters(self):
        return {
            "model_save_path": self.model_path_edit.text(),
            "training_data_path": self.training_data_path_edit.text(),
            "augmented_data_path": self.augmented_data_path_edit.text(),
        }
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QSlider,
    QCheckBox,
    QLineEdit,
)
from PySide6.QtCore import Qt


class ModelArchitectureWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Model Architecture Parameters")
        self.layout.addWidget(group)

        form_layout = QFormLayout(group)

        self.input_format = QComboBox()
        self.input_format.addItems(["Image Snapshot", "Raw Numeric Vectors"])
        form_layout.addRow("Input Format:", self.input_format)

        self.model_type = QComboBox()
        self.model_type.addItems(["Vision Transformer (ViT)", "Convolutional Neural Network (CNN)"])
        form_layout.addRow("Model Type:", self.model_type)

        self.enable_sequential_input = QCheckBox()
        form_layout.addRow("Enable Sequential Input:", self.enable_sequential_input)

        self.sequence_length = QSlider(Qt.Horizontal)
        self.sequence_length.setRange(2, 10)
        form_layout.addRow("Sequence Length (S):", self.sequence_length)

        self.sequence_handling_method = QComboBox()
        self.sequence_handling_method.addItems(["Fixed Length", "Padding + Masking"])
        form_layout.addRow("Sequence Handling Method:", self.sequence_handling_method)

        self.enable_delta_features = QCheckBox()
        form_layout.addRow("Enable Delta Features:", self.enable_delta_features)

        self.delta_method = QComboBox()
        self.delta_method.addItems(["Feature Subtraction (Latent)", "Image Subtraction (Pixel)"])
        form_layout.addRow("Delta Method:", self.delta_method)

        self.learning_rate = QLineEdit("0.001")
        form_layout.addRow("Learning Rate:", self.learning_rate)

        self.batch_size = QLineEdit("32")
        form_layout.addRow("Batch Size:", self.batch_size)

        self.epochs = QLineEdit("100")
        form_layout.addRow("Epochs:", self.epochs)

        self.optimizer = QComboBox()
        self.optimizer.addItems(["Adam", "SGD", "RMSprop"])
        form_layout.addRow("Optimizer:", self.optimizer)

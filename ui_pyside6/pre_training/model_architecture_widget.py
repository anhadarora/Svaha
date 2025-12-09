from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QGridLayout,
    QFormLayout,
    QComboBox,
    QCheckBox,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QLabel,
)
from PySide6.QtCore import Signal, Qt


class ModelArchitectureWidget(QWidget):
    """A widget to configure the model architecture, including backbone, sequence modeling, and prediction heads."""

    configuration_changed = Signal()
    prediction_heads_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- 1. Backbone Architecture ---
        backbone_group = QGroupBox("Backbone Architecture (Vision Encoder)")
        self.layout.addWidget(backbone_group)
        backbone_layout = QGridLayout(backbone_group)

        self.architecture_selection = QComboBox()
        self.architecture_selection.addItems([
            "EfficientNet-B7",
            "ResNet-50",
            "ViT-Base-Patch16",
            "Swin-Transformer",
        ])
        architecture_label = QLabel("Backbone:")
        architecture_label.setBuddy(self.architecture_selection)
        
        self.pretrained_weights = QCheckBox("Use Pre-trained Weights (ImageNet)")
        self.pretrained_weights.setChecked(True)
        
        self.freeze_backbone = QCheckBox("Freeze Backbone (Transfer Learning)")
        self.freeze_backbone.setChecked(True)

        backbone_layout.addWidget(architecture_label, 0, 0)
        backbone_layout.addWidget(self.architecture_selection, 0, 1)
        backbone_layout.addWidget(self.pretrained_weights, 1, 0, 1, 2)
        backbone_layout.addWidget(self.freeze_backbone, 2, 0, 1, 2)

        # --- 2. Sequence Modeling ---
        self.sequence_group = QGroupBox("Sequence Modeling (Temporal Aggregator)")
        self.layout.addWidget(self.sequence_group)
        sequence_layout = QFormLayout(self.sequence_group)

        self.temporal_aggregator = QComboBox()
        self.temporal_aggregator.addItems([
            "None (Channel Stack)",
            "Time-Distributed CNN + LSTM",
            "Transformer Encoder",
        ])
        sequence_layout.addRow("Method:", self.temporal_aggregator)

        # --- 3. Prediction Heads ---
        heads_group = QGroupBox("Prediction Heads (Task Definition)")
        self.layout.addWidget(heads_group)
        heads_layout = QVBoxLayout(heads_group)
        
        primary_head_layout = QFormLayout()
        self.primary_output = QComboBox()
        self.primary_output.addItems([
            "Scalar Regression (Return %)",
            "Classification (Buy/Sell/Hold)",
        ])
        primary_head_layout.addRow("Primary Output:", self.primary_output)
        heads_layout.addLayout(primary_head_layout)

        aux_heads_group = QGroupBox("Auxiliary Heads (Multi-Task Learning)")
        aux_heads_layout = QVBoxLayout(aux_heads_group)
        self.rally_time_prediction = QCheckBox("Rally Time Prediction (Regression)")
        self.directional_confidence = QCheckBox("Directional Confidence (Classification)")
        aux_heads_layout.addWidget(self.rally_time_prediction)
        aux_heads_layout.addWidget(self.directional_confidence)
        heads_layout.addWidget(aux_heads_group)

        head_arch_group = QGroupBox("Head Architecture")
        head_arch_layout = QGridLayout(head_arch_group)
        
        hidden_units_label = QLabel("Hidden Units:")
        self.hidden_units = QSpinBox()
        self.hidden_units.setRange(64, 4096)
        self.hidden_units.setValue(512)
        hidden_units_label.setBuddy(self.hidden_units)

        dropout_label = QLabel("Dropout:")
        self.dropout = QDoubleSpinBox()
        self.dropout.setRange(0.0, 0.9)
        self.dropout.setSingleStep(0.05)
        self.dropout.setValue(0.2)
        dropout_label.setBuddy(self.dropout)

        activation_label = QLabel("Activation:")
        self.activation = QComboBox()
        self.activation.addItems(["ReLU", "GeLU", "SiLU"])
        activation_label.setBuddy(self.activation)

        head_arch_layout.addWidget(hidden_units_label, 0, 0)
        head_arch_layout.addWidget(self.hidden_units, 0, 1)
        head_arch_layout.addWidget(dropout_label, 1, 0)
        head_arch_layout.addWidget(self.dropout, 1, 1)
        head_arch_layout.addWidget(activation_label, 2, 0)
        head_arch_layout.addWidget(self.activation, 2, 1)
        heads_layout.addWidget(head_arch_group)

        # --- 4. Training Hyperparameters ---
        hyperparams_group = QGroupBox("Training Hyperparameters")
        self.layout.addWidget(hyperparams_group)
        hyperparams_layout = QGridLayout(hyperparams_group)

        lr_label = QLabel("Learning Rate:")
        self.learning_rate = QLineEdit("1e-3")
        lr_label.setBuddy(self.learning_rate)

        optimizer_label = QLabel("Optimizer:")
        self.optimizer = QComboBox()
        self.optimizer.addItems(["Adam", "SGD", "RMSprop", "AdamW"])
        optimizer_label.setBuddy(self.optimizer)

        loss_label = QLabel("Loss Function:")
        self.loss_function = QComboBox()
        self.loss_function.addItems(["MSE", "MAE", "Huber"])
        loss_label.setBuddy(self.loss_function)

        batch_size_label = QLabel("Batch Size:")
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 8192)
        self.batch_size.setValue(32)
        batch_size_label.setBuddy(self.batch_size)

        epochs_label = QLabel("Max Epochs:")
        self.max_epochs = QSpinBox()
        self.max_epochs.setRange(1, 1000)
        self.max_epochs.setValue(100)
        epochs_label.setBuddy(self.max_epochs)

        patience_label = QLabel("Early Stopping Patience:")
        self.early_stopping_patience = QSpinBox()
        self.early_stopping_patience.setRange(0, 100)
        self.early_stopping_patience.setValue(10)
        patience_label.setBuddy(self.early_stopping_patience)

        hyperparams_layout.addWidget(lr_label, 0, 0)
        hyperparams_layout.addWidget(self.learning_rate, 0, 1)
        hyperparams_layout.addWidget(optimizer_label, 1, 0)
        hyperparams_layout.addWidget(self.optimizer, 1, 1)
        hyperparams_layout.addWidget(loss_label, 2, 0)
        hyperparams_layout.addWidget(self.loss_function, 2, 1)
        hyperparams_layout.addWidget(batch_size_label, 0, 2)
        hyperparams_layout.addWidget(self.batch_size, 0, 3)
        hyperparams_layout.addWidget(epochs_label, 1, 2)
        hyperparams_layout.addWidget(self.max_epochs, 1, 3)
        hyperparams_layout.addWidget(patience_label, 2, 2)
        hyperparams_layout.addWidget(self.early_stopping_patience, 2, 3)

        # --- 5. Input Constraints ---
        constraints_group = QGroupBox("Input Constraints")
        self.layout.addWidget(constraints_group)
        constraints_layout = QGridLayout(constraints_group)

        channels_label = QLabel("Input Channels:")
        self.input_channels = QSpinBox()
        self.input_channels.setRange(1, 64)
        self.input_channels.setValue(3)
        channels_label.setBuddy(self.input_channels)

        resolution_label = QLabel("Target Resolution:")
        self.target_resolution_display = QLineEdit("e.g., 64x128")
        self.target_resolution_display.setReadOnly(True)
        self.target_resolution_display.setStyleSheet("background-color: #2a2a2a;")
        resolution_label.setBuddy(self.target_resolution_display)

        constraints_layout.addWidget(channels_label, 0, 0)
        constraints_layout.addWidget(self.input_channels, 0, 1)
        constraints_layout.addWidget(resolution_label, 0, 2)
        constraints_layout.addWidget(self.target_resolution_display, 0, 3)

        self.layout.addStretch()

    def connect_signals(self):
        """Connect all widget signals to the configuration_changed signal."""
        self.architecture_selection.currentIndexChanged.connect(self.configuration_changed)
        self.pretrained_weights.toggled.connect(self.configuration_changed)
        self.freeze_backbone.toggled.connect(self.configuration_changed)
        
        self.temporal_aggregator.currentIndexChanged.connect(self.configuration_changed)
        
        self.primary_output.currentIndexChanged.connect(self.configuration_changed)
        self.rally_time_prediction.toggled.connect(self.configuration_changed)
        self.directional_confidence.toggled.connect(self.configuration_changed)
        
        self.primary_output.currentIndexChanged.connect(self._emit_prediction_heads_changed)
        self.rally_time_prediction.toggled.connect(self._emit_prediction_heads_changed)
        self.directional_confidence.toggled.connect(self._emit_prediction_heads_changed)

        self.hidden_units.valueChanged.connect(self.configuration_changed)
        self.dropout.valueChanged.connect(self.configuration_changed)
        self.activation.currentIndexChanged.connect(self.configuration_changed)
        
        self.learning_rate.textChanged.connect(self.configuration_changed)
        self.optimizer.currentIndexChanged.connect(self.configuration_changed)
        self.loss_function.currentIndexChanged.connect(self.configuration_changed)
        self.batch_size.valueChanged.connect(self.configuration_changed)
        self.max_epochs.valueChanged.connect(self.configuration_changed)
        self.early_stopping_patience.valueChanged.connect(self.configuration_changed)

        self.input_channels.valueChanged.connect(self.configuration_changed)

    def _emit_prediction_heads_changed(self):
        state = {
            "primary": self.primary_output.currentText(),
            "rally_time": self.rally_time_prediction.isChecked(),
            "directional_confidence": self.directional_confidence.isChecked(),
        }
        self.prediction_heads_changed.emit(state)

    def get_parameters(self):
        """Return a dictionary of the current configuration."""
        return {
            "backbone": {
                "architecture": self.architecture_selection.currentText(),
                "pretrained": self.pretrained_weights.isChecked(),
                "freeze": self.freeze_backbone.isChecked(),
            },
            "sequence_modeling": {
                "aggregator": self.temporal_aggregator.currentText(),
            },
            "prediction_heads": {
                "primary_output": self.primary_output.currentText(),
                "auxiliary_heads": {
                    "rally_time": self.rally_time_prediction.isChecked(),
                    "directional_confidence": self.directional_confidence.isChecked(),
                },
                "head_architecture": {
                    "hidden_units": self.hidden_units.value(),
                    "dropout": self.dropout.value(),
                    "activation": self.activation.currentText(),
                },
            },
            "training": {
                "learning_rate": self.learning_rate.text(),
                "optimizer": self.optimizer.currentText(),
                "loss_function": self.loss_function.currentText(),
                "batch_size": self.batch_size.value(),
                "max_epochs": self.max_epochs.value(),
                "early_stopping_patience": self.early_stopping_patience.value(),
            },
            "input_constraints": {
                "input_channels": self.input_channels.value(),
            },
        }

    def set_target_resolution(self, resolution_text):
        """Slot to update the read-only resolution display."""
        self.target_resolution_display.setText(resolution_text)
    
    def set_sequence_modeling_visibility(self, n_value):
        """Slot to show or hide the Sequence Modeling group based on N value."""
        self.sequence_group.setVisible(n_value > 1)

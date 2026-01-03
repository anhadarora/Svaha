from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QTextEdit,
    QSizePolicy
)
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QFont
import json
import os
import logging
import multiprocessing
from queue import Empty

from analysis.training_worker import TrainingWorker
from ..training.run_status_widget import RunStatusWidget
from ..training.progress_indicators_widget import ProgressIndicatorsWidget
from ..training.plots.combined_metric_plot_widget import CombinedMetricPlotWidget

class MonitorTabWidget(QWidget):
    training_run_completed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.training_process = None
        self.queue = None
        self.logger = logging.getLogger(__name__)
        self.dynamic_plots = []
        
        self.queue_timer = QTimer(self)
        self.queue_timer.timeout.connect(self._check_worker_queue)
        
        # --- Main Layout ---
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- Top Bar ---
        top_bar_widget = QWidget()
        top_bar_layout = QHBoxLayout(top_bar_widget)
        self.begin_button = QPushButton("Begin Experiment")
        self.begin_button.clicked.connect(self._on_begin_clicked)
        top_bar_layout.addWidget(self.begin_button)
        top_bar_layout.addStretch()
        self.run_status_widget = RunStatusWidget()
        self.progress_indicators_widget = ProgressIndicatorsWidget()
        top_bar_layout.addWidget(self.run_status_widget)
        top_bar_layout.addWidget(self.progress_indicators_widget)
        self.layout.addWidget(top_bar_widget)

        # --- Scroll Area for Plots and Log ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.layout.addWidget(scroll_area)

        container = QWidget()
        scroll_area.setWidget(container)
        self.main_grid = QGridLayout(container)

        # --- Log View (will be at the bottom) ---
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Courier", 10))
        self.log_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        self.main_grid.addWidget(self.log_view, 1, 0, 1, 2) # Start at row 1
        self.main_grid.setRowStretch(0, 1) # Plots area will stretch
        self.main_grid.setRowStretch(1, 0) # Log view will not stretch initially

    def begin_training(self):
        self.begin_button.click()

    def _on_begin_clicked(self):
        config_path = os.path.abspath("./build/last_applied_config.json")
        if not os.path.exists(config_path):
            QMessageBox.critical(self, "Error", "No configuration applied. Please go to the Setup tab and click 'Apply' first.")
            return

        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            
            self._reset_ui()
            self._setup_plots(config)
            self.log_view.append("Starting training process...")
            
            self.begin_button.setEnabled(False)
            self.begin_button.setText("Experiment Running...")
            
            self.queue = multiprocessing.Queue()
            self.training_process = TrainingWorker(config, self.queue)
            self.training_process.start()
            self.queue_timer.start(100)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start training process:\n{e}")
            self._reset_button()

    def _setup_plots(self, config):
        self._clear_plots()
        
        # 1. Add total loss plot
        total_loss_plot = CombinedMetricPlotWidget("Total Loss", "loss", "val_loss", "Loss")
        self.dynamic_plots.append(total_loss_plot)
        
        # 2. Add plots for each head
        heads_cfg = config.get('prediction_heads', {})
        if 'Regression' in heads_cfg.get('primary_output', ''):
            self.dynamic_plots.append(CombinedMetricPlotWidget("Regression Head Loss", "label_regression_loss", "val_label_regression_loss", "Loss"))
        
        if 'Classification' in heads_cfg.get('primary_output', ''):
            self.dynamic_plots.append(CombinedMetricPlotWidget("Classification Head Loss", "label_classification_loss", "val_label_classification_loss", "Loss"))
            self.dynamic_plots.append(CombinedMetricPlotWidget("Classification Head Accuracy", "label_classification_accuracy", "val_label_classification_accuracy", "Accuracy"))

        aux_heads = heads_cfg.get('auxiliary_heads', {})
        if aux_heads.get('rally_time'):
            self.dynamic_plots.append(CombinedMetricPlotWidget("Rally Time Head Loss", "label_rally_time_loss", "val_label_rally_time_loss", "Loss"))
        if aux_heads.get('directional_confidence'):
            self.dynamic_plots.append(CombinedMetricPlotWidget("Directional Confidence Head Loss", "label_directional_confidence_loss", "val_label_directional_confidence_loss", "Loss"))
            self.dynamic_plots.append(CombinedMetricPlotWidget("Directional Confidence Head Accuracy", "label_directional_confidence_accuracy", "val_label_directional_confidence_accuracy", "Accuracy"))

        # 3. Add plots to the grid
        row, col = 0, 0
        for plot in self.dynamic_plots:
            self.main_grid.addWidget(plot, row, col)
            col += 1
            if col > 1: # 2 plots per row
                col = 0
                row += 1
        
        # Move log view to the next row
        self.main_grid.addWidget(self.log_view, row + 1, 0, 1, 2)

    def _check_worker_queue(self):
        if self.queue is None: return
        try:
            while not self.queue.empty():
                message = self.queue.get_nowait()
                msg_type = message.get("type")
                
                if msg_type == "log":
                    self.log_view.append(message.get("message", ""))
                elif msg_type == "epoch":
                    self._update_ui_with_metrics(message.get("data"))
                elif msg_type == "finished":
                    self._on_training_finished(message.get("data"))
                    return # Stop processing queue as it is now None
        except Empty:
            pass
        except Exception as e:
            self.logger.error(f"Error processing worker queue: {e}")
            self.log_view.append(f"--- ERROR: Could not process message from worker: {e} ---")

    def _update_ui_with_metrics(self, metrics):
        # Log detailed breakdown
        log_message = f"Epoch {metrics.get('epoch')}: "
        details = [f"{key}: {value:.4f}" for key, value in metrics.items() if key != 'epoch']
        log_message += " | ".join(details)
        self.log_view.append(log_message)
        
        # Update all dynamic plots
        for plot in self.dynamic_plots:
            plot.update_data(metrics)

    def _on_training_finished(self, final_results):
        self.queue_timer.stop()
        if self.training_process:
            self.training_process.join(timeout=5)
        self.training_process = None
        self.queue = None

        self._reset_button()
        self.log_view.append("\n--- TRAINING COMPLETE ---")
        QMessageBox.information(self, "Training Complete", "The training process has finished.")
        self.training_run_completed.emit(final_results)

    def _clear_plots(self):
        for plot in self.dynamic_plots:
            plot.deleteLater()
        self.dynamic_plots.clear()

    def _reset_ui(self):
        self.log_view.clear()
        self._clear_plots()

    def _reset_button(self):
        self.begin_button.setEnabled(True)
        self.begin_button.setText("Begin Experiment")
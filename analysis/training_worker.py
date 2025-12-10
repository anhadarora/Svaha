import time
import random
from PySide6.QtCore import QObject, Signal, QThread


class Communicate(QObject):
    """Holds signals for the worker thread to communicate with the main UI."""
    log_message = Signal(str)
    epoch_completed = Signal(dict)
    training_finished = Signal(dict) # Changed to carry a results dictionary


class TrainingWorker(QThread):
    """
    A QThread worker for running the training process in the background.
    """
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.comm = Communicate()
        self.all_epoch_data = []

    def run(self):
        """The main entry point for the training thread."""
        final_results = {}
        try:
            self.comm.log_message.emit("Training worker started.")
            self.comm.log_message.emit(f"Configuration loaded for experiment: {self.config.get('experiment_name', 'N/A')}")

            max_epochs = self.config.get("training", {}).get("max_epochs", 10)
            self.comm.log_message.emit(f"Simulating training for {max_epochs} epochs...")

            for epoch in range(1, max_epochs + 1):
                time.sleep(1) # Shortened for faster testing
                metrics = {
                    "epoch": epoch,
                    "train_loss": 1.0 / epoch + random.uniform(-0.05, 0.05),
                    "val_loss": 1.2 / epoch + random.uniform(-0.05, 0.05),
                    "prediction_correctness": 0.6 + (epoch * 0.03) + random.uniform(-0.02, 0.02),
                    "frame_shift_error": 0.5 / epoch + random.uniform(-0.05, 0.05),
                    "correction_healing": 0.1 * epoch + random.uniform(-0.05, 0.05),
                    "error_component_A": 1.0 - (epoch * 0.05) + random.uniform(-0.1, 0.1),
                    "error_component_B": 0.5 + (epoch * 0.02) + random.uniform(-0.1, 0.1),
                }
                self.all_epoch_data.append(metrics)
                self.comm.epoch_completed.emit(metrics)
                self.comm.log_message.emit(f"Epoch {epoch}/{max_epochs} completed. Val Loss: {metrics['val_loss']:.4f}")

            self.comm.log_message.emit("Training simulation finished successfully.")
            
            # --- Prepare Final Summary ---
            final_results = self.prepare_summary()

        except Exception as e:
            self.comm.log_message.emit(f"An error occurred in the training worker: {e}")
        finally:
            # Signal that the entire process is done, emitting the final results
            self.comm.training_finished.emit(final_results)

    def prepare_summary(self):
        """Creates a summary dictionary from the completed training run."""
        if not self.all_epoch_data:
            return {}

        best_epoch = min(self.all_epoch_data, key=lambda x: x['val_loss'])
        last_epoch = self.all_epoch_data[-1]

        summary = {
            "experiment_summary": {
                "Experiment Name": self.config.get('experiment_name', 'N/A'),
                "Completed On": time.strftime("%Y-%m-%d %H:%M:%S"),
                "Total Epochs": len(self.all_epoch_data),
                "Best Validation Loss": f"{best_epoch['val_loss']:.4f} (Epoch {best_epoch['epoch']})",
            },
            "parameter_configuration": self.config,
            "kpis": {
                "Final Accuracy": f"{last_epoch['prediction_correctness'] * 100:.2f}%",
                "Sharpe Ratio": f"{random.uniform(0.5, 2.5):.2f}", # Dummy
                "Max Drawdown": f"{random.uniform(5, 25):.2f}%", # Dummy
                "Alpha": f"{random.uniform(-0.05, 0.05):.3f}", # Dummy
            },
            "trade_statistics": {
                "Total Trades": random.randint(50, 200),
                "Win Rate": f"{random.uniform(40, 60):.2f}%",
                "Profit Factor": f"{random.uniform(1.1, 2.5):.2f}",
                "Average Win": f"{random.uniform(0.5, 2.0):.2f}%",
                "Average Loss": f"{random.uniform(-0.4, -1.5):.2f}%",
            },
            "plot_data": {
                "all_epochs": self.all_epoch_data,
                # In a real scenario, you might pass file paths to saved plot images
                # or the raw data required to regenerate them.
            }
        }
        return summary
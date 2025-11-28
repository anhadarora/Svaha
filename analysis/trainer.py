import time

from PySide6.QtCore import QObject, Signal


class Trainer(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()
    plot_data = Signal(dict)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def start_training(self):
        try:
            self.log.emit("Starting training...")
            self.log.emit(f"Configuration: {self.config}")

            # Placeholder for data loading and preprocessing
            self.log.emit("Loading and preprocessing data...")
            for i in range(10):
                time.sleep(0.1)
                self.progress.emit((i + 1) * 5)

            # Placeholder for model building
            self.log.emit("Building model...")
            time.sleep(1)

            # Placeholder for training loop
            self.log.emit("Starting training loop...")
            for epoch in range(self.config["epochs"]):
                self.log.emit(f"Epoch {epoch + 1}/{self.config['epochs']}")
                # Simulate training for one epoch
                for i in range(10):
                    time.sleep(0.1)
                    self.progress.emit(
                        50
                        + int((epoch / self.config["epochs"]) * 50)
                        + int((i / 10.0) * (50 / self.config["epochs"]))
                    )

                # Simulate loss values
                train_loss = 1 / (epoch + 1)
                val_loss = 1.2 / (epoch + 1)
                self.plot_data.emit(
                    {"train_loss": train_loss, "val_loss": val_loss})

            self.log.emit("Training finished.")
            self.progress.emit(100)
            self.finished.emit()

        except Exception as e:
            self.log.emit(f"An error occurred: {e}")
            self.finished.emit()

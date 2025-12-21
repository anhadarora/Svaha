
import os
import json
import pandas as pd
from PySide6.QtCore import QObject, Signal, QRunnable

class DiskSpaceCalculatorSignals(QObject):
    """Defines the signals available from a running worker thread."""
    finished = Signal(dict)

class DiskSpaceCalculator(QRunnable):
    """
    Worker thread for calculating the estimated disk space.
    Inherits from QRunnable to run on a thread from the global thread pool.
    """
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.signals = DiskSpaceCalculatorSignals()

    def run(self):
        """The main worker logic."""
        try:
            # 1. Get size of a single sample
            h = self.config.get("style_settings", {}).get("target_height", 64)
            w = self.config.get("style_settings", {}).get("target_width", 128)
            c = 1 if 'Grayscale' in self.config.get('channel_depth', '') else 3
            bytes_per_sample = h * w * c

            # 2. Get number of samples
            num_samples = self._calculate_number_of_samples()

            # 3. Calculate total size
            total_bytes = num_samples * bytes_per_sample
            
            result = {
                "status": "done",
                "total_bytes": total_bytes,
                "num_files": num_samples,
            }
        except Exception as e:
            result = {"status": "error", "message": str(e)}
            
        self.signals.finished.emit(result)

    def _calculate_number_of_samples(self):
        """
        Performs a dry run of the data loading and windowing process
        to determine the total number of samples that will be generated.
        """
        # --- Load Data ---
        metadata_path = os.path.abspath("./generated_data/metadata.json")
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        instrument_files = [
            os.path.join(os.path.dirname(metadata_path), item.get('parquet_filename', ''))
            for item in metadata 
            if item['symbol'] in self.config.get('instruments', []) 
            and item.get('parquet_filename') 
            and os.path.exists(os.path.join(os.path.dirname(metadata_path), item.get('parquet_filename', '')))
        ]
        if not instrument_files:
            return 0

        df = pd.concat([pd.read_parquet(f) for f in instrument_files], ignore_index=True)
        df['date'] = pd.to_datetime(df['date'])
        
        # --- Filter by Date ---
        start_date = pd.to_datetime(self.config.get('master_start_date'))
        end_date = pd.to_datetime(self.config.get('master_end_date'))
        if start_date and end_date:
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        df = df.sort_values('date').reset_index(drop=True)

        # --- Resample ---
        resampling_factor = self.config.get('resampling_factor', 1)
        if resampling_factor > 1:
            rule = str(resampling_factor) + 'T'
            df = df.set_index('date').resample(rule).agg({
                'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
            }).dropna().reset_index()

        # --- Count Windows ---
        if df.empty:
            return 0
            
        window_size = self.config.get("input_window_size", 5)
        horizon = self.config.get("prediction_horizon", 1)
        
        # The number of samples is the total length minus the window size needed for the last label.
        # This is a simplification of the loop in the TrainingWorker.
        num_samples = len(df) - window_size - horizon
        
        return max(0, num_samples)

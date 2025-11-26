import json
import os
import time
import logging
from datetime import datetime, timedelta
from threading import Thread

import pandas as pd
from kiteconnect import KiteConnect


class DownloadWorker(Thread):
    """
    A background thread to handle the data download process without freezing the UI.
    """

    def __init__(self, params, screen, kite_session: KiteConnect):
        super().__init__(daemon=True)
        self.params = params
        self.screen = screen
        # Use the authenticated KiteConnect session passed from the main app
        self.kite = kite_session
        self.instrument_map = {}
        self.logger = self.setup_logger()

    def run(self):
        """The main entry point for the thread."""
        try:
            self.log_and_add_to_screen("Worker started.")
            self.prepare_instruments()

            if self.params.get('resume_mode'):
                self.run_resume_mode()
            else:
                self.run_normal_mode()

        except Exception as e:
            self.log_and_add_to_screen(f"FATAL ERROR: {e}", level='error')
        finally:
            self.log_and_add_to_screen("Worker finished.")
            self.screen.comm.finish_signal.emit()

    def setup_logger(self):
        """Sets up a file-based logger for the download session."""
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = os.path.join(
            log_dir, f"download_session_{timestamp}.log")

        logger = logging.getLogger(f"DownloadWorker_{timestamp}")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_filename)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def log_and_add_to_screen(self, message, level='info'):
        """Logs message to file and adds it to the UI screen."""
        getattr(self.logger, level)(message)
        self.screen.comm.log_signal.emit(message)

    def prepare_instruments(self):
        """Fetches instruments and creates a Symbol -> Token map."""
        self.log_and_add_to_screen("Fetching instrument list...")
        try:
            # Basic caching mechanism
            instruments_file = 'assets/instruments.csv'
            if os.path.exists(instruments_file):
                instruments = pd.read_csv(instruments_file)
                self.log_and_add_to_screen("Loaded instruments from cache.")
            else:
                instruments_data = self.kite.instruments("NSE")
                instruments = pd.DataFrame(instruments_data)
                instruments.to_csv(instruments_file, index=False)
                self.log_and_add_to_screen("Fetched and cached instruments.")

            # Filter for Equity and create the map
            eq_df = instruments[instruments['instrument_type'] == 'EQ']
            self.instrument_map = pd.Series(
                eq_df.instrument_token.values, index=eq_df.tradingsymbol).to_dict()
            self.log_and_add_to_screen("Instrument map created.")

        except Exception as e:
            raise Exception(f"Failed to prepare instruments: {e}")

    def run_normal_mode(self):
        """Handles a standard download task from the UI queue."""
        symbols = self.params['symbols']
        manifest = {
            'pending': symbols,
            'completed': [],
            'failed': []
        }
        self.process_symbols(manifest)

    def run_resume_mode(self):
        """Handles a download task based on a manifest file."""
        manifest_path = self.params['manifest_path']
        self.log_and_add_to_screen(
            f"Resuming from {os.path.basename(manifest_path)}")
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        if not manifest.get('pending'):
            self.log_and_add_to_screen(
                "No pending symbols in manifest. Nothing to do.")
            return

        self.process_symbols(manifest)

    def process_symbols(self, manifest):
        """Iterates through symbols, downloads data, and updates the manifest."""
        pending = manifest['pending'][:]  # Work on a copy
        total_symbols = len(pending)
        output_dir = self.params['output_dir']
        manifest_path = os.path.join(output_dir, 'session_manifest.json')

        for i, symbol in enumerate(pending):
            self.screen.comm.progress_signal.emit(int((i / total_symbols) * 100))
            token = self.instrument_map.get(symbol)

            if not token:
                self.log_and_add_to_screen(
                    f"SKIP: No token found for {symbol}", level='warning')
                manifest['pending'].remove(symbol)
                manifest['failed'].append(symbol)
                continue

            try:
                self.log_and_add_to_screen(
                    f"FETCH: {symbol} ({i+1}/{total_symbols})")
                df = self.fetch_paginated_data(token)

                if df.empty:
                    self.log_and_add_to_screen(
                        f"WARN: No data returned for {symbol}", level='warning')
                    manifest['pending'].remove(symbol)
                    manifest['failed'].append(symbol)
                else:
                    self.save_data(df, symbol)
                    manifest['pending'].remove(symbol)
                    manifest['completed'].append(symbol)

            except Exception as e:
                self.log_and_add_to_screen(
                    f"ERROR fetching {symbol}: {e}", level='error')
                manifest['pending'].remove(symbol)
                manifest['failed'].append(symbol)
            finally:
                # Save manifest after each symbol
                with open(manifest_path, 'w') as f:
                    json.dump(manifest, f, indent=4)
                time.sleep(0.5)  # API rate limiting

        self.screen.comm.progress_signal.emit(100)

    def fetch_paginated_data(self, token):
        """Fetches data in 60-day chunks for minute-level intervals."""
        from_date = self.params['start_date']
        to_date = self.params['end_date']
        interval = self.params['interval']
        all_data = []

        while from_date <= to_date:
            chunk_to_date = min(from_date + timedelta(days=59), to_date)
            records = self.kite.historical_data(
                token, from_date, chunk_to_date, interval)
            all_data.extend(records)
            from_date = chunk_to_date + timedelta(days=1)

        return pd.DataFrame(all_data)

    def save_data(self, df, symbol):
        """Saves the DataFrame according to sharding and format options."""
        output_dir = self.params['output_dir']
        sharding = self.params['sharding']

        if sharding == 'None':
            if self.params['save_csv']:
                df.to_csv(os.path.join(
                    output_dir, f"{symbol}.csv"), index=False)
            if self.params['save_parquet']:
                df.to_parquet(os.path.join(
                    output_dir, f"{symbol}.parquet"), index=False)
        else:
            freq = 'M' if sharding == 'By Month' else 'Y'
            df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
            df.set_index('date', inplace=True)
            for name, group in df.groupby(pd.Grouper(freq=freq)):
                shard_name = f"{symbol}_{name.strftime('%Y-%m')}" if freq == 'M' else f"{symbol}_{name.strftime('%Y')}"
                if self.params['save_csv']:
                    group.to_csv(os.path.join(output_dir, f"{shard_name}.csv"))
                if self.params['save_parquet']:
                    group.to_parquet(os.path.join(
                        output_dir, f"{shard_name}.parquet"))

        self.log_and_add_to_screen(f"SAVE: {symbol} data saved.")

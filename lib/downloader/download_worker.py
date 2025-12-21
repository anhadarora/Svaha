import json
import logging
import os
import time
import uuid
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
        self.kite = kite_session
        self.instrument_map = {}
        self.logger = logging.getLogger(__name__)

    def _log(self, message, level="info"):
        """Helper to log to file/console and emit signal for UI."""
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
        self.screen.comm.log_signal.emit(message)

    def run(self):
        """The main entry point for the thread."""
        try:
            self._log("Download worker started.")
            self.prepare_instruments()

            if self.params.get("resume_mode"):
                self.run_resume_mode()
            else:
                self.run_normal_mode()

        except Exception as e:
            self._log(f"FATAL ERROR: {e}", level="error")
        finally:
            self._log("Download worker finished.")
            self.screen.comm.finish_signal.emit()

    def prepare_instruments(self):
        """Fetches instruments and creates a Symbol -> Token map."""
        self._log("Fetching instrument list...")
        try:
            instruments_file = "source_data/instruments.csv"
            if os.path.exists(instruments_file):
                instruments = pd.read_csv(instruments_file)
                self._log("Loaded instruments from cache.")
            else:
                instruments_data = self.kite.instruments("NSE")
                instruments = pd.DataFrame(instruments_data)
                instruments.to_csv(instruments_file, index=False)
                self._log("Fetched and cached instruments.")

            eq_df = instruments[instruments["instrument_type"] == "EQ"]
            self.instrument_map = pd.Series(
                eq_df.instrument_token.values, index=eq_df.tradingsymbol
            ).to_dict()
            self._log("Instrument map created.")

        except Exception as e:
            raise Exception(f"Failed to prepare instruments: {e}")

    def run_normal_mode(self):
        """Handles a standard download task from the UI queue."""
        symbols = self.params["symbols"]
        manifest = {"pending": symbols, "completed": [], "failed": []}
        self.process_symbols(manifest)

    def run_resume_mode(self):
        """Handles a download task based on a manifest file."""
        manifest_path = self.params["manifest_path"]
        self._log(f"Resuming from {os.path.basename(manifest_path)}")
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        if not manifest.get("pending"):
            self._log("No pending symbols in manifest. Nothing to do.")
            return

        self.process_symbols(manifest)

    def process_symbols(self, manifest):
        """Iterates through symbols, downloads data, and updates the manifest."""
        pending = manifest["pending"][:]
        total_symbols = len(pending)
        output_dir = self.params["output_dir"]
        manifest_path = os.path.join(output_dir, "session_manifest.json")

        for i, symbol in enumerate(pending):
            self.screen.comm.progress_signal.emit(int((i / total_symbols) * 100))
            token = self.instrument_map.get(symbol)

            if not token:
                self._log(f"SKIP: No token found for {symbol}", level="warning")
                manifest["pending"].remove(symbol)
                manifest["failed"].append(symbol)
                continue

            try:
                self._log(f"FETCH: {symbol} ({i+1}/{total_symbols})")
                df = self.fetch_paginated_data(token)

                if df.empty:
                    self._log(f"WARN: No data returned for {symbol}", level="warning")
                    manifest["pending"].remove(symbol)
                    manifest["failed"].append(symbol)
                else:
                    self.save_data(df, symbol)
                    manifest["pending"].remove(symbol)
                    manifest["completed"].append(symbol)

            except Exception as e:
                self._log(f"ERROR fetching {symbol}: {e}", level="error")
                manifest["pending"].remove(symbol)
                manifest["failed"].append(symbol)
            finally:
                with open(manifest_path, "w") as f:
                    json.dump(manifest, f, indent=4)
                time.sleep(0.5)

        self.screen.comm.progress_signal.emit(100)

    def fetch_paginated_data(self, token):
        from_date = self.params["start_date"]
        to_date = self.params["end_date"]
        interval = self.params["interval"]
        self._log(f"Fetching data for token {token} from {from_date} to {to_date} with interval {interval}")
        all_data = []

        while from_date <= to_date:
            chunk_to_date = min(from_date + timedelta(days=59), to_date)
            self._log(f"Fetching chunk from {from_date} to {chunk_to_date}")
            records = self.kite.historical_data(token, from_date, chunk_to_date, interval)
            self._log(f"Got {len(records)} records in chunk.")
            all_data.extend(records)
            from_date = chunk_to_date + timedelta(days=1)

        return pd.DataFrame(all_data)

    def save_data(self, df, symbol):
        output_dir = self.params["output_dir"]
        sharding = self.params["sharding"]
        start_date = self.params["start_date"]
        end_date = self.params["end_date"]
        interval = self.params["interval"]

        metadata_path = os.path.join(output_dir, "metadata.json")
        metadata = []
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

        sharding_map = {"By Day": "D", "By Week": "W", "By Month": "M", "By Quarter": "Q", "By Year": "Y"}
        freq = sharding_map.get(sharding)

        if freq:
            df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
            df.set_index("date", inplace=True)
            for name, group in df.groupby(pd.Grouper(freq=freq)):
                file_id = str(uuid.uuid4())
                shard_name_suffix = name.strftime("%Y-%m-%d")
                base_filename = f"{symbol}_{interval}_{shard_name_suffix}"
                
                file_info = {"file_id": file_id, "base_filename": base_filename, "symbol": symbol, "start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d"), "interval": interval, "sharding": sharding, "shard_name": shard_name_suffix}

                if self.params["save_csv"]:
                    filename = f"{file_id}.csv"
                    group.to_csv(os.path.join(output_dir, filename))
                    file_info["csv_filename"] = filename
                
                if self.params["save_parquet"]:
                    filename = f"{file_id}.parquet"
                    group.to_parquet(os.path.join(output_dir, filename))
                    file_info["parquet_filename"] = filename
                
                metadata.append(file_info)
        else:
            file_id = str(uuid.uuid4())
            base_filename = f"{symbol}_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}_{interval}"
            file_info = {"file_id": file_id, "base_filename": base_filename, "symbol": symbol, "start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d"), "interval": interval, "sharding": "None"}

            if self.params["save_csv"]:
                filename = f"{file_id}.csv"
                df.to_csv(os.path.join(output_dir, filename), index=False)
                file_info["csv_filename"] = filename

            if self.params["save_parquet"]:
                filename = f"{file_id}.parquet"
                df.to_parquet(os.path.join(output_dir, filename), index=False)
                file_info["parquet_filename"] = filename
            
            metadata.append(file_info)

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)

        self._log(f"SAVE: {symbol} data saved.")

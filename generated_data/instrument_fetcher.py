import os
from io import StringIO

import pandas as pd
import requests


def fetch_and_save_intraday_equities():
    """
    Downloads the full list of instruments from Zerodha, filters for NSE equities,
    and saves them to a CSV file.

    Returns:
        str: The path to the saved CSV file, or None if an error occurs.
    """
    try:
        print("Fetching Zerodha instrument list...")
        # Zerodha's public URL for all instruments
        url = "https://api.kite.trade/instruments"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Use StringIO to treat the string response as a file for pandas
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)

        # Filter for equities on the NSE exchange
        # All 'EQ' instruments are generally available for intraday (MIS) trading
        # unless under specific surveillance, which is a good default.
        nse_equities = df[(df["exchange"] == "NSE") & (df["instrument_type"] == "EQ")]

        # Create a new DataFrame with just the trading symbols
        symbols_df = nse_equities[["tradingsymbol"]].rename(
            columns={"tradingsymbol": "symbol"}
        )

        output_path = os.path.join(os.path.dirname(__file__), "default_symbols.csv")
        symbols_df.to_csv(output_path, index=False)
        print(f"Saved {len(symbols_df)} NSE equity symbols to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error fetching instrument list: {e}")
        return None

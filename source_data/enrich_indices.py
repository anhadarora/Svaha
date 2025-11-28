import io
import time

import pandas as pd
import requests

# 1. Configuration: The "Index Map"
# These are the direct CSV links to the live constituents on NSE's index website.
# I have mapped the major ones from your screenshot.
INDEX_URLS = {
    # Broad Market
    "NIFTY 50": "https://www.niftyindices.com/IndexConstituent/ind_nifty50list.csv",
    "NIFTY NEXT 50": "https://www.niftyindices.com/IndexConstituent/ind_niftynext50list.csv",
    "NIFTY 100": "https://www.niftyindices.com/IndexConstituent/ind_nifty100list.csv",
    "NIFTY 200": "https://www.niftyindices.com/IndexConstituent/ind_nifty200list.csv",
    "NIFTY 500": "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv",
    "NIFTY MIDCAP 150": "https://www.niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
    "NIFTY SMALLCAP 250": "https://www.niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv",
    # Sectoral Indices
    "NIFTY BANK": "https://www.niftyindices.com/IndexConstituent/ind_niftybanklist.csv",
    "NIFTY AUTO": "https://www.niftyindices.com/IndexConstituent/ind_niftyautolist.csv",
    "NIFTY IT": "https://www.niftyindices.com/IndexConstituent/ind_niftyitlist.csv",
    "NIFTY FMCG": "https://www.niftyindices.com/IndexConstituent/ind_niftyfmcglist.csv",
    "NIFTY METAL": "https://www.niftyindices.com/IndexConstituent/ind_niftymetallist.csv",
    "NIFTY PHARMA": "https://www.niftyindices.com/IndexConstituent/ind_niftypharmalist.csv",
    "NIFTY REALTY": "https://www.niftyindices.com/IndexConstituent/ind_niftyrealtylist.csv",
    "NIFTY PSU BANK": "https://www.niftyindices.com/IndexConstituent/ind_niftypsubanklist.csv",
    "NIFTY ENERGY": "https://www.niftyindices.com/IndexConstituent/ind_niftyenergylist.csv",
}


def fetch_constituents(index_name, url):
    """Fetches the CSV for a specific index and returns a list of symbols."""
    print(f"Fetching {index_name}...")
    # The niftyindices server expects a User-Agent and a Referer to allow the download
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.niftyindices.com/reports/historical-data",
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # NSE CSVs often have different column names, but 'Symbol' is consistent
            df = pd.read_csv(io.StringIO(response.content.decode("utf-8")))
            return df["Symbol"].unique().tolist()
        else:
            print(f"Failed to fetch {index_name} (Status: {response.status_code})")
            return []
    except Exception as e:
        print(f"Error fetching {index_name}: {e}")
        return []


def main():
    # 2. Load your existing Master Catalog
    # Replace 'master_catalog.csv' with your actual filename
    try:
        main_df = pd.read_csv("source_data/master_catalog.csv")
    except FileNotFoundError:
        print("Could not find master_catalog.csv. Please ensure the file exists.")
        return

    # Initialize the Indices column if it doesn't exist
    main_df["Indices"] = ""

    # 3. Iterate through URLs and tag stocks
    for index_name, url in INDEX_URLS.items():
        symbols = fetch_constituents(index_name, url)

        # For every symbol found in this index, append the index name
        for symbol in symbols:
            # Check if symbol exists in our master list
            mask = main_df["Symbol"] == symbol
            if mask.any():
                # If current val is empty, just add index. If not, append ", Index"
                main_df.loc[mask, "Indices"] = main_df.loc[mask, "Indices"].apply(
                    lambda x: f"{x}, {index_name}" if x else index_name
                )

        # Be polite to the server
        time.sleep(1)

    # 4. Save the enriched catalog
    output_file = "source_data/master_catalog_enriched.csv"
    main_df.to_csv(output_file, index=False)
    print(f"\nSuccess! Saved enriched data to {output_file}")
    print("Sample Row:")
    print(main_df[main_df["Symbol"] == "RELIANCE"][["Symbol", "Indices"]].to_string())


if __name__ == "__main__":
    main()

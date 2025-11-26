import pandas as pd
import os

CWD = os.getcwd()


def generate_master_catalog():
    # 1. Load your Zerodha Dump (The file you uploaded)
    # We only need 'tradingsymbol' and 'instrument_token' from here
    z_path = os.path.join(CWD, 'assets', 'default_symbols.csv')
    # The provided CSV has no header, so we name the column 'tradingsymbol'
    z_df = pd.read_csv(z_path, header=None, names=['tradingsymbol'])

    # 2. Load the NSE Nifty 500 List (You need to download this from NSE website)
    # If you don't have it yet, I will simulate a basic version structure here
    # Real NSE file usually has columns: 'Symbol', 'Company Name', 'Industry'
    nse_path = os.path.join(CWD, 'assets', 'ind_nifty500list.csv')
    # Use the actual NSE Nifty 500 list
    nse_df = pd.read_csv(nse_path)

    # 3. Merge them on the Symbol
    # Zerodha uses 'tradingsymbol', NSE uses 'Symbol'. They usually match 1:1.
    merged_df = pd.merge(
        nse_df,
        z_df,
        left_on='Symbol',
        right_on='tradingsymbol',
        how='inner'  # Only keep stocks that exist in both
    )

    # 4. Clean up columns
    # The 'instrument_token' is not available in the source files.
    # We will create a catalog with the available information.
    final_df = merged_df[['Symbol', 'Industry', 'ISIN Code']]

    # 5. Save to your assets folder
    final_df.to_csv('assets/master_catalog.csv', index=False)
    print("Master Catalog Generated with Industries and ISIN codes!")


if __name__ == "__main__":
    generate_master_catalog()

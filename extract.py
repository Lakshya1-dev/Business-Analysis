#!/usr/bin/env python3
"""
extract.py
~~~~~~~~~~
Data ingestion script for Titan Company (TITAN.NS) and Gold Futures (GC=F) historical data.

This script uses yfinance to download daily historical closing prices for the specified
tickers and date range. It then isolates the 'Close' column, resets the index, renames
columns appropriately, and saves the data to CSV files.

Steps:
1. Download data for TITAN.NS and GC=F from '2014-01-01' to '2024-01-01'.
2. Extract the 'Close' price for each.
3. Reset the index to turn the date index into a column.
4. Rename columns to: Trade_Date, Titan_Close (for TITAN.NS) and Trade_Date, Gold_Close (for GC=F).
5. Save each to CSV: titan_raw.csv and gold_raw.csv.

Note: The script assumes that yfinance is installed (see requirements.txt).
"""

import yfinance as yf
import pandas as pd

def main():
    # Define the tickers and date range
    titan_ticker = "TITAN.NS"
    gold_ticker = "GC=F"
    start_date = "2014-01-01"
    end_date = "2024-01-01"

    # Download data for Titan
    print(f"Downloading data for {titan_ticker}...")
    titan_data = yf.download(titan_ticker, start=start_date, end=end_date)
    # Download data for Gold
    print(f"Downloading data for {gold_ticker}...")
    gold_data = yf.download(gold_ticker, start=start_date, end=end_date)

    # Check if data was downloaded successfully
    if titan_data.empty:
        raise ValueError(f"No data downloaded for {titan_ticker}. Check ticker symbol or date range.")
    if gold_data.empty:
        raise ValueError(f"No data downloaded for {gold_ticker}. Check ticker symbol or date range.")

    # Isolate the 'Close' column and reset index for Titan
    titan_close = titan_data[['Close']].copy()
    titan_close.reset_index(inplace=True)
    titan_close.rename(columns={'Date': 'Trade_Date', 'Close': 'Titan_Close'}, inplace=True)

    # Isolate the 'Close' column and reset index for Gold
    gold_close = gold_data[['Close']].copy()
    gold_close.reset_index(inplace=True)
    gold_close.rename(columns={'Date': 'Trade_Date', 'Close': 'Gold_Close'}, inplace=True)

    # Save to CSV
    titan_close.to_csv('titan_raw.csv', index=False)
    gold_close.to_csv('gold_raw.csv', index=False)

    print("Data extraction complete. Files saved: titan_raw.csv, gold_raw.csv")

if __name__ == "__main__":
    main()
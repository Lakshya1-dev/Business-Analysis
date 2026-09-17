#!/usr/bin/env python3
"""
transform.py
~~~~~~~~~~~~
SQL feature engineering script for Titan Company and Gold Futures data.

This script creates a local SQLite database, loads the raw CSV data, and executes a
comprehensive SQL query to engineer features including:
- Forward-filling missing Gold prices using window functions (to handle market holiday differences)
- 30-day moving average of Titan's closing price
- Year-over-year growth of Titan's closing price

The engineered features are saved to 'sql_engineered_features.csv' for further analysis.

Steps:
1. Create SQLite database 'market_data.db'.
2. Load 'titan_raw.csv' and 'gold_raw.csv' into SQL tables.
3. Execute a single SQL query that:
   a) Left joins Titan's trading calendar (base) with Gold data on Trade_Date.
   b) Forward-fills missing Gold prices using COALESCE and a windowed MAX over preceding rows.
   c) Calculates 30-day moving average using AVG() OVER (ROWS BETWEEN 29 PRECEDING AND CURRENT ROW).
   d) Calculates Year-over-Year growth using LAG(252) to compare with price ~1 year ago.
4. Save query results to 'sql_engineered_features.csv'.

Dependencies: pandas, sqlite3 (built-in)
"""

import sqlite3
import pandas as pd

def main():
    # Step 1: Create/connect to SQLite database
    print("Creating database connection...")
    conn = sqlite3.connect('market_data.db')

    # Step 2: Load raw CSV data into SQL tables
    print("Loading raw CSV data into database tables...")
    titan_df = pd.read_csv('titan_raw.csv')
    gold_df = pd.read_csv('gold_raw.csv')

    # Use pandas to_sql for simplicity and efficiency
    titan_df.to_sql('titan_raw', conn, if_exists='replace', index=False)
    gold_df.to_sql('gold_raw', conn, if_exists='replace', index=False)

    # Step 3: Define and execute the comprehensive SQL query
    print("Executing SQL feature engineering query...")
    sql_query = """
    SELECT
        t.Trade_Date,
        t.Titan_Close,
        -- Forward-fill missing Gold prices: use last known Gold_Close if current is NULL
        COALESCE(
            g.Gold_Close,
            MAX(CASE WHEN g.Gold_Close IS NOT NULL THEN g.Gold_Close END)
                OVER (ORDER BY t.Trade_Date ROWS UNBOUNDED PRECEDING)
        ) AS Gold_Close,
        -- 30-day moving average of Titan's closing price
        AVG(t.Titan_Close) OVER (
            ORDER BY t.Trade_Date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS Titan_30d_MA,
        -- Year-over-Year growth: (current price / price 252 days ago) - 1
        (t.Titan_Close / LAG(t.Titan_Close, 252) OVER (ORDER BY t.Trade_Date) - 1) * 100 AS Titan_YoY_Growth
    FROM titan_raw t
    LEFT JOIN gold_raw g ON t.Trade_Date = g.Trade_Date
    ORDER BY t.Trade_Date;
    """

    # Execute query and load results into a DataFrame
    engineered_df = pd.read_sql_query(sql_query, conn)

    # Step 4: Save engineered features to CSV
    output_path = 'sql_engineered_features.csv'
    engineered_df.to_csv(output_path, index=False)
    print(f"Feature engineering complete. Saved to '{output_path}'")
    print(f"Shape of engineered data: {engineered_df.shape}")

    # Close database connection
    conn.close()

if __name__ == "__main__":
    main()
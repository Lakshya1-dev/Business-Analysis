#!/usr/bin/env python3
"""
analyze.py
~~~~~~~~~~
Statistical modeling and visualization script for Titan-Gold analysis.

This script loads the engineered features, computes univariate statistics,
calculates daily returns, runs an OLS regression, and generates a dual-axis
timeseries plot comparing Titan and Gold prices.

Steps:
1. Load 'sql_engineered_features.csv' into a pandas DataFrame.
2. Drop rows with NaN (resulting from lag and moving average calculations).
3. Calculate and print:
   - 10-year average Titan price (mean of Titan_Close)
   - annualized volatility (daily std dev * sqrt(252))
4. Compute daily percentage returns for Titan and Gold.
5. Run OLS regression: Titan_Return ~ Gold_Return + Titan_30d_MA (with constant).
6. Print the regression summary.
7. Generate dual-axis line chart (Titan vs Gold prices) and save as 'timeseries_plot.png'.

Dependencies: pandas, numpy, statsmodels, matplotlib, seaborn
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    # Step 1: Load engineered features
    print("Loading engineered features...")
    df = pd.read_csv('sql_engineered_features.csv')

    # Convert Trade_Date to datetime for plotting and sorting
    df['Trade_Date'] = pd.to_datetime(df['Trade_Date'])
    df.sort_values('Trade_Date', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Step 2: Drop rows with NaN (due to lag/moving average at start)
    original_len = len(df)
    df.dropna(inplace=True)
    print(f"Dropped {original_len - len(df)} rows with NaN values. Remaining: {len(df)}")

    # Step 3: Univariate statistics
    titan_avg_price = df['Titan_Close'].mean()
    titan_daily_vol = df['Titan_Close'].std()
    titan_annualized_vol = titan_daily_vol * np.sqrt(252)

    print("\n=== Univariate Statistics (Titan Company) ===")
    print(f"10-Year Average Closing Price: ₹{titan_avg_price:.2f}")
    print(f"Annualized Volatility: {titan_annualized_vol:.2%}")

    # Step 4: Calculate daily percentage returns
    df['Titan_Return'] = df['Titan_Close'].pct_change()
    df['Gold_Return'] = df['Gold_Close'].pct_change()
    # Drop the first row which will have NaN return due to pct_change
    df_returns = df.dropna(subset=['Titan_Return', 'Gold_Return']).copy()

    # Step 5: OLS regression
    print("\n=== OLS Regression: Titan_Return ~ Gold_Return + Titan_30d_MA ===")
    # Prepare predictors and add constant
    X = df_returns[['Gold_Return', 'Titan_30d_MA']]
    X = sm.add_constant(X)  # adds intercept term
    y = df_returns['Titan_Return']

    model = sm.OLS(y, X).fit()
    print(model.summary())

    # Step 6: Dual-axis line chart
    print("\nGenerating dual-axis timeseries plot...")
    plt.style.use('seaborn-v0_8')
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Plot Titan price on left axis
    color_titan = '#2E86AB'
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Titan Company Close Price (₹)', color=color_titan, fontsize=12)
    ax1.plot(df['Trade_Date'], df['Titan_Close'], color=color_titan, linewidth=2.5, label='Titan Close')
    ax1.tick_params(axis='y', labelcolor=color_titan)
    ax1.grid(True, alpha=0.3)

    # Create second axis for Gold price
    ax2 = ax1.twinx()
    color_gold = '#F18F01'
    ax2.set_ylabel('Gold Futures Close Price ($)', color=color_gold, fontsize=12)
    ax2.plot(df['Trade_Date'], df['Gold_Close'], color=color_gold, linewidth=2.5, linestyle='--', label='Gold Close')
    ax2.tick_params(axis='y', labelcolor=color_gold)

    # Title and layout
    plt.title('Titan Company (TITAN.NS) vs Gold Futures (GC=F): 10-Year Price Comparison\n'
              'Left Axis: Titan Price (₹) | Right Axis: Gold Price ($)',
              fontsize=14, pad=20, fontweight='bold')

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)

    # Adjust layout and save
    fig.tight_layout()
    plot_path = 'timeseries_plot.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved as '{plot_path}'")

    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
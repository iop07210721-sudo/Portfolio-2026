import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Download copper data (using HG=F futures as proxy for copper)
def get_copper_data(start_date, end_date):
    copper = yf.download('HG=F', start=start_date, end=end_date)
    return copper['Close']

# Simple Moving Average Crossover Strategy
def sma_crossover_strategy(data, short_window=50, long_window=200):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data
    signals['short_mavg'] = data.rolling(window=short_window, min_periods=1).mean()
    signals['long_mavg'] = data.rolling(window=long_window, min_periods=1).mean()
    signals['signal'] = 0.0
    mask = signals.index >= signals.index[short_window]
    signals.loc[mask, 'signal'] = np.where(signals.loc[mask, 'short_mavg'] > signals.loc[mask, 'long_mavg'], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals

# Backtest the strategy
def backtest_strategy(signals, initial_capital=10000):
    positions = pd.DataFrame(index=signals.index).fillna(0.0)
    positions['HG=F'] = 100 * signals['signal']  # Buy 100 contracts when signal is 1
    portfolio = positions.multiply(signals['price'], axis=0)
    pos_diff = positions.diff()
    portfolio['holdings'] = (positions.multiply(signals['price'], axis=0)).sum(axis=1)
    portfolio['cash'] = initial_capital - (pos_diff.multiply(signals['price'], axis=0)).sum(axis=1).cumsum()
    portfolio['total'] = portfolio['cash'] + portfolio['holdings']
    portfolio['returns'] = portfolio['total'].pct_change()
    return portfolio

# Main function
if __name__ == "__main__":
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*5)  # 5 years of data

    copper_data = get_copper_data(start_date, end_date)
    signals = sma_crossover_strategy(copper_data)
    portfolio = backtest_strategy(signals)

    # Plot results
    fig, ax = plt.subplots(2, 1, figsize=(12, 8))
    ax[0].plot(signals['price'], label='Copper Price')
    ax[0].plot(signals['short_mavg'], label='50-day SMA')
    ax[0].plot(signals['long_mavg'], label='200-day SMA')
    ax[0].set_title('Copper Price and Moving Averages')
    ax[0].legend()

    ax[1].plot(portfolio['total'], label='Portfolio Value')
    ax[1].set_title('Portfolio Value Over Time')
    ax[1].legend()

    plt.tight_layout()
    plt.savefig('copper_strategy_backtest.png')
    plt.show()

    print("Backtest completed. Check copper_strategy_backtest.png for results.")
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 設置中文字體（如果可用）
try:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.family'] = 'sans-serif'
    # 強制重新載入字體
    import matplotlib.font_manager as fm
    fm._rebuild()
except:
    pass

# 下載黃金數據
def get_gold_data(start_date='2024-01-01', end_date='2025-12-31'):
    gold = yf.Ticker("GC=F")
    data = gold.history(start=start_date, end=end_date)
    return data

# 計算 RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    data['RSI'] = rsi
    return data

# 計算移動平均線
def calculate_moving_averages(data, short_window=50, long_window=200):
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    return data

# 生成交易信號
def generate_signals(data):
    data['Signal'] = 0
    # 買入條件：短期 MA > 長期 MA 且 RSI < 70 (避免過買)
    buy_condition = (data['Short_MA'] > data['Long_MA']) & (data['RSI'] < 70)
    # 賣出條件：短期 MA < 長期 MA 或 RSI > 30 (避免過賣)
    sell_condition = (data['Short_MA'] < data['Long_MA']) | (data['RSI'] > 30)
    data.loc[buy_condition, 'Signal'] = 1
    data.loc[sell_condition, 'Signal'] = -1
    return data

# 模擬交易決策
def simulate_trading(data, initial_capital=10000):
    capital = float(initial_capital)
    position = 0.0  # 持有黃金盎司數
    data['Capital'] = float(initial_capital)
    data['Position'] = 0.0

    for i in range(len(data)):
        if data['Signal'].iloc[i] == 1 and position == 0:  # 買入
            position = capital / data['Close'].iloc[i]
            capital = 0.0
        elif data['Signal'].iloc[i] == -1 and position > 0:  # 賣出
            capital = position * data['Close'].iloc[i]
            position = 0.0
        data.loc[data.index[i], 'Capital'] = capital
        data.loc[data.index[i], 'Position'] = position

    final_value = capital + position * data['Close'].iloc[-1]
    return final_value, data

# 繪製圖表
def plot_strategy(data):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10))

    # 價格和 MA
    ax1.plot(data['Close'], label='Close Price')
    ax1.plot(data['Short_MA'], label='50-Day MA')
    ax1.plot(data['Long_MA'], label='200-Day MA')
    ax1.scatter(data[data['Signal'] == 1].index, data['Close'][data['Signal'] == 1], marker='^', color='g', label='Buy')
    ax1.scatter(data[data['Signal'] == -1].index, data['Close'][data['Signal'] == -1], marker='v', color='r', label='Sell')
    ax1.set_title('Gold Price and Trading Signals')
    ax1.legend()

    # RSI
    ax2.plot(data['RSI'], label='RSI')
    ax2.axhline(70, color='r', linestyle='--', label='Overbought')
    ax2.axhline(30, color='g', linestyle='--', label='Oversold')
    ax2.set_title('Relative Strength Index (RSI)')
    ax2.legend()

    # 資本變化
    ax3.plot(data['Capital'], label='Capital')
    ax3.set_title('Simulated Capital Change')
    ax3.legend()

    plt.tight_layout()
    plt.savefig('trading_strategy.png', dpi=300, bbox_inches='tight')
    plt.savefig('trading_strategy.svg', bbox_inches='tight')
    plt.show()
    print("圖表已保存為 trading_strategy.png 和 trading_strategy.svg")

# 主函數
if __name__ == "__main__":
    data = get_gold_data()
    data = calculate_rsi(data)
    data = calculate_moving_averages(data)
    data = generate_signals(data)
    final_value, data = simulate_trading(data)
    plot_strategy(data)
    print(f"初始資本: $10000")
    print(f"最終價值: ${final_value:.2f}")
    print("決策程式執行完成。圖表已顯示。")
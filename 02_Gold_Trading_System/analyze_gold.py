import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 設置中文字體（如果可用）
try:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

# 獲取 2024~2025 黃金價格數據
def get_gold_data_2024_2025():
    gold = yf.Ticker("GC=F")
    data = gold.history(start='2024-01-01', end='2025-12-31')
    return data

# 分析數據：顯示基本統計和圖表
def analyze_data(data):
    print("黃金價格數據統計 (2024-2025):")
    print(data['Close'].describe())
    print("\n最高價:", data['High'].max())
    print("最低價:", data['Low'].min())
    print("平均價:", data['Close'].mean())

    # 繪製價格走勢圖
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price')
    plt.title('Gold Price Trend (2024-2025)')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    data = get_gold_data_2024_2025()
    analyze_data(data)
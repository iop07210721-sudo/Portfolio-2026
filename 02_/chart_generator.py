import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

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

# 生成綜合圖表
def create_comprehensive_chart(data):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # 1. 價格走勢圖
    ax1.plot(data.index, data['Close'], label='Close Price', color='gold')
    ax1.set_title('Gold Price Trend (2024-2025)')
    ax1.set_ylabel('Price (USD)')
    ax1.legend()
    ax1.grid(True)

    # 2. 成交量圖
    ax2.bar(data.index, data['Volume'], color='blue', alpha=0.7)
    ax2.set_title('Volume')
    ax2.set_ylabel('Volume')
    ax2.grid(True)

    # 3. 價格分佈直方圖
    ax3.hist(data['Close'], bins=50, color='green', alpha=0.7)
    ax3.set_title('Price Distribution')
    ax3.set_xlabel('Price (USD)')
    ax3.set_ylabel('Frequency')
    ax3.grid(True)

    # 4. 月度平均價格
    monthly_data = data.resample('ME').mean()
    ax4.plot(monthly_data.index, monthly_data['Close'], marker='o', color='red')
    ax4.set_title('Monthly Average Price')
    ax4.set_ylabel('Average Price (USD)')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True)

    plt.tight_layout()
    plt.savefig('/workspaces/glod/gold_chart.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("圖表已保存為 gold_chart.png")

# 顯示統計摘要
def show_statistics(data):
    print("=== 黃金價格統計摘要 (2024-2025) ===")
    print(f"數據期間: {data.index.min().date()} 到 {data.index.max().date()}")
    print(f"總交易日: {len(data)}")
    print(f"平均收盤價: ${data['Close'].mean():.2f}")
    print(f"最高價: ${data['High'].max():.2f} (日期: {data['High'].idxmax().date()})")
    print(f"最低價: ${data['Low'].min():.2f} (日期: {data['Low'].idxmin().date()})")
    print(f"價格波動性 (標準差): ${data['Close'].std():.2f}")
    print(f"總成交量: {data['Volume'].sum():,.0f}")

if __name__ == "__main__":
    data = get_gold_data_2024_2025()
    show_statistics(data)
    create_comprehensive_chart(data)
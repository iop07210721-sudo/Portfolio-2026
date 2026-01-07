import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import talib as ta

# 設置中文字體（如果可用）
try:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

# 獲取黃金數據
def get_gold_data(start_date='2024-01-01', end_date='2025-12-31'):
    gold = yf.Ticker("GC=F")
    data = gold.history(start=start_date, end=end_date)
    return data

# 計算RSI
def calculate_rsi(data, period=14):
    data['RSI'] = ta.RSI(data['Close'], timeperiod=period)
    return data

# 計算EMA
def calculate_emas(data, fast_period=20, slow_period=50):
    data['Fast_EMA'] = ta.EMA(data['Close'], timeperiod=fast_period)
    data['Slow_EMA'] = ta.EMA(data['Close'], timeperiod=slow_period)
    return data

# 實現Pine Script策略邏輯
def apply_pine_strategy(data, rsi_overbought=70, rsi_target_min=45, rsi_target_max=55):
    # 趨勢條件：20 EMA > 50 EMA
    data['Trend_Condition'] = data['Fast_EMA'] > data['Slow_EMA']

    # RSI 從超買區回落至目標區間的條件
    data['RSI_Was_Overbought'] = False
    data['RSI_In_Target_Zone'] = (data['RSI'] >= rsi_target_min) & (data['RSI'] <= rsi_target_max)

    # 檢查RSI是否曾經在超買區
    for i in range(1, len(data)):
        # 檢查前幾根K線是否有RSI >= overbought
        prev_overbought = data['RSI'].iloc[:i].max() >= rsi_overbought
        data.loc[data.index[i], 'RSI_Was_Overbought'] = prev_overbought

    data['RSI_Pullback_Condition'] = data['RSI_Was_Overbought'] & data['RSI_In_Target_Zone']

    # RSI 勾頭向上的條件 (當前RSI > 前一個RSI)
    data['RSI_Bullish_Hook'] = data['RSI'] > data['RSI'].shift(1)

    # 價格回測 20 EMA 的條件
    # 價格在前一根K線低於或等於20 EMA，在當前K線高於20 EMA
    data['Price_Retest_Condition'] = (data['Low'].shift(1) <= data['Fast_EMA'].shift(1)) & (data['High'] >= data['Fast_EMA'])

    # 綜合買入條件
    data['Buy_Signal'] = (data['Trend_Condition'] &
                         data['Price_Retest_Condition'] &
                         data['RSI_Pullback_Condition'] &
                         data['RSI_Bullish_Hook'])

    return data

# 繪製策略圖表
def plot_strategy_chart(data):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [3, 1]})

    # 上方面板：價格和EMA
    ax1.plot(data.index, data['Close'], label='Close Price', color='black', alpha=0.7)
    ax1.plot(data.index, data['Fast_EMA'], label='20 EMA', color='blue', linewidth=2)
    ax1.plot(data.index, data['Slow_EMA'], label='50 EMA', color='red', linewidth=2)

    # 標記買入訊號
    buy_signals = data[data['Buy_Signal']]
    if not buy_signals.empty:
        ax1.scatter(buy_signals.index, buy_signals['High'], marker='^', color='green',
                   s=100, label='BUY Signal', zorder=5)

        # 添加訊號標籤
        for idx, row in buy_signals.iterrows():
            ax1.annotate('BUY', xy=(idx, row['High']),
                        xytext=(5, 5), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='green', alpha=0.8),
                        fontsize=10, color='white', fontweight='bold')

    ax1.set_title('Gold Price with EMA Crossover & RSI Pullback Strategy')
    ax1.set_ylabel('Price (USD)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 趨勢背景顏色
    trend_up = data['Trend_Condition']
    ax1.fill_between(data.index, data['Close'].min(), data['Close'].max(),
                    where=trend_up, color='green', alpha=0.1, label='Uptrend (20>50 EMA)')
    ax1.fill_between(data.index, data['Close'].min(), data['Close'].max(),
                    where=~trend_up, color='red', alpha=0.1, label='Downtrend (20<50 EMA)')

    # 下方面板：RSI
    ax2.plot(data.index, data['RSI'], label='RSI(14)', color='purple', linewidth=2)

    # RSI參考線
    ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
    ax2.axhline(y=50, color='orange', linestyle='--', alpha=0.7, label='Target Zone')
    ax2.axhline(y=45, color='orange', linestyle='--', alpha=0.7)
    ax2.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')

    # 標記買入訊號在RSI圖上
    if not buy_signals.empty:
        ax2.scatter(buy_signals.index, buy_signals['RSI'], marker='^', color='green',
                   s=50, zorder=5)

    ax2.set_title('RSI(14) Indicator')
    ax2.set_ylabel('RSI')
    ax2.set_ylim(0, 100)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/workspaces/glod/pine_strategy_chart.png', dpi=300, bbox_inches='tight')
    plt.savefig('/workspaces/glod/pine_strategy_chart.svg', bbox_inches='tight')
    plt.show()

    return buy_signals

# 主函數
if __name__ == "__main__":
    # 檢查是否安裝了TA-Lib
    try:
        import talib
    except ImportError:
        print("需要安裝TA-Lib庫，請運行: pip install TA-Lib")
        exit(1)

    # 獲取數據
    data = get_gold_data()

    # 計算指標
    data = calculate_rsi(data)
    data = calculate_emas(data)

    # 應用策略
    data = apply_pine_strategy(data)

    # 繪製圖表
    buy_signals = plot_strategy_chart(data)

    # 統計訊號
    print("=== Pine Script Strategy Analysis ===")
    print(f"數據期間: {data.index.min().date()} 到 {data.index.max().date()}")
    print(f"總交易日: {len(data)}")
    print(f"買入訊號數量: {len(buy_signals)}")

    if len(buy_signals) > 0:
        print("\n買入訊號日期:")
        for date in buy_signals.index[:10]:  # 只顯示前10個
            print(f"- {date.date()}")
        if len(buy_signals) > 10:
            print(f"... 還有 {len(buy_signals) - 10} 個訊號")

    print("\n圖表已保存為 pine_strategy_chart.png 和 pine_strategy_chart.svg")
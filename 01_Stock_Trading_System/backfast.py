import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import platform
import numpy as np

# --- 🛠️ 字型設定 (解決中文亂碼) 🛠️ ---
if platform.system() == "Windows":
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
else:
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']   
plt.rcParams['axes.unicode_minus'] = False 

# --- 🚀 參數設定 🚀 ---
START_DATE = "2021-01-01" 
INITIAL_CAPITAL = 1_000_000 
FEE_RATE = 0.001425 * 0.6 
TAX_RATE = 0.003          

def get_user_input():
    print("\n" + "="*40)
    print("      台股全方位資產管理系統")
    print("="*40)
    
    stock_id = input("1. 請輸入股票代號 (如 2330): ").strip()
    if not stock_id:
        print("   預設使用 2330 (台積電)")
        stock_id = "2330.TW"
    elif stock_id.isdigit():
        stock_id = f"{stock_id}.TW"
    else:
        stock_id = stock_id.upper()

    try:
        qty_str = input("2. 請輸入持有股數 (沒買請按 Enter): ").strip()
        held_qty = float(qty_str) if qty_str else 0
        
        avg_cost = 0
        if held_qty > 0:
            cost_str = input("3. 請輸入平均成本 (例如 500): ").strip()
            avg_cost = float(cost_str) if cost_str else 0
    except:
        print("   輸入格式錯誤，設定為無庫存模式。")
        held_qty = 0
        avg_cost = 0
        
    return stock_id, held_qty, avg_cost

def get_fundamental_analysis(stock_id):
    """ 基本面分析 """
    print(f"   正在下載 {stock_id} 數據...")
    try:
        stock = yf.Ticker(stock_id)
        info = stock.info
        
        pe = info.get('trailingPE', None)
        roe = info.get('returnOnEquity', None)

        if pe:
            pe_status = "(便宜)" if pe < 15 else "(昂貴)" if pe > 30 else "(合理)"
            pe_str = f"{pe:.1f}倍 {pe_status}"
        else:
            pe_str = "N/A"

        if roe:
            roe_val = roe * 100
            roe_status = "(優秀)" if roe_val > 15 else "(偏弱)" if roe_val < 5 else "(尚可)"
            roe_str = f"{roe_val:.1f}% {roe_status}"
        else:
            roe_str = "N/A"

        return f"本益比: {pe_str}\nROE: {roe_str}"
    except:
        return "基本面數據 N/A"

def calculate_technical_indicators(df):
    """ 技術面分析 """
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    current_rsi = df['RSI'].iloc[-1]
    
    if current_rsi > 70: rsi_status = "過熱"
    elif current_rsi < 30: rsi_status = "超賣"
    else: rsi_status = "中性"
        
    return f"RSI(14): {current_rsi:.1f} ({rsi_status})"

def calculate_prediction(df):
    """ 趨勢預測 """
    recent_ma20 = df['MA20'].tail(5)
    slope = (recent_ma20.iloc[-1] - recent_ma20.iloc[0]) / recent_ma20.iloc[0]
    
    current_price = df['Close'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]
    ma60 = df['MA60'].iloc[-1]
    
    if current_price > ma20 and ma20 > ma60:
        if slope > 0.015:
            return "強力多頭", "持有 1~3 個月", "#ffcccc"
        else:
            return "緩步墊高", "持有 1~2 週", "#fff5cc"
    elif current_price < ma20:
        return "空頭走勢", "空手觀望", "#ccffcc"
    else:
        return "盤整震盪", "區間操作", "#eeeeee"

def run_backtest():
    # 1. 取得輸入
    stock_id, held_qty, avg_cost = get_user_input()
    
    # 2. 抓資料
    fund_info = get_fundamental_analysis(stock_id)
    try:
        df = yf.download(stock_id, start=START_DATE)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
    except Exception as e:
        print(f"下載失敗: {e}")
        return

    if df.empty:
        print("找不到資料。")
        return

    # 3. 計算
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    
    df['Signal'] = 0
    df.loc[df['MA20'] > df['MA60'], 'Signal'] = 1 
    df['Position'] = df['Signal'].shift(1) 
    df['Strategy_Return'] = df['Close'].pct_change() * df['Position']
    action_mask = df['Position'].diff().abs() > 0
    df.loc[action_mask, 'Strategy_Return'] -= (FEE_RATE + TAX_RATE/2)
    df['Equity'] = INITIAL_CAPITAL * (1 + df['Strategy_Return']).cumprod()
    
    total_return = (df['Equity'].iloc[-1] - INITIAL_CAPITAL) / INITIAL_CAPITAL
    df['Peak'] = df['Equity'].cummax()
    df['Drawdown'] = (df['Equity'] - df['Peak']) / df['Peak']
    mdd = df['Drawdown'].min()
    current_dd = df['Drawdown'].iloc[-1]

    tech_info = calculate_technical_indicators(df)
    pred_trend, pred_time, box_color = calculate_prediction(df)

    current_price = df['Close'].iloc[-1]
    
    # 庫存計算
    personal_pnl_str = "無庫存"
    if held_qty > 0:
        market_value = current_price * held_qty
        total_cost = avg_cost * held_qty
        unrealized_pl = market_value - total_cost
        roi = (unrealized_pl / total_cost) * 100
        personal_pnl_str = (
            f"持有: {held_qty:,.0f}股 (成本 {avg_cost})\n"
            f"損益: {unrealized_pl:+,.0f} ({roi:+.1f}%)"
        )

    # 4. 顯示報告
    print("\n" + "="*40)
    print(f"📊 {stock_id} 完整分析報告")
    print("="*40)
    print(f"總報酬率: {total_return*100:.2f}%")
    print(f"基本面: {fund_info.replace(chr(10), ' | ')}")
    print(f"技術面: {tech_info}")
    print(f"庫存狀況: {personal_pnl_str.replace(chr(10), ' | ')}")
    print("="*40)

    # 5. 畫圖
    plt.figure(figsize=(14, 8)) # 畫布加大
    
    plt.subplot(2, 1, 1)
    plt.plot(df.index, df['Close'], color='black', alpha=0.6, label='收盤價')
    plt.plot(df.index, df['MA20'], color='blue', alpha=0.8, label='月線')
    plt.plot(df.index, df['MA60'], color='orange', alpha=0.8, label='季線')
    if held_qty > 0:
        plt.axhline(y=avg_cost, color='green', linestyle='--', linewidth=2, label='成本線')
    plt.title(f'{stock_id} 價格走勢與個人成本', fontsize=14, fontweight='bold')
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 1, 2)
    plt.plot(df.index, df['Equity'], color='#C0392B', linewidth=2, label='策略績效')
    plt.title('策略資產曲線')
    plt.grid(True, alpha=0.3)

    # ★ 究極資訊框：所有資訊一次滿足 ★
    info_text = (
        f"【{stock_id} 分析摘要】\n"
        f"------------------\n"
        f"策略總報酬: {total_return*100:.2f}%\n"
        f"歷史最大回檔: {mdd*100:.2f}%\n"
        f"目前回檔: {current_dd*100:.2f}%\n"
        f"------------------\n"
        f"【庫存損益】\n"
        f"{personal_pnl_str}\n"
        f"------------------\n"
        f"【體質與指標】\n"
        f"{fund_info}\n"
        f"{tech_info}\n"
        f"------------------\n"
        f"趨勢: {pred_trend}\n"
        f"建議: {pred_time}"
    )
    
    # 調整文字框位置與字體大小，確保塞得下
    plt.gcf().text(0.76, 0.50, info_text, fontsize=9,
             bbox=dict(boxstyle='round,pad=0.5', facecolor=box_color, alpha=0.9, edgecolor='black'))

    plt.subplots_adjust(right=0.75)
    print("✅ 分析完成！全方位圖表已開啟。")
    plt.show()

if __name__ == "__main__":
    run_backtest()
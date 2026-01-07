import ccxt
import pandas as pd
import matplotlib.pyplot as plt
from strategy import apply_strategy

# =====================
# 參數
# =====================
SYMBOL = "ETC/USDT"
TIMEFRAME = "1h"
INITIAL_CAPITAL = 10000
START_DATE = "2024-01-01T00:00:00Z"
END_DATE = "2025-12-31"
RISK_PER_TRADE = 0.01   # 每筆虧損上限 1% 資金
TAKE_PROFIT_PCT = 0.02  # 停利 2% (可調整)

# =====================
# 抓資料
# =====================
exchange = ccxt.binance()
since = exchange.parse8601(START_DATE)

ohlcv = exchange.fetch_ohlcv(
    SYMBOL,
    timeframe=TIMEFRAME,
    since=since,
    limit=2000
)

df = pd.DataFrame(
    ohlcv,
    columns=["timestamp","open","high","low","close","volume"]
)

df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
df = df[df["datetime"] <= END_DATE]

# =====================
# 套用策略訊號
# =====================
df = apply_strategy(df)
# 假設 apply_strategy 已經產生 'signal' 欄位：1=多, -1=空, 0=無訊號

# =====================
# 回測 + 固定停損停利
# =====================
trades = []
equity = [INITIAL_CAPITAL]
capital = INITIAL_CAPITAL

i = 0
while i < len(df):
    row = df.iloc[i]
    signal = row.get("signal", 0)
    
    if signal == 0:
        equity.append(capital)
        i += 1
        continue

    entry_price = row['close']
    risk_amount = capital * RISK_PER_TRADE
    position_size = risk_amount / (entry_price * RISK_PER_TRADE)  # 假設用1%價差計算

    # 設定停損 / 停利
    if signal == 1:  # LONG
        stop_loss_price = entry_price * (1 - RISK_PER_TRADE)
        take_profit_price = entry_price * (1 + TAKE_PROFIT_PCT)
    elif signal == -1:  # SHORT
        stop_loss_price = entry_price * (1 + RISK_PER_TRADE)
        take_profit_price = entry_price * (1 - TAKE_PROFIT_PCT)

    # 從下一根 K 開始檢查出場
    exit_price = entry_price
    for j in range(i+1, len(df)):
        k = df.iloc[j]
        if signal == 1:  # 多單
            if k['low'] <= stop_loss_price:
                exit_price = stop_loss_price
                exit_index = j
                break
            elif k['high'] >= take_profit_price:
                exit_price = take_profit_price
                exit_index = j
                break
        elif signal == -1:  # 空單
            if k['high'] >= stop_loss_price:
                exit_price = stop_loss_price
                exit_index = j
                break
            elif k['low'] <= take_profit_price:
                exit_price = take_profit_price
                exit_index = j
                break
    else:
        # 沒觸及停損停利，以最後收盤價出場
        exit_index = len(df)-1
        exit_price = df.iloc[-1]['close']

    # 計算 PnL
    if signal == 1:
        pnl = (exit_price - entry_price) * position_size
    else:
        pnl = (entry_price - exit_price) * position_size

    capital += pnl
    equity.append(capital)

    trades.append({
        "datetime": row['datetime'],
        "type": "LONG" if signal==1 else "SHORT",
        "entry": entry_price,
        "exit": exit_price,
        "pnl": pnl
    })

    i = exit_index + 1  # 跳過已處理的 K

# =====================
# 存交易紀錄 CSV
# =====================
trade_log = pd.DataFrame(trades)
trade_log.to_csv("trade_log.csv", index=False)
print("已輸出 trade_log.csv")

# =====================
# 總體績效
# =====================
equity_series = pd.Series(equity)
final_value = equity_series.iloc[-1]

rolling_max = equity_series.cummax()
drawdown = (equity_series - rolling_max) / rolling_max
max_dd = drawdown.min() * 100

print("====== ETC 策略回測（2024–2025）======")
print(f"初始資金: {INITIAL_CAPITAL}")
print(f"最終資金: {round(final_value,2)}")
print(f"最大回撤: {round(max_dd,2)}%")

# =====================
# 多單 vs 空單績效
# =====================
def summary(name, df):
    if len(df) == 0:
        print(f"{name}: 無交易")
        return
    print(f"\n--- {name} ---")
    print(f"交易次數: {len(df)}")
    print(f"總損益: {round(df['pnl'].sum(),2)}")
    print(f"勝率: {round((df['pnl'] > 0).mean()*100,2)}%")

summary("多單 LONG", trade_log[trade_log["type"] == "LONG"])
summary("空單 SHORT", trade_log[trade_log["type"] == "SHORT"])

# =====================
# Equity Curve（存檔）
# =====================
plt.figure(figsize=(10,5))
plt.plot(equity_series)
plt.title("ETC Equity Curve (2024–2025)")
plt.xlabel("Time")
plt.ylabel("Equity")
plt.grid(True)
plt.savefig("equity_curve.png")
plt.close()
print("\n已輸出 equity_curve.png")

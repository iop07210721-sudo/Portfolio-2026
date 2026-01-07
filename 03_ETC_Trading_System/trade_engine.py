import pandas as pd

def backtest(df, capital=10000, sl=0.03, tp=0.06):
    position = 0
    entry_price = 0
    entry_type = None

    equity_curve = []
    trades = []
    trade_log = []

    for i in range(1, len(df)):
        price = df.iloc[i]["close"]
        signal = df.iloc[i]["signal"]
        time = df.iloc[i]["datetime"]

        pnl = 0

        # === 開倉 ===
        if position == 0:
            if signal == 1:
                position = capital / price
                entry_price = price
                entry_type = "LONG"
                capital = 0

            elif signal == -1:
                position = -capital / price
                entry_price = price
                entry_type = "SHORT"
                capital = 0

        # === 持倉中 ===
        else:
            if entry_type == "LONG":
                pnl = (price - entry_price) * position
                stop_loss = price <= entry_price * (1 - sl)
                take_profit = price >= entry_price * (1 + tp)
                exit_signal = signal == -1

            else:  # SHORT
                pnl = (entry_price - price) * abs(position)
                stop_loss = price >= entry_price * (1 + sl)
                take_profit = price <= entry_price * (1 - tp)
                exit_signal = signal == 1

            if stop_loss or take_profit or exit_signal:
                capital = abs(position) * price
                trades.append(pnl)

                trade_log.append({
                    "time": time,
                    "type": entry_type,
                    "entry_price": entry_price,
                    "exit_price": price,
                    "pnl": pnl
                })

                position = 0
                entry_price = 0
                entry_type = None

        equity = capital if position == 0 else capital + pnl
        equity_curve.append(equity)

    pd.DataFrame(trade_log).to_csv("trade_log.csv", index=False)
    return trades, equity_curve

import ta

def apply_strategy(df):
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma60"] = df["close"].rolling(60).mean()
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], 14).rsi()

    df["signal"] = 0

    # 多單
    df.loc[
        (df["ma20"] > df["ma60"]) & (df["rsi"] > 55),
        "signal"
    ] = 1

    # 空單
    df.loc[
        (df["ma20"] < df["ma60"]) & (df["rsi"] < 45),
        "signal"
    ] = -1

    return df


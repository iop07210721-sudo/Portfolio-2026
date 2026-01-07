# glod - 黃金交易策略

這是一個簡單的黃金交易策略實現，使用 Python 和 yfinance 獲取黃金價格數據，並基於移動平均線和 RSI 指標生成交易信號，並模擬決策。

## 策略描述

- 使用黃金期貨 (GC=F) 的歷史數據 (2024-2025)。
- 計算 50 日和 200 日移動平均線。
- 計算 RSI 指標 (14 日)。
- 買入條件：短期 MA > 長期 MA 且 RSI < 70。
- 賣出條件：短期 MA < 長期 MA 或 RSI > 30。
- 模擬交易決策，顯示資本變化。

## LSTM 機器學習預測

運行 `python lstm_predictor.py` 來使用 LSTM 神經網路預測黃金價格。

- 使用過去 60 天數據預測下一天價格
- 訓練 50 個 epoch，包含驗證
- 評估指標：MSE, MAE, RMSE
- 預測未來 30 天價格走勢
- 生成包含訓練歷史、測試預測和未來預測的綜合圖表

## 生成圖表

運行 `python chart_generator.py` 來創建綜合圖表，包括價格走勢、成交量、價格分佈和月度平均價格。圖表會保存為 `gold_chart.png`。

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 運行決策程式

```bash
python main.py
```

這將下載數據、計算指標、生成信號、模擬交易並繪製圖表。
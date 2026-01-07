# 📈 台股全方位智慧選股與雲端監控系統
**Intelligent Stock Trading Strategy & Cloud Monitoring System**

## 專案簡介
本專案為「程式交易策略」課程期末成果。系統整合了 **Python 數據分析** 與 **GitHub Actions 雲端自動化** 技術，旨在解決投資人無法全天候盯盤的痛點，並提供量化的進出場依據。

## 🚀 核心功能
本系統採用 **Hybrid 混合架構**，具備兩種運作模式：

### 1. 📊 本地端分析模式 (Local Analysis)
- **策略回測**：基於 MA20/MA60 黃金交叉策略，回測近 5 年績效。
- **全方位健檢**：自動抓取 **本益比 (P/E)**、**ROE** 與 **RSI** 指標。
- **資產管理**：輸入庫存成本，即時計算未實現損益與報酬率。
- **AI 趨勢預測**：根據均線斜率，提供「建議持有時間」與「多空判斷」。

### 2. ☁️ 雲端監控模式 (Cloud Monitoring)
- **24H 自動化**：利用 GitHub Actions CRON 排程，每 **30 分鐘** 自動喚醒。
- **即時推播**：串接 **Discord Webhook**，將最新股價、趨勢訊號傳送至手機。
- **Serverless**：無需架設伺服器，實現零成本雲端盯盤。

## 🛠️ 使用技術
- **語言**：Python 3.11
- **數據源**：yfinance (Yahoo Finance API)
- **分析套件**：Pandas, NumPy, Matplotlib
- **雲端整合**：GitHub Actions, Discord API

## 📉 實測成果
<img width="866" height="524" alt="image" src="https://github.com/user-attachments/assets/24e40703-35ba-476c-bc84-9f84e0cc855f" />


## 📦 安裝與執行
1. 安裝套件：
   ```bash
   pip install yfinance pandas matplotlib requests

import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 設置中文字體（如果可用）
try:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

# 獲取黃金數據
def get_gold_data(start_date='2020-01-01', end_date='2025-12-31'):
    gold = yf.Ticker("GC=F")
    data = gold.history(start=start_date, end=end_date)
    return data['Close'].values.reshape(-1, 1)

# 數據預處理：創建序列
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

# 構建 LSTM 模型
def build_lstm_model(seq_length):
    model = Sequential()
    model.add(LSTM(100, return_sequences=True, input_shape=(seq_length, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(100, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# 訓練模型
def train_model(X_train, y_train, seq_length, epochs=100):
    model = build_lstm_model(seq_length)
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=32, validation_split=0.1, verbose=1)
    return model, history

# 預測未來價格
def predict_future(model, last_sequence, scaler, days_ahead=30):
    predictions = []
    current_sequence = last_sequence.copy()

    for _ in range(days_ahead):
        pred = model.predict(current_sequence.reshape(1, seq_length, 1), verbose=0)
        predictions.append(pred[0][0])
        current_sequence = np.roll(current_sequence, -1)
        current_sequence[-1] = pred[0][0]

    # 反標準化
    predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
    return predictions.flatten()

# 評估模型
def evaluate_model(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    return mse, mae, rmse

# 主函數
if __name__ == "__main__":
    try:
        # 獲取數據
        data = get_gold_data()
        print(f"數據長度: {len(data)}")

        # 標準化數據
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        # 創建訓練序列
        seq_length = 60  # 使用過去 60 天預測下一天
        X, y = create_sequences(scaled_data, seq_length)

        # 分割訓練和測試數據
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        print(f"訓練數據: {X_train.shape}, 測試數據: {X_test.shape}")

        # 訓練模型
        model, history = train_model(X_train, y_train, seq_length, epochs=50)

        # 預測測試數據
        predictions = model.predict(X_test, verbose=0)
        predictions = scaler.inverse_transform(predictions)
        y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

        # 評估模型
        mse, mae, rmse = evaluate_model(y_test_actual, predictions)
        print(f"測試 MSE: {mse:.2f}")
        print(f"測試 MAE: {mae:.2f}")
        print(f"測試 RMSE: {rmse:.2f}")

        # 預測未來 30 天
        last_sequence = scaled_data[-seq_length:]
        future_predictions = predict_future(model, last_sequence, scaler, days_ahead=30)

        # 繪製結果
        plt.figure(figsize=(16, 10))

        # 子圖1: 訓練歷史
        plt.subplot(2, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Training History')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)

        # 子圖2: 測試預測 vs 實際
        plt.subplot(2, 2, 2)
        plt.plot(y_test_actual, label='Actual Price', color='blue')
        plt.plot(predictions, label='Predicted Price', color='red')
        plt.title('Test Data Prediction')
        plt.xlabel('Sample')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True)

        # 子圖3: 整體價格走勢
        plt.subplot(2, 2, 3)
        plt.plot(data, label='Actual Price', color='blue')
        test_start = len(data) - len(predictions)
        plt.plot(range(test_start, len(data)), predictions, label='Test Prediction', color='red')
        plt.title('Overall Price Trend')
        plt.xlabel('Days')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True)

        # 子圖4: 未來預測
        plt.subplot(2, 2, 4)
        future_start = len(data)
        future_dates = range(future_start, future_start + len(future_predictions))
        plt.plot(data[-100:], label='Last 100 Days Actual Price', color='blue')
        plt.plot(future_dates, future_predictions, label='Future Prediction (30 Days)', color='green', linestyle='--')
        plt.title('Future Price Prediction')
        plt.xlabel('Days')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.savefig('/workspaces/glod/lstm_prediction.png', dpi=300, bbox_inches='tight')
        plt.show()

        print("LSTM 預測完成。圖表已保存為 lstm_prediction.png")
        print(f"未來 30 天預測價格範圍: ${future_predictions.min():.2f} - ${future_predictions.max():.2f}")
        print(f"預測平均價格: ${future_predictions.mean():.2f}")

    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
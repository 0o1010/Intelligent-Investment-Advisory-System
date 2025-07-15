import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
from ta.momentum import RSIIndicator
from ta.trend import MACD
import keras_tuner as kt
import time
import yfinance as yf

# -------------------- 1. 数据加载与特征工程 --------------------
def load_and_engineer_data(file_path, start_date="2018-01-01"):
    df = get_data('QQQ', '2018-01-01', '2025-07-01')
    df.columns = [col.title() for col in df.columns]
    print(df.columns)
    df = df.loc[start_date:].copy()
    df['RSI'] = RSIIndicator(df['Close']).rsi()
    macd = MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df.dropna(inplace=True)
    return df

# -------------------- 2. 数据归一化与序列生成 --------------------
def preprocess_data(df, feature_cols, target_col, window_size):
    scaler_features = MinMaxScaler()
    scaler_target = MinMaxScaler()
    scaled_features = scaler_features.fit_transform(df[feature_cols])
    scaled_target = scaler_target.fit_transform(df[[target_col]])

    X, y = [], []
    for i in range(window_size, len(scaled_features)):
        X.append(scaled_features[i - window_size:i])
        y.append(scaled_target[i, 0])
    return np.array(X), np.array(y), scaler_features, scaler_target

# -------------------- 3. 简化版模型构建函数 --------------------
def build_model_simple(hp):
    model = Sequential()
    model.add(Bidirectional(
        LSTM(hp.Int('lstm_units', 32, 64, step=32), return_sequences=False),
        input_shape=(hp['window_size'], hp['num_features'])
    ))
    model.add(Dropout(hp.Float('drop_rate', 0.2, 0.4, step=0.1)))
    model.add(Dense(hp.Int('dense_units', 25, 50, step=25)))
    model.add(Dense(1))
    model.compile(optimizer=tf.keras.optimizers.Adam(hp.Choice('learning_rate', [1e-3])),
                  loss='mean_squared_error')
    return model

# -------------------- 4. 超参数搜索 --------------------
def tune_model(X, y, window_size, num_features, ticker, max_trials=3, epochs=10):
    split = int(len(X) * 0.8)
    x_train, x_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]

    def model_wrapper(hp):
        hp['window_size'] = window_size
        hp['num_features'] = num_features
        return build_model_simple(hp)

    tuner = kt.RandomSearch(
        model_wrapper,
        objective='val_loss',
        max_trials=max_trials,
        executions_per_trial=1,
        directory='keras_tuner_dir_fast',
        project_name=f'{ticker}_fast_tuning'
    )
    tuner.search(x_train, y_train,
                 validation_data=(x_val, y_val),
                 callbacks=[EarlyStopping(monitor='val_loss', patience=2)],
                 epochs=epochs,
                 verbose=0)
    return tuner

# -------------------- 5. 模型训练 --------------------
def train_final_model(model, X, y, train_rate=0.85, batch_size=128, epochs=15):
    split = int(len(X) * train_rate)
    x_train, x_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model.fit(x_train, y_train,
              validation_data=(x_test, y_test),
              epochs=epochs,
              batch_size=batch_size,
              callbacks=[EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)],
              verbose=0)
    return model, x_test, y_test

# -------------------- 6. 模型评估 --------------------
def evaluate_model(model, x_test, y_test, scaler_target):
    y_pred = model.predict(x_test, verbose=0)
    y_test_nn = scaler_target.inverse_transform(y_test.reshape(-1, 1))
    y_pred_nn = scaler_target.inverse_transform(y_pred)
    rmse = np.sqrt(mean_squared_error(y_test_nn, y_pred_nn))
    return y_pred_nn, y_test_nn, rmse

# -------------------- 7. 未来预测 --------------------
def predict_future(model, last_seq, future_days, feature_cols, scaler_target, target_col='Close'):
    future_predictions = []
    current_seq = last_seq.copy()
    for _ in range(future_days):
        next_pred_scaled = model.predict(current_seq, verbose=0)[0, 0]
        future_predictions.append(next_pred_scaled)
        new_row = current_seq[0, -1, :].copy()
        new_row[feature_cols.index(target_col)] = next_pred_scaled
        current_seq = np.append(current_seq[:, 1:, :], [[new_row]], axis=1)
    return scaler_target.inverse_transform(np.array(future_predictions).reshape(-1, 1))

# -------------------- 8. 可视化 --------------------
def plot_predictions(y_test, y_pred, future_pred, df, future_days):
    plt.figure(figsize=(15, 7))
    plot_data = df.iloc[-len(y_test):]
    plt.plot(plot_data.index, y_test, label='Actual Price', color='blue')
    plt.plot(plot_data.index, y_pred, label='Predicted Price', color='orange')

    last_date = plot_data.index[-1]
    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=future_days)
    plt.plot(future_dates, future_pred, label='Future Prediction', color='green', linestyle='--', marker='o')

    plt.title("Price Prediction")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.show()

def get_data(code: str, start_date: str, end_date: str):
    etf = yf.Ticker(code)
    hist = etf.history(start=start_date, end=end_date, auto_adjust=False)
    df = hist.reset_index()

    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"])

    df = (df.assign(Date=lambda x: x['Date'].dt.tz_localize(None).dt.strftime('%Y-%m-%d'))
    .rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    }))
    return df
if __name__ == "__main__":
    start_time = time.time()

    ticker = "QQQ"
    file_path = fr"D:\橘子先生\HKUcs\Project\data\{ticker}.csv"
    feature_cols = ['Close', 'Volume', 'RSI', 'MACD', 'MACD_signal']
    target_col = 'Close'
    window_size = 30
    search_len = 500
    future_days = 10

    df = load_and_engineer_data(file_path)
    scaled_X, scaled_y, _, scaler_target = preprocess_data(df, feature_cols, target_col, window_size)

    # 搜索阶段子集
    X_search, y_search = scaled_X[-search_len:], scaled_y[-search_len:]

    tuner = tune_model(X_search, y_search, window_size, len(feature_cols), ticker)

    best_hp = tuner.get_best_hyperparameters(1)[0]
    best_hp['window_size'] = window_size
    best_hp['num_features'] = len(feature_cols)
    model = build_model_simple(best_hp)

    model, x_test, y_test = train_final_model(model, scaled_X, scaled_y)
    y_pred_nn, y_test_nn, rmse = evaluate_model(model, x_test, y_test, scaler_target)

    print(f"\n最终测试集 RMSE: {rmse:.2f}")

    last_seq = scaled_X[-1].reshape(1, window_size, len(feature_cols))
    future_pred = predict_future(model, last_seq, future_days, feature_cols, scaler_target)

    plot_predictions(y_test_nn, y_pred_nn, future_pred, df, future_days)

    print(f"\n总运行时间: {time.time() - start_time:.2f} 秒")

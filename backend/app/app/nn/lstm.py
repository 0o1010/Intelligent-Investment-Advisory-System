from ta.momentum import RSIIndicator
from ta.trend import MACD
import keras_tuner as kt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd
import tensorflow as tf
import random


def lstm_two(stk_data, window_size=30, train_rate=0.85, future_days=10, search_data_len=50):
    seed = 3
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
    kt.engine.hyperparameters.HyperParameters._random_state = np.random.RandomState(seed)
    df = stk_data.copy()
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df[['close', 'volume']].copy()
    df['RSI'] = RSIIndicator(df['close']).rsi()
    macd = MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df.dropna(inplace=True)

    feature_cols = ['close', 'volume', 'RSI', 'MACD', 'MACD_signal']
    target_col = 'close'
    num_features = len(feature_cols)

    scaler_features = MinMaxScaler()
    scaler_target = MinMaxScaler()
    scaled_features = scaler_features.fit_transform(df[feature_cols])
    scaled_target = scaler_target.fit_transform(df[[target_col]])

    scaled_features_search = scaled_features[-search_data_len:]
    scaled_target_search = scaled_target[-search_data_len:]
    X_search, y_search = [], []
    for i in range(window_size, len(scaled_features_search)):
        X_search.append(scaled_features_search[i - window_size:i])
        y_search.append(scaled_target_search[i, 0])
    X_search, y_search = np.array(X_search), np.array(y_search)

    split_index = int(len(X_search) * train_rate)
    x_train_search, x_val_search = X_search[:split_index], X_search[split_index:]
    y_train_search, y_val_search = y_search[:split_index], y_search[split_index:]

    def build_model_simple(hp):
        model = Sequential()
        model.add(Bidirectional(LSTM(hp.Int('lstm_units', 32, 64, step=32), return_sequences=False),
                                input_shape=(window_size, num_features)))
        model.add(Dropout(hp.Float('drop_rate', 0.2, 0.4, step=0.1)))
        model.add(Dense(hp.Int('dense_units', 25, 50, step=25)))
        model.add(Dense(1))
        model.compile(optimizer=tf.keras.optimizers.Adam(hp.Choice('learning_rate', [1e-3])),
                      loss='mean_squared_error')
        return model

    tuner = kt.RandomSearch(
        build_model_simple,
        objective='val_loss',
        max_trials=3,
        executions_per_trial=1,
        directory='keras_tuner_lstm_fast',
        project_name='lstm_fast_tune'
    )
    tuner.search(x_train_search, y_train_search,
                 validation_data=(x_val_search, y_val_search),
                 callbacks=[EarlyStopping(monitor='val_loss', patience=2)],
                 epochs=10,
                 verbose=0)
    best_hp = tuner.get_best_hyperparameters(1)[0]
    model = tuner.hypermodel.build(best_hp)

    X_full, y_full = [], []
    for i in range(window_size, len(scaled_features)):
        X_full.append(scaled_features[i - window_size:i])
        y_full.append(scaled_target[i, 0])
    X_full, y_full = np.array(X_full), np.array(y_full)

    split_index = int(len(X_full) * train_rate)
    x_train, x_test = X_full[:split_index], X_full[split_index:]
    y_train, y_test = y_full[:split_index], y_full[split_index:]

    history = model.fit(x_train, y_train,
                        epochs=15,
                        batch_size=128,
                        validation_data=(x_test, y_test),
                        callbacks=[EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)],
                        verbose=0)
    y_train_pred = model.predict(x_train, verbose=0)
    y_test_pred = model.predict(x_test, verbose=0)
    y_train_pred_nn = scaler_target.inverse_transform(y_train_pred)
    y_test_pred_nn = scaler_target.inverse_transform(y_test_pred)
    y_train_nn = scaler_target.inverse_transform(y_train.reshape(-1, 1))
    y_test_nn = scaler_target.inverse_transform(y_test.reshape(-1, 1))

    mean_rmse = np.sqrt(mean_squared_error(y_test_nn, y_test_pred_nn))
    mean_norm_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    mean_mape = np.mean(np.abs((y_test_nn - y_test_pred_nn) / y_test_nn)) * 100

    train_dates = df.index[window_size:split_index + window_size]
    valid_dates = df.index[split_index + window_size:]
    train_df = pd.DataFrame({'close': y_train_nn.flatten(), 'Prediction': y_train_pred_nn.flatten()},
                            index=train_dates)
    valid_df = pd.DataFrame({'close': y_test_nn.flatten(), 'Prediction': y_test_pred_nn.flatten()},
                            index=valid_dates)

    current_seq = scaled_features[-window_size:].reshape(1, window_size, num_features)
    future_predictions = []
    for _ in range(future_days):
        next_pred = model.predict(current_seq, verbose=0)[0, 0]
        future_predictions.append(next_pred)
        new_row = current_seq[0, -1, :].copy()
        new_row[feature_cols.index(target_col)] = next_pred
        current_seq = np.append(current_seq[:, 1:, :], [[new_row]], axis=1)
    future_predictions_nn = scaler_target.inverse_transform(np.array(future_predictions).reshape(-1, 1))

    last_date = df.index[-1]
    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=future_days)
    future_dates = [d.strftime('%Y-%m-%d') for d in future_dates]
    future_df = pd.DataFrame({'date': future_dates, 'Prediction': future_predictions_nn.flatten()})
    future_df.set_index('date', inplace=True)

    actual_data = pd.concat([train_df, valid_df])
    pred_data = pd.concat([train_df, valid_df, future_df])
    pred_data = pred_data[['Prediction']]
    return actual_data, pred_data, history.history['loss'], mean_norm_rmse, mean_rmse, mean_mape


def get_data(code: str, start_date: str, end_date: str):
    import yfinance as yf
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

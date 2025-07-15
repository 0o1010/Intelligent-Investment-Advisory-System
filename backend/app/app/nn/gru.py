import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dropout, Dense
def gru_three(stk_data, window_size=30, train_rate=0.8, drop_rate=0.2, batch_size=32, lstm_gru_units=64, epochs=20,
              future_days=10):
    stk_data['date'] = pd.to_datetime(stk_data['date'])
    stk_data.set_index('date', inplace=True)

    data_close = stk_data[['close']].copy()
    s_data = data_close.values
    sca = MinMaxScaler(feature_range=(0, 1))
    normal_data = sca.fit_transform(s_data)
    x, y = [], []
    for i in range(window_size, len(normal_data)):
        x.append(normal_data[i - window_size:i, 0])
        y.append(normal_data[i, 0])
    x, y = np.array(x), np.array(y)
    split_index = int(len(x) * train_rate)
    x_train, x_test = x[:split_index], x[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    model = Sequential()
    model.add(GRU(units=lstm_gru_units, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(Dropout(drop_rate))
    model.add(GRU(units=lstm_gru_units, return_sequences=True))
    model.add(Dropout(drop_rate))
    model.add(GRU(units=lstm_gru_units))
    model.add(Dropout(drop_rate))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    history = model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)

    y_train_pred = model.predict(x_train, verbose=0)
    y_test_pred = model.predict(x_test, verbose=0)
    y_train_pred_nn = sca.inverse_transform(y_train_pred)
    y_test_pred_nn = sca.inverse_transform(y_test_pred)
    y_train_nn = sca.inverse_transform(y_train.reshape(-1, 1))
    y_test_nn = sca.inverse_transform(y_test.reshape(-1, 1))
    mean_norm_rmse = np.sqrt(np.mean((y_test_pred - y_test) ** 2))
    mean_rmse = np.sqrt(np.mean((y_test_pred_nn - y_test_nn) ** 2))
    mean_mape = np.mean(np.abs((y_test_nn - y_test_pred_nn) / y_test_nn)) * 100

    train_dates = data_close.index[window_size:split_index + window_size]
    valid_dates = data_close.index[split_index + window_size:]

    train_df = pd.DataFrame({'close': y_train_nn.flatten(), 'Prediction': y_train_pred_nn.flatten()},
                            index=train_dates)
    valid_df = pd.DataFrame({'close': y_test_nn.flatten(), 'Prediction': y_test_pred_nn.flatten()},
                            index=valid_dates)

    future_predictions = []
    last_sequence = normal_data[-window_size:]
    current_batch = last_sequence.reshape(1, window_size, 1)

    for _ in range(future_days):
        next_pred = model.predict(current_batch, verbose=0)[0]
        future_predictions.append(next_pred)
        current_batch = np.append(current_batch[:, 1:, :], [[next_pred]], axis=1)

    future_predictions_nn = sca.inverse_transform(future_predictions)

    last_date = data_close.index[-1]
    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=future_days)
    future_dates = [date.strftime('%Y-%m-%d') for date in future_dates]
    future_df = pd.DataFrame({
        'date': future_dates,
        'Prediction': future_predictions_nn.flatten()
    })
    future_df.set_index('date', inplace=True)
    actual_data = pd.concat([train_df, valid_df], axis=0)
    pred_data = pd.concat([train_df, valid_df, future_df], axis=0)
    pred_data = pred_data[['Prediction']]
    print(pred_data)
    return actual_data, pred_data, history.history['loss'], mean_norm_rmse, mean_rmse, mean_mape


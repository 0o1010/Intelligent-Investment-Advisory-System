import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout


def artificial_neural_network_model(stk_data, window_size=30, train_rate=0.8, drop_rate=0.2, batch_size=32, epochs=20,
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

    classifier = Sequential()
    classifier.add(Dense(units=128, activation='relu', input_dim=window_size))
    classifier.add(Dropout(drop_rate))
    classifier.add(Dense(units=64, activation='relu'))
    classifier.add(Dropout(drop_rate))
    classifier.add(Dense(units=1))
    classifier.compile(optimizer='adam', loss='mean_squared_error')
    history = classifier.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, verbose=0)

    y_train_pred = classifier.predict(x_train, verbose=0)
    y_test_pred = classifier.predict(x_test, verbose=0)
    y_train_pred_nn = sca.inverse_transform(y_train_pred)
    y_test_pred_nn = sca.inverse_transform(y_test_pred)
    y_train_nn = sca.inverse_transform(y_train.reshape(-1, 1))
    y_test_nn = sca.inverse_transform(y_test.reshape(-1, 1))
    rmse = np.sqrt(mean_squared_error(y_test_nn, y_test_pred_nn))
    mape = mean_absolute_percentage_error(y_test_nn, y_test_pred_nn) * 100

    future_predictions = []
    last_sequence = normal_data[-window_size:].flatten()
    current_batch = last_sequence.reshape(1, window_size)

    for i in range(future_days):
        next_pred = classifier.predict(current_batch, verbose=0)[0]
        future_predictions.append(next_pred)
        new_sequence = np.append(current_batch[0][1:], next_pred)
        current_batch = new_sequence.reshape(1, window_size)

    future_predictions_nn = sca.inverse_transform(future_predictions)

    train_df = data_close[window_size:split_index + window_size].copy()
    valid_df = data_close[split_index + window_size:].copy()
    train_df['Prediction'] = y_train_pred_nn
    valid_df['Prediction'] = y_test_pred_nn
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
    return actual_data, pred_data, history.history['loss'], rmse, mape

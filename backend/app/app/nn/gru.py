import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GRU, Dropout


def predict_future(model, last_window, scaler, num_days=30):
    pred_window = last_window.copy()
    future_preds = []

    for _ in range(num_days):
        X = np.reshape(pred_window, (1, pred_window.shape[0], 1))
        pred = model.predict(X, verbose=0)[0][0]
        future_preds.append(pred)
        pred_window = np.append(pred_window[1:], pred)

    future_preds_transformed = scaler.inverse_transform(np.array(future_preds).reshape(-1, 1))

    return future_preds_transformed.flatten()


def gru_three(fin_data, window_size, train_rate, drop_rate, batch_size, lstm_gru_units, epochs):
    data_close = fin_data.filter(['close'])

    s_data = data_close.values
    sca = MinMaxScaler(feature_range=(0, 1))
    normal_data = sca.fit_transform(s_data)

    def data_split(data, step_size):
        x, y, z = [], [], []
        for i in range(step_size, len(data)):
            x.append(data[i - step_size:i, -1])
            y.append(data[i - 1, -1])
        return np.array(x), np.array(y)

    x1, y1 = data_split(normal_data, step_size=window_size)

    split_index = int(np.ceil(len(x1) * (train_rate)))
    x_train, x_test = x1[:split_index], x1[split_index:]
    y_train, y_test = y1[:split_index], y1[split_index:]

    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    y_train = np.reshape(y_train, (y_train.shape[0], 1))
    y_test = np.reshape(y_test, (y_test.shape[0], 1))

    av_rmse = 0
    av_rmse1 = 0
    av_mape = 0

    # GRU Model Three
    def gru_model_three(av_rmse, av_rmse1, av_mape):
        model_loss_graph_points = []
        for i in range(10):
            GRU3 = Sequential()
            GRU3.add(GRU(lstm_gru_units, input_shape=(window_size, 1), return_sequences=True))
            GRU3.add(Dropout(drop_rate))
            GRU3.add(GRU(lstm_gru_units, input_shape=(window_size, 1), return_sequences=True))
            GRU3.add(Dropout(drop_rate))
            GRU3.add(GRU(lstm_gru_units, input_shape=(window_size, 1)), )
            GRU3.add(Dropout(drop_rate))
            GRU3.add(Dense(units=1, activation='linear'))
            GRU3.compile(loss='mse', optimizer='adam')

            history = GRU3.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)

            y_test_pred = GRU3.predict(x_test)
            y_train_pred = GRU3.predict(x_train)

            rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
            av_rmse = av_rmse + rmse
            y_test_pred_nn = sca.inverse_transform(y_test_pred)
            y_train_pred_nn = sca.inverse_transform(y_train_pred)
            y_test_nn = sca.inverse_transform(y_test)
            rmse1 = np.sqrt(mean_squared_error(y_test_nn, y_test_pred_nn))
            mape = mean_absolute_percentage_error(y_test, y_test_pred)
            av_rmse1 = av_rmse1 + rmse1
            av_mape = av_mape + mape
            GRU3.reset_states()
            model_loss_graph_points.append(history.history['loss'])

        train = data_close[window_size:split_index + window_size]
        valid = data_close[split_index + window_size:]

        train['Prediction'] = y_train_pred_nn
        valid['Prediction'] = y_test_pred_nn

        return train[['close', 'Prediction']], valid[['close', 'Prediction']], model_loss_graph_points[
            0], av_rmse / 10, av_rmse1 / 10, av_mape / 10

    df1, df2, model_loss, mean_norm_rmse, mean_rmse, mean_mape = gru_model_three(av_rmse, av_rmse1, av_mape)
    return df1, df2, model_loss, mean_norm_rmse, mean_rmse, mean_mape


def test_gru_three_model(data):
    data.set_index('date', inplace=True)
    stock_data = data

    window_size = 30  # Sliding window size
    train_rate = 0.8  # Training dataset size
    drop_rate = 0.2  # Dropout rate
    batch_size = 32
    lstm_gru_units = 64  # GRU units
    epochs = 10

    print("Running the GRU three layer model...")
    train_df, valid_df, model_loss, mean_norm_rmse, mean_rmse, mean_mape = gru_three(
        stock_data, window_size, train_rate, drop_rate, batch_size, lstm_gru_units, epochs
    )

    print(f"Mean norm RMSE: {mean_norm_rmse:.4f}")
    print(f"RMSE: {mean_rmse:.4f}")
    print(f"MAPE: {mean_mape:.4f}")

    data_close = stock_data.filter(['close'])
    s_data = data_close.values
    scaler = MinMaxScaler(feature_range=(0, 1))
    normal_data = scaler.fit_transform(s_data)

    def data_split(data, step_size):
        x, y = [], []
        for i in range(step_size, len(data)):
            x.append(data[i - step_size:i, -1])
            y.append(data[i - 1, -1])
        return np.array(x), np.array(y)

    x1, y1 = data_split(normal_data, step_size=window_size)

    split_index = int(np.ceil(len(x1) * (train_rate)))
    x_train, x_test = x1[:split_index], x1[split_index:]
    y_train, y_test = y1[:split_index], y1[split_index:]

    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    y_train = np.reshape(y_train, (y_train.shape[0], 1))

    model = Sequential()
    model.add(GRU(units=lstm_gru_units, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))
    model.add(Dropout(drop_rate))
    model.add(GRU(units=lstm_gru_units, return_sequences=True))
    model.add(Dropout(drop_rate))
    model.add(GRU(units=lstm_gru_units))
    model.add(Dropout(drop_rate))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)
    last_window = normal_data[-window_size:, 0]

    future_preds = predict_future(model, last_window, scaler, num_days=30)

    last_date = stock_data.index[-1]
    future_dates = pd.date_range(start=pd.to_datetime(last_date) + pd.Timedelta(days=1), periods=30, freq='D')
    future_dates = [date.strftime('%Y-%m-%d') for date in future_dates]

    future_df = pd.DataFrame({
        'date': future_dates,
        'Prediction': future_preds
    })
    future_df.set_index('date', inplace=True)
    actual_data = pd.concat([train_df, valid_df], axis=0)
    actual_data.sort_values('date', inplace=True)
    pred_data = pd.concat([train_df, valid_df, future_df], axis=0)
    pred_data.sort_values('date', inplace=True)
    pred_data = pred_data[['Prediction']]
    return actual_data, pred_data, model_loss, mean_norm_rmse, mean_rmse, mean_mape

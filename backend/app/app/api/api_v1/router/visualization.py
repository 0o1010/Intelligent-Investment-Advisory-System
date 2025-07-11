from fastapi import APIRouter, Depends
import pandas as pd
from sqlalchemy.orm import Session
import yfinance as yf
from app.core.response import resp_200, resp_401
from app.nn.gru import test_gru_three_model
from app.nn.lstm import test_lstm_two_model
from app.db.db_session import get_db
from app.models.etf import ETF

router = APIRouter()


@router.get("/getAllETF")
def get_all_etf(db: Session = Depends(get_db)):
    data = db.query(ETF).filter().all()
    etfs = []
    for i in range(len(data)):
        etfs.append({'value': data[i].value, 'label': f"{data[i].value} - {data[i].label}"})
    return resp_200(data=etfs)


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


@router.get("/getPrice", summary='Get history and predicted price of a financial instrument')
async def get_finance_price(model: str, code: str, start_date: str, end_date: str):
    try:
        df = get_data(code, start_date, end_date)
        if model == 'LSTM':
            actual_data, pred_data, model_loss, mean_norm_rmse, mean_rmse, mean_mape = test_lstm_two_model(df.copy())
        else:
            actual_data, pred_data, model_loss, mean_norm_rmse, mean_rmse, mean_mape = test_gru_three_model(df.copy())

        actual_data = actual_data.reset_index()
        pred_data = pred_data.reset_index()
        train_records = actual_data.to_dict(orient="records")
        valid_records = pred_data.to_dict(orient="records")
        return resp_200(data={
            "train": train_records,
            "valid": valid_records,
            "metrics": {
                "mean_norm_rmse": mean_norm_rmse,
                "mean_rmse": mean_rmse,
                "mean_mape": mean_mape
            }
        })

    except Exception as e:
        print(e)
        return resp_401(message="Error fetching and predicting prices: {}".format(e))

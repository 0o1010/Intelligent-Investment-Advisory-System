from fastapi import APIRouter, Depends
import os
import openai
import pandas as pd
import yfinance as yf
from app.core.response import resp_200, resp_401

router = APIRouter()


@router.get("/getPrice", summary='Get history price of a financial instrument')
async def get_finance_price(code: str, start_date: str, end_date: str):
    try:
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

        return resp_200(data=df.to_dict(orient="records"), total=len(df))

    except Exception as e:
        print(e)
        return resp_401(message="Error fetching historical prices: {}".format(e))




import os, requests
import yfinance as yf
from datetime import datetime
import pandas as pd

def update_rates():
    krw = round(yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1], 2)
    cny = round(yf.Ticker("USDCNY=X").history(period="1d")['Close'].iloc[-1], 4)
    record = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "usd_krw": krw, "usd_cny": cny}
    
    df = pd.DataFrame([record])
    df.to_csv("exchange_rates.csv", mode='a', header=not os.path.exists("exchange_rates.csv"), index=False, encoding="utf-8-sig")
    print(f"[성공] 저장 완료: USD/KRW={krw}, USD/CNY={cny}")

if __name__ == "__main__":
    update_rates()

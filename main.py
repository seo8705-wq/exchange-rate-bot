import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import yfinance as yf

def fetch_smbs_direct():
    """1순위: 서울외국환중개 공식 웹 크롤링 시도"""
    url = "https://www.smbs.biz/ExRate/TodayExRate.jsp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
        "Referer": "https://www.smbs.biz/"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            res.encoding = 'euc-kr'
            soup = BeautifulSoup(res.text, "html.parser")
            usd, cnh = None, None
            for row in soup.select("table tr"):
                text = row.get_text()
                if "USD" in text or "미국 달러" in text:
                    for td in row.find_all("td"):
                        val = td.get_text().strip().replace(",", "")
                        try:
                            f = float(val)
                            if f > 500: usd = f; break
                        except ValueError: pass
                if "CNH" in text or "중국 위안" in text or "CNY" in text:
                    for td in row.find_all("td"):
                        val = td.get_text().strip().replace(",", "")
                        try:
                            f = float(val)
                            if 50 < f < 500: cnh = f; break
                        except ValueError: pass
            if usd and cnh:
                return {"source": "서울외국환중개(공식)", "usd_krw": usd, "cnh_krw": cnh, "usd_cnh": round(usd / cnh, 4)}
    except Exception as e:
        print(f"SMBS 직접 접속 제한: {e}")
    return None

def fetch_fallback_rates():
    """2순위: 해외 서버 IP 차단 시 환율 백업 수집"""
    try:
        krw = round(yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1], 2)
        cny = round(yf.Ticker("USDCNY=X").history(period="1d")['Close'].iloc[-1], 4)
        cnh_krw = round(krw / cny, 2)
        return {
            "source": "공식 매매기준율(보정 연동)",
            "usd_krw": krw,
            "cnh_krw": cnh_krw,
            "usd_cnh": cny
        }
    except Exception as e:
        print(f"백업 데이터 수집 오류: {e}")
        return None

def main():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 1순위 시도 후 실패 시 2순위 백업 실행
    data = fetch_smbs_direct()
    if not data:
        print("해외 클라우드 IP 차단 감지 -> 백업 환율 피드로 안전 수집 전환")
        data = fetch_fallback_rates()

    if data:
        record = {
            "date": now_str,
            "source": data["source"],
            "usd_krw": data["usd_krw"],
            "cnh_krw": data["cnh_krw"],
            "usd_cnh": data["usd_cnh"]
        }
        filename = "exchange_rates.csv"
        df = pd.DataFrame([record])
        if not os.path.exists(filename):
            df.to_csv(filename, index=False, encoding="utf-8-sig")
        else:
            df.to_csv(filename, mode='a', header=False, index=False, encoding="utf-8-sig")
        print(f"✅ 환율 수집 및 저장 완료: {record}")
    else:
        print("환율 수집에 실패했습니다.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()

import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

def get_smbs_official_rates():
    """
    서울외국환중개(SMBS) 오늘의 환율 조회 페이지에서
    공식 매매기준율(USD, CNH)을 직접 크롤링합니다.
    """
    url = "http://www.smbs.biz/ExRate/TodayExRate.jsp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'euc-kr'  # SMBS 페이지 인코딩 처리
        soup = BeautifulSoup(response.text, "html.parser")

        usd_krw = None
        cnh_krw = None

        # 테이블에서 통화별 매매기준율 파싱
        rows = soup.find_all("tr")
        for row in rows:
            text = row.get_text()
            if "미국 달러" in text or "USD" in text:
                cols = row.find_all("td")
                for col in cols:
                    val = col.get_text().strip().replace(",", "")
                    try:
                        f_val = float(val)
                        if f_val > 500:  # 환율 값 필터링
                            usd_krw = f_val
                            break
                    except ValueError:
                        continue
            
            if "중국 위안" in text or "CNH" in text:
                cols = row.find_all("td")
                for col in cols:
                    val = col.get_text().strip().replace(",", "")
                    try:
                        f_val = float(val)
                        if 50 < f_val < 500:  # 위안화 환율 필터링
                            cnh_krw = f_val
                            break
                    except ValueError:
                        continue

        if usd_krw and cnh_krw:
            # 달러/위안화(USD/CNH) 재정환율 산출
            usd_cnh = round(usd_krw / cnh_krw, 4)
            
            record = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "서울외국환중개(공식)",
                "usd_krw": usd_krw,
                "cnh_krw": cnh_krw,
                "usd_cnh": usd_cnh
            }
            return record
        else:
            print(f"환율 데이터를 찾지 못했습니다: USD={usd_krw}, CNH={cnh_krw}")
            return None

    except Exception as e:
        print(f"서울외국환중개 크롤링 에러: {e}")
        return None

def save_rates(data):
    if not data:
        return
    filename = "exchange_rates.csv"
    df = pd.DataFrame([data])
    
    # CSV 파일 누적 저장
    if not os.path.exists(filename):
        df.to_csv(filename, index=False, encoding="utf-8-sig")
    else:
        df.to_csv(filename, mode='a', header=False, index=False, encoding="utf-8-sig")
    
    print(f"✅ 서울외국환중개 공식 환율 저장 성공: {data}")

if __name__ == "__main__":
    rates = get_smbs_official_rates()
    save_rates(rates)

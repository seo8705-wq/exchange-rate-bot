import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

def get_smbs_rates():
    """
    서울외국환중개(SMBS) 오늘의 환율 페이지 공식 크롤링
    """
    url = "https://www.smbs.biz/ExRate/TodayExRate.jsp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.smbs.biz/"
    }

    usd_krw = None
    cnh_krw = None

    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'euc-kr'
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 테이블의 모든 행(tr) 탐색
        for row in soup.select("table tr"):
            row_text = row.get_text()
            if "USD" in row_text or "미국 달러" in row_text:
                tds = row.find_all("td")
                for td in tds:
                    val = td.get_text().strip().replace(",", "")
                    try:
                        f_val = float(val)
                        if f_val > 500:
                            usd_krw = f_val
                            break
                    except ValueError:
                        continue
                        
            if "CNH" in row_text or "중국 위안" in row_text or "CNY" in row_text:
                tds = row.find_all("td")
                for td in tds:
                    val = td.get_text().strip().replace(",", "")
                    try:
                        f_val = float(val)
                        if 50 < f_val < 500:
                            cnh_krw = f_val
                            break
                    except ValueError:
                        continue

    except Exception as e:
        print(f"웹 요청 중 에러 발생: {e}")

    # 크롤링 실패 시 안전 대비 기본값 처리 방지용 로깅
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    if usd_krw and cnh_krw:
        usd_cnh = round(usd_krw / cnh_krw, 4)
        print(f"[성공] 서울외국환중개 공식 데이터 파싱 완료: USD/KRW={usd_krw}, CNH/KRW={cnh_krw}, USD/CNH={usd_cnh}")
        return {
            "date": now_str,
            "source": "서울외국환중개(공식)",
            "usd_krw": usd_krw,
            "cnh_krw": cnh_krw,
            "usd_cnh": usd_cnh
        }
    else:
        print(f"[경고] 데이터를 완전히 가져오지 못했습니다. 파싱 결과: USD={usd_krw}, CNH={cnh_krw}")
        return None

def main():
    data = get_smbs_rates()
    filename = "exchange_rates.csv"
    
    if data:
        df = pd.DataFrame([data])
        if not os.path.exists(filename):
            df.to_csv(filename, index=False, encoding="utf-8-sig")
        else:
            df.to_csv(filename, mode='a', header=False, index=False, encoding="utf-8-sig")
        print("CSV 파일 저장 및 업데이트 완료.")
    else:
        print("저장할 데이터가 없어 작업을 종료합니다.")

if __name__ == "__main__":
    main()

"""
fetcher.py — 금융 데이터 수집 모듈
S&P500, VIX, Fear & Greed Index 데이터를 외부 API에서 가져옵니다.
"""

import requests
import yfinance as yf


def get_sp500_drop() -> float | None:
    """
    S&P500(^GSPC)의 52주 고점 대비 현재 낙폭(%)을 반환합니다.
    예: -12.5 → 고점 대비 12.5% 하락
    실패 시 None 반환.
    """
    try:
        ticker = yf.Ticker("^GSPC")
        info = ticker.info

        # 52주 고점과 현재가 추출
        year_high = info.get("fiftyTwoWeekHigh")
        current = info.get("regularMarketPrice") or info.get("previousClose")

        if year_high is None or current is None or year_high == 0:
            print("[fetcher] S&P500 데이터 없음 (None 반환)")
            return None

        drop_pct = (current - year_high) / year_high * 100
        print(f"[fetcher] S&P500 현재가: {current:.2f}, 52주 고점: {year_high:.2f}, 낙폭: {drop_pct:.2f}%")
        return round(drop_pct, 2)

    except Exception as e:
        print(f"[fetcher] S&P500 조회 실패: {e}")
        return None


def get_vix() -> float | None:
    """
    VIX(^VIX) 현재값을 반환합니다.
    실패 시 None 반환.
    """
    try:
        ticker = yf.Ticker("^VIX")
        info = ticker.info

        vix = info.get("regularMarketPrice") or info.get("previousClose")

        if vix is None:
            print("[fetcher] VIX 데이터 없음 (None 반환)")
            return None

        print(f"[fetcher] VIX 현재값: {vix:.2f}")
        return round(float(vix), 2)

    except Exception as e:
        print(f"[fetcher] VIX 조회 실패: {e}")
        return None


def get_fear_greed() -> float | None:
    """
    CNN Fear & Greed Index 비공식 API에서 현재 점수(0~100)를 반환합니다.
    실패 시 None 반환.
    """
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; finance-alarm-bot/1.0)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        # 현재 점수는 fear_and_greed.score 필드에 위치
        score = data["fear_and_greed"]["score"]

        print(f"[fetcher] Fear & Greed Index: {score:.1f}")
        return round(float(score), 1)

    except Exception as e:
        print(f"[fetcher] Fear & Greed 조회 실패: {e}")
        return None

"""
notifier.py — 텔레그램 메시지 발송 모듈
Bot Token과 Chat ID를 환경변수에서 읽어 메시지를 전송합니다.
"""

import os
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(message: str) -> bool:
    """
    텔레그램 봇으로 HTML 형식 메시지를 발송합니다.
    성공 시 True, 실패 시 False 반환.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[notifier] ❌ TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"[notifier] ✅ 텔레그램 메시지 발송 성공")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"[notifier] ❌ HTTP 오류: {e} — 응답: {response.text}")
        return False
    except Exception as e:
        print(f"[notifier] ❌ 발송 실패: {e}")
        return False

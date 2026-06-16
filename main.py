"""
main.py — 금융 지수 텔레그램 알람 시스템 진입점
APScheduler를 사용해 주기적으로 금융 지표를 확인하고 알람을 발송합니다.
"""

import sys
import os
import yaml
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

# src/ 디렉터리를 모듈 탐색 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# 환경변수 로드 (.env 파일)
load_dotenv()

from checker import check_all  # noqa: E402 (경로 설정 후 임포트)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "conditions.yaml")


def load_interval() -> int:
    """YAML 설정에서 폴링 간격(분)을 읽어옵니다."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("schedule", {}).get("interval_minutes", 30)


def main():
    interval = load_interval()
    print("=" * 50)
    print("  💹 금융 지수 텔레그램 알람 시스템 시작")
    print(f"  ⏱  폴링 간격: {interval}분")
    print("=" * 50)

    # 시작 즉시 1회 실행
    print("\n[main] 초기 실행...")
    check_all()

    # 스케줄러 설정 및 시작
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(check_all, "interval", minutes=interval)

    print(f"[main] 스케줄러 시작 — {interval}분마다 반복 실행 (종료: Ctrl+C)\n")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[main] 알람 시스템 종료")


if __name__ == "__main__":
    main()

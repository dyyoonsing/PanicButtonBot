"""
state.py — 알람 쿨다운 상태 관리 모듈
마지막 알람 발송 시각을 JSON 파일에 저장하여 중복 알람을 방지합니다.
"""

import json
import os
from datetime import datetime, timezone

# 상태 파일 경로 (프로젝트 루트 기준)
STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "state.json")


def _load_state() -> dict:
    """JSON 파일에서 상태를 불러옵니다. 파일이 없으면 빈 dict 반환."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[state] 상태 파일 읽기 실패, 초기화: {e}")
        return {}


def _save_state(state: dict) -> None:
    """상태를 JSON 파일에 저장합니다."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def can_alert(key: str, cooldown_hours: float) -> bool:
    """
    해당 key의 알람을 발송해도 되는지 확인합니다.
    마지막 알람 이후 cooldown_hours가 지났으면 True 반환.
    """
    state = _load_state()
    last_alerted_str = state.get(key)

    if last_alerted_str is None:
        # 한 번도 알람이 발송된 적 없으면 허용
        return True

    last_alerted = datetime.fromisoformat(last_alerted_str)
    now = datetime.now(timezone.utc)
    elapsed_hours = (now - last_alerted).total_seconds() / 3600

    if elapsed_hours >= cooldown_hours:
        print(f"[state] {key} 쿨다운 종료 ({elapsed_hours:.1f}h 경과, 기준 {cooldown_hours}h)")
        return True
    else:
        remaining = cooldown_hours - elapsed_hours
        print(f"[state] {key} 쿨다운 중 (잔여 {remaining:.1f}h)")
        return False


def mark_alerted(key: str) -> None:
    """해당 key의 마지막 알람 시각을 현재 시각으로 기록합니다."""
    state = _load_state()
    state[key] = datetime.now(timezone.utc).isoformat()
    _save_state(state)
    print(f"[state] {key} 알람 시각 기록 완료")

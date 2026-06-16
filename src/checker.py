"""
checker_test.py — 테스트용 조건 판단 모듈
조건·쿨다운을 무시하고 값이 존재하면 무조건 텔레그램 알람을 발송합니다.
실제 운영 시에는 checker.py를 사용하세요.

사용법: main.py 상단의 import를 아래와 같이 변경
  from checker_test import check_all
"""

import os
import yaml
from datetime import datetime, timezone

from fetcher import get_sp500_drop, get_vix, get_fear_greed
from notifier import send_telegram

# 설정 파일 경로
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "conditions.yaml")


def _load_config() -> dict:
    """YAML 설정 파일을 로드합니다."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _format_message(indicator_name: str, current_value: float, threshold: float) -> str:
    """텔레그램으로 발송할 HTML 포맷 메시지를 생성합니다."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    labels = {
        "sp500":      ("🧪 [테스트] S&P500", f"{current_value:.2f}%",    f"{threshold:.1f}% 이하 낙폭"),
        "vix":        ("🧪 [테스트] VIX",    f"{current_value:.2f}",     f"{threshold:.1f} 이상"),
        "fear_greed": ("🧪 [테스트] Fear & Greed", f"{current_value:.1f} / 100", f"{threshold:.0f} 이하"),
    }

    title, val_str, cond_str = labels.get(indicator_name, (indicator_name, str(current_value), str(threshold)))

    message = (
        f"<b>{title}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"📊 현재값: <b>{val_str}</b>\n"
        f"🎯 알람 조건 (미적용): {cond_str}\n"
        f"🕐 확인 시각: {now_str}\n"
        f"━━━━━━━━━━━━━━\n"
        f"<i>finance-alarm-bot · 테스트 모드</i>"
    )
    return message


def check_all() -> None:
    """
    모든 지표를 순차적으로 확인합니다.
    조건·쿨다운을 무시하고 값이 있으면 무조건 알람을 발송합니다.
    """
    print(f"\n{'='*40}")
    print(f"[checker_test] ⚠️  테스트 모드 — 조건·쿨다운 무시")
    print(f"[checker_test] 지표 확인 시작: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*40}")

    config = _load_config()
    indicators = config.get("indicators", {})

    # ── S&P500 ──────────────────────────────
    sp_cfg = indicators.get("sp500", {})
    if sp_cfg.get("enabled", False):
        value = get_sp500_drop()
        if value is not None:
            print(f"[checker_test] S&P500 값 수신: {value:.2f}% → 무조건 알람 발송")
            msg = _format_message("sp500", value, sp_cfg["threshold"])
            send_telegram(msg)
        else:
            print("[checker_test] S&P500 데이터 없음 (None) — 알람 스킵")

    # ── VIX ─────────────────────────────────
    vix_cfg = indicators.get("vix", {})
    if vix_cfg.get("enabled", False):
        value = get_vix()
        if value is not None:
            print(f"[checker_test] VIX 값 수신: {value:.2f} → 무조건 알람 발송")
            msg = _format_message("vix", value, vix_cfg["threshold"])
            send_telegram(msg)
        else:
            print("[checker_test] VIX 데이터 없음 (None) — 알람 스킵")

    # ── Fear & Greed ─────────────────────────
    fg_cfg = indicators.get("fear_greed", {})
    if fg_cfg.get("enabled", False):
        value = get_fear_greed()
        if value is not None:
            print(f"[checker_test] Fear & Greed 값 수신: {value:.1f} → 무조건 알람 발송")
            msg = _format_message("fear_greed", value, fg_cfg["threshold"])
            send_telegram(msg)
        else:
            print("[checker_test] Fear & Greed 데이터 없음 (None) — 알람 스킵")

    print(f"[checker_test] 확인 완료\n")

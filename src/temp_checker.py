"""
checker.py — 조건 판단 및 알람 트리거 모듈
YAML 설정을 읽고 각 지표를 fetch한 뒤 조건을 판단하여 텔레그램 알람을 발송합니다.
"""

import os
import yaml
from datetime import datetime, timezone

from fetcher import get_sp500_drop, get_vix, get_fear_greed
from state import can_alert, mark_alerted
from notifier import send_telegram

# 설정 파일 경로
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "conditions.yaml")


def _load_config() -> dict:
    """YAML 설정 파일을 로드합니다."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _format_message(indicator_name: str, current_value: float, condition: str, threshold: float) -> str:
    """텔레그램으로 발송할 HTML 포맷 메시지를 생성합니다."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # 지표별 한국어 이름 및 단위
    labels = {
        "sp500": ("📉 S&P500 급락 경보", f"{current_value:.2f}%", f"{threshold:.1f}% 이하 낙폭"),
        "vix":   ("⚠️ VIX 급등 경보",   f"{current_value:.2f}", f"{threshold:.1f} 이상"),
        "fear_greed": ("😱 Fear & Greed 극단적 공포", f"{current_value:.1f} / 100", f"{threshold:.0f} 이하"),
    }

    title, val_str, cond_str = labels.get(indicator_name, (indicator_name, str(current_value), str(threshold)))

    message = (
        f"<b>{title}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"📊 현재값: <b>{val_str}</b>\n"
        f"🎯 알람 조건: {cond_str}\n"
        f"🕐 확인 시각: {now_str}\n"
        f"━━━━━━━━━━━━━━\n"
        f"<i>finance-alarm-bot</i>"
    )
    return message


def check_all() -> None:
    """
    모든 지표를 순차적으로 확인하고,
    조건 충족 + 쿨다운 만료 시 텔레그램 알람을 발송합니다.
    """
    print(f"\n{'='*40}")
    print(f"[checker] 지표 확인 시작: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*40}")

    config = _load_config()
    indicators = config.get("indicators", {})

    # ── S&P500 ──────────────────────────────
    sp_cfg = indicators.get("sp500", {})
    if sp_cfg.get("enabled", False):
        value = get_sp500_drop()
        threshold = sp_cfg["threshold"]
        cooldown = sp_cfg["cooldown_hours"]

        if value is not None and value <= threshold:
            print(f"[checker] S&P500 조건 충족: {value:.2f}% <= {threshold}%")
            if can_alert("sp500", cooldown):
                msg = _format_message("sp500", value, sp_cfg["condition"], threshold)
                if send_telegram(msg):
                    mark_alerted("sp500")
        else:
            print(f"[checker] S&P500 조건 미충족 (현재: {value}%)")

    # ── VIX ─────────────────────────────────
    vix_cfg = indicators.get("vix", {})
    if vix_cfg.get("enabled", False):
        value = get_vix()
        threshold = vix_cfg["threshold"]
        cooldown = vix_cfg["cooldown_hours"]

        if value is not None and value >= threshold:
            print(f"[checker] VIX 조건 충족: {value:.2f} >= {threshold}")
            if can_alert("vix", cooldown):
                msg = _format_message("vix", value, vix_cfg["condition"], threshold)
                if send_telegram(msg):
                    mark_alerted("vix")
        else:
            print(f"[checker] VIX 조건 미충족 (현재: {value})")

    # ── Fear & Greed ─────────────────────────
    fg_cfg = indicators.get("fear_greed", {})
    if fg_cfg.get("enabled", False):
        value = get_fear_greed()
        threshold = fg_cfg["threshold"]
        cooldown = fg_cfg["cooldown_hours"]

        if value is not None and value <= threshold:
            print(f"[checker] Fear & Greed 조건 충족: {value:.1f} <= {threshold}")
            if can_alert("fear_greed", cooldown):
                msg = _format_message("fear_greed", value, fg_cfg["condition"], threshold)
                if send_telegram(msg):
                    mark_alerted("fear_greed")
        else:
            print(f"[checker] Fear & Greed 조건 미충족 (현재: {value})")

    print(f"[checker] 확인 완료\n")

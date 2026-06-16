# 💹 금융 지수 텔레그램 알람 시스템

S&P500 급락, VIX 급등, Fear & Greed Index 극단적 공포 구간 진입 시  
텔레그램 봇으로 자동 알람을 발송하는 Python 스크립트입니다.

---

## 📋 알람 조건

| 지표 | 조건 | 쿨다운 |
|------|------|--------|
| S&P500 | 52주 고점 대비 **-10% 이하** | 24시간 |
| VIX | **25 이상** | 6시간 |
| Fear & Greed Index | **25 이하** | 12시간 |

> 임계값은 코드 수정 없이 `config/conditions.yaml`에서 변경 가능합니다.

---

## 🗂 프로젝트 구조

```
finance-alarm/
├── main.py                  # 진입점, APScheduler 루프
├── requirements.txt
├── .env.example             # 환경변수 양식
├── .gitignore
├── config/
│   └── conditions.yaml      # 임계값·스케줄 설정
├── src/
│   ├── fetcher.py           # 데이터 수집 (yfinance, CNN API)
│   ├── checker.py           # 조건 판단 + 알람 트리거
│   ├── notifier.py          # 텔레그램 메시지 발송
│   └── state.py             # 쿨다운 상태 저장/조회
└── data/                    # state.json 자동 생성
```

---

## 🤖 텔레그램 봇 설정 방법

### 1단계 — 봇 생성

1. 텔레그램에서 **[@BotFather](https://t.me/BotFather)** 를 검색하여 대화 시작
2. `/newbot` 명령어 입력
3. 봇 이름과 사용자명(username, `_bot`으로 끝나야 함) 입력
4. 생성 완료 후 **Bot Token** 수령 (예: `1234567890:ABCdefGHI...`)

### 2단계 — Chat ID 확인

**개인 채팅인 경우:**
1. 생성한 봇에게 아무 메시지나 전송
2. 아래 URL을 브라우저에서 열기 (토큰 교체):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. 응답 JSON에서 `result[0].message.chat.id` 값이 Chat ID

**그룹 채팅인 경우:**
1. 봇을 그룹에 초대한 뒤 아무 메시지 전송
2. 동일한 `getUpdates` URL로 조회
3. Chat ID는 음수(예: `-1001234567890`)로 표시됨

---

## ⚙️ 설치 및 실행

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
```

`.env` 파일을 열어 발급받은 값을 입력합니다:
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_CHAT_ID=987654321
```

```bash
# 4. 실행
python main.py
```

---

## 🔧 설정 변경

`config/conditions.yaml`에서 임계값, 쿨다운, 폴링 간격을 변경할 수 있습니다:

```yaml
indicators:
  sp500:
    enabled: true
    threshold: -10.0       # -15.0으로 변경 시 15% 하락부터 알람
    cooldown_hours: 24

  vix:
    enabled: true
    threshold: 25.0        # 30.0으로 변경 시 VIX 30 이상부터 알람
    cooldown_hours: 6

  fear_greed:
    enabled: false         # false로 설정 시 해당 지표 알람 비활성화
    threshold: 25.0
    cooldown_hours: 12

schedule:
  interval_minutes: 30     # 60으로 변경 시 1시간 간격 폴링
```

---

## 📨 알람 메시지 예시

```
📉 S&P500 급락 경보
━━━━━━━━━━━━━━
📊 현재값: -11.34%
🎯 알람 조건: -10.0% 이하 낙폭
🕐 확인 시각: 2025-08-01 09:30 UTC
━━━━━━━━━━━━━━
finance-alarm-bot
```

---

## 🛠 데이터 소스

| 지표 | 소스 | 방식 |
|------|------|------|
| S&P500, VIX | Yahoo Finance | `yfinance` 라이브러리 |
| Fear & Greed | CNN Markets | 비공식 JSON API |

> CNN Fear & Greed API는 비공식 엔드포인트이므로 구조가 변경될 수 있습니다.  
> 장애 발생 시 `src/fetcher.py`의 `get_fear_greed()` 함수를 수정하세요.

---

## ❓ 자주 묻는 질문

**Q. 알람이 오지 않아요.**  
A. `.env` 파일의 토큰과 Chat ID를 확인하세요. `getUpdates` API로 봇이 정상 작동하는지 먼저 테스트하세요.

**Q. 쿨다운을 초기화하고 싶어요.**  
A. `data/state.json` 파일을 삭제하면 모든 쿨다운이 초기화됩니다.

**Q. 서버에서 24시간 실행하고 싶어요.**  
A. `nohup python main.py &` 또는 `systemd` 서비스로 등록하거나, `screen` / `tmux` 세션 안에서 실행하세요.

# Trend Following MCP Server

추세추종 투자 방법론을 기반으로 한 MCP(Model Context Protocol) 서버입니다. 주식 시장 분석, 매매 시점 판단, 포트폴리오 관리를 위한 종합적인 투자 도구를 제공합니다.

---

## 🌟 프로젝트 개요

Trend Following MCP Server는 다음과 같은 핵심 기능을 제공합니다:

- 📈 **주식 정보 수집**: 실시간 주가, 재무제표, 뉴스 데이터
- 📊 **기술적 분석**: 이동평균, RSI, MACD, 볼린저 밴드 등
- 🎯 **매매 시점 신호**: 추세 추종 전략 기반 매수/매도 시점 판단
- 📋 **포트폴리오 관리**: 자산 배분, 리스크 관리, 성과 추적
- 🤖 **AI 기반 분석**: 머신러닝을 활용한 시장 예측 및 최적화

---

## 🚀 주요 기능

### 1. 주식 정보 도구 (Stock Information Tools)
- **`get_stock_info`**: 실시간 주가 데이터 수집 및 기업 정보 조회
- **`screen_stocks`**: 기술적/기본적 조건에 따른 주식 스크리닝
- 기업 재무제표 분석 (손익계산서, 재무상태표, 현금흐름표)
- 뉴스 및 이벤트 모니터링
- 섹터별 시장 동향 분석

### 2. 기술적 분석 도구 (Technical Analysis Tools)
- **`analyze_technical`**: 종합적인 기술적 분석 수행
- 이동평균선 분석 (20일, 50일, 200일 SMA/EMA)
- 모멘텀 지표 (RSI, MACD, 스토캐스틱)
- 변동성 지표 (볼린저 밴드, ATR)
- 거래량 분석 (OBV, 거래량 가중 평균)
- 추세 방향 및 강도 분석

### 3. 매매 신호 도구 (Trading Signal Tools)
- **`generate_signal`**: 추세 추종 매매 시점 판단
- **`backtest_signals`**: 전략 백테스팅 및 성과 분석
- 리스크 관리 및 손절매 설정
- 포지션 사이징 최적화
- 신호 신뢰도 및 강도 계산

### 4. 포트폴리오 관리 도구 (Portfolio Management Tools)
- **`manage_portfolio`**: 포트폴리오 분석, 최적화, 리밸런싱
- **`analyze_risk`**: 포트폴리오 리스크 분석 (VaR, CVaR)
- 자산 배분 최적화
- 리스크 대비 수익률 분석
- 성과 추적 및 리포팅

---

## 🏗️ 프로젝트 구조

```
TradeMonster/
├── src/
│   ├── mcp/                    # MCP 서버 핵심
│   │   ├── server.py          # MCP 서버 메인
│   │   ├── schemas.py         # 데이터 스키마 (Pydantic 모델)
│   │   └── tools/             # MCP 도구들
│   │       ├── stock_info.py  # 주식 정보 도구
│   │       ├── technical.py   # 기술적 분석 도구
│   │       ├── signals.py     # 매매 신호 도구
│   │       └── portfolio.py   # 포트폴리오 관리 도구
│   ├── analysis/              # 분석 엔진
│   │   ├── trend_analysis.py  # 추세 분석 엔진
│   │   ├── momentum.py        # 모멘텀 분석 (구현 예정)
│   │   └── volatility.py      # 변동성 분석 (구현 예정)
│   ├── utils/                 # 유틸리티
│   │   ├── config.py          # 설정 관리 (Pydantic 기반)
│   │   └── logger.py          # 로깅 시스템
│   └── main.py                # 메인 실행 파일
├── tests/                     # 테스트 파일들
│   └── test_mcp_server.py     # MCP 서버 테스트
├── pyproject.toml             # 프로젝트 설정 (업데이트됨)
├── README.md                  # 프로젝트 문서
├── env.example                # 환경 변수 예시
└── LICENSE                    # MIT 라이선스
```

---

## 📊 추세추종 전략

### 핵심 원칙
1. **추세 확인**: 장기 이동평균선을 기준으로 상승/하락 추세 판단
2. **모멘텀 활용**: RSI, MACD 등 모멘텀 지표로 강도 측정
3. **변동성 관리**: 볼린저 밴드, ATR로 변동성 기반 진입/청산
4. **리스크 제어**: 손절매, 익절매, 포지션 사이징으로 리스크 관리

### 매매 시점 판단
- **매수 조건**: 상승 추세 + 모멘텀 상승 + 변동성 확대
- **매도 조건**: 하락 추세 + 모멘텀 하락 + 지지선 이탈
- **홀딩 조건**: 추세 지속 + 리스크 관리 범위 내

### 구현된 신호 로직
```python
# 강력한 매수 신호
if (trend_direction == "up" and 
    current_price > sma_20 > sma_50 > sma_200 and
    rsi < 70 and  # 과매수 아님
    macd > macd_signal and
    price_position < 0.8):  # 볼린저 상단 밴드 이하
    signal_type = "strong_buy"
```

---

## 🛠️ 설치 및 실행

### 1. 환경 설정
```bash
# 저장소 클론
git clone https://github.com/yourusername/TradeMonster.git
cd TradeMonster

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -e .
```

### 2. 환경 변수 설정
```bash
# .env 파일 생성
cp env.example .env

# API 키 설정 (선택사항 - yfinance는 기본적으로 API 키가 필요 없음)
YAHOO_FINANCE_API_KEY=your_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
```

### 3. MCP 서버 실행
```bash
# 메인 실행 파일로 실행
python src/main.py

# 또는 직접 MCP 서버 실행
python -m src.mcp.server --dev

# 또는 개발 모드
python -m src.mcp.server --dev --stdio
```

### 4. 테스트 실행
```bash
# 전체 테스트 실행
pytest tests/

# 특정 테스트 실행
pytest tests/test_mcp_server.py -v
```

---

## 📈 사용 예시

### 1. 주식 정보 조회
```python
# Apple 주식 정보 조회
stock_info = await session.call_tool("get_stock_info", {
    "symbol": "AAPL",
    "include_financials": True,
    "include_news": True
})
```

### 2. 기술적 분석
```python
# 기술적 지표 분석
analysis = await session.call_tool("analyze_technical", {
    "symbol": "AAPL",
    "period": "1y",
    "indicators": ["sma", "rsi", "macd", "bollinger"]
})
```

### 3. 매매 신호 생성
```python
# 추세추종 매매 신호
signal = await session.call_tool("generate_signal", {
    "symbol": "AAPL",
    "strategy": "trend_following",
    "risk_level": "moderate"
})
```

### 4. 포트폴리오 분석
```python
# 포트폴리오 분석
portfolio = await session.call_tool("manage_portfolio", {
    "action": "analyze",
    "portfolio": [
        {"symbol": "AAPL", "shares": 100, "cost_basis": 150.0},
        {"symbol": "GOOGL", "shares": 50, "cost_basis": 2800.0}
    ]
})
```

### 5. 리스크 분석
```python
# 포트폴리오 리스크 분석
risk_analysis = await session.call_tool("analyze_risk", {
    "portfolio": portfolio_data,
    "confidence_level": 0.95
})
```

---

## 🔧 개발 가이드

### 새로운 도구 추가
```python
# src/mcp/tools/new_tool.py
from mcp import Tool
from typing import Dict, Any

class NewTool(Tool):
    name = "new_tool"
    description = "새로운 도구 설명"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # 도구 로직 구현
        return {"result": "success"}
```

### 설정 관리
```python
# src/utils/config.py에서 설정 추가
class Config(BaseSettings):
    new_setting: str = Field(default="default_value", description="새로운 설정")
```

### 로깅 사용
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("정보 메시지")
logger.error("에러 메시지")
```

---

## 📊 성과 지표

- **승률**: 65% 이상 목표
- **샤프 비율**: 1.5 이상 목표
- **최대 낙폭**: 15% 이하 목표
- **연간 수익률**: 20% 이상 목표

---

## 🛡️ 리스크 관리

### 구현된 리스크 관리 기능
- **ATR 기반 손절매**: 변동성에 따른 동적 손절매 설정
- **포지션 사이징**: 신뢰도와 리스크 수준에 따른 포지션 크기 조절
- **포트폴리오 다각화**: 자산 간 상관관계를 고려한 배분
- **VaR/CVaR 분석**: 포트폴리오 리스크 측정

### 리스크 수준별 설정
```python
# 보수적 (Conservative)
stop_loss_multiplier = 2.0
position_size = 0.05  # 5%

# 중간 (Moderate) - 기본값
stop_loss_multiplier = 1.5
position_size = 0.1   # 10%

# 공격적 (Aggressive)
stop_loss_multiplier = 1.0
position_size = 0.15  # 15%
```

---

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 개발 가이드라인
- Python 3.13+ 사용
- Type hints 필수
- Pydantic 모델 사용
- Async/await 패턴 사용
- 테스트 코드 작성

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## ⚠️ 면책 조항

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다. 실제 투자에 사용하기 전에 충분한 검증과 테스트를 거쳐야 합니다. 투자 손실에 대한 책임은 사용자에게 있습니다.

**중요**: 이 도구는 투자 조언이 아닙니다. 모든 투자 결정은 본인의 판단에 따라 이루어져야 합니다.

---

## 📞 문의

프로젝트에 대한 문의사항이나 제안사항이 있으시면 이슈를 생성해 주세요.

**함께 더 나은 투자 도구를 만들어가요! 🚀**


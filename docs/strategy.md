# 추세추종 투자 방법론 (Trend Following Strategy)

## 📖 개요

추세추종 투자 방법론은 시장의 방향성을 따라가는 투자 전략입니다. "추세는 당신의 친구다(Trend is your friend)"라는 유명한 격언처럼, 이미 형성된 추세를 인식하고 그 방향으로 투자하는 방법입니다.

### 핵심 철학
- **시장의 방향성을 인정**: 시장이 상승하면 매수, 하락하면 매도
- **모멘텀 활용**: 이미 움직이고 있는 방향으로 추가 모멘텀을 얻음
- **시장의 지혜 신뢰**: 개별 투자자의 판단보다 시장 전체의 움직임을 신뢰

---

## 🎯 추세추종의 기본 원리

### 1. 추세의 정의
추세는 일정 기간 동안 지속되는 가격의 방향성을 의미합니다.

```
상승 추세: 고점과 저점이 모두 상승하는 패턴
하락 추세: 고점과 저점이 모두 하락하는 패턴
횡보 추세: 명확한 방향성이 없는 패턴
```

### 2. 추세의 세 가지 방향
- **주요 추세 (Primary Trend)**: 1년 이상 지속되는 장기 추세
- **중기 추세 (Intermediate Trend)**: 3주~6개월 지속되는 중기 추세  
- **단기 추세 (Minor Trend)**: 1~3주 지속되는 단기 추세

---

## 📊 추세 확인 방법

### 1. 이동평균선 분석

#### 단순이동평균 (SMA)
```python
# 추세 확인을 위한 이동평균선
SMA_20 = 20일 이동평균선 (단기 추세)
SMA_50 = 50일 이동평균선 (중기 추세)
SMA_200 = 200일 이동평균선 (장기 추세)
```

#### 추세 판단 기준
- **강한 상승 추세**: 가격 > SMA_20 > SMA_50 > SMA_200
- **약한 상승 추세**: 가격 > SMA_50 > SMA_200
- **강한 하락 추세**: 가격 < SMA_20 < SMA_50 < SMA_200
- **약한 하락 추세**: 가격 < SMA_50 < SMA_200
- **횡보 추세**: 이동평균선들이 교차하거나 평행한 상태

### 2. 추세선 분석

#### 상승 추세선
- 연속된 저점들을 연결한 직선
- 추세선 위에서 매수, 아래에서 매도

#### 하락 추세선
- 연속된 고점들을 연결한 직선
- 추세선 아래에서 매도, 위에서 매수

### 3. 지지선과 저항선

#### 지지선 (Support)
- 가격이 하락할 때 지지받는 수준
- 과거 저점들이 형성된 가격대

#### 저항선 (Resistance)
- 가격이 상승할 때 저항받는 수준
- 과거 고점들이 형성된 가격대

---

## 🚀 매수 신호 (Buy Signals)

### 1. 강한 매수 신호 (Strong Buy)

#### 조건
```python
# 강한 매수 신호 조건
if (trend_direction == "up" and 
    current_price > sma_20 > sma_50 > sma_200 and
    rsi < 70 and  # 과매수 상태가 아님
    macd > macd_signal and  # MACD 상승 신호
    volume > volume_sma and  # 거래량 증가
    price_position < 0.8):  # 볼린저 밴드 상단 이하
    signal = "strong_buy"
```

#### 특징
- **신뢰도**: 85% 이상
- **포지션 크기**: 기본 포지션의 100-120%
- **손절매**: ATR × 1.0 (공격적)
- **익절매**: ATR × 2.0 (2:1 비율)

### 2. 일반 매수 신호 (Buy)

#### 조건
```python
# 일반 매수 신호 조건
if (trend_direction == "up" and
    current_price > sma_50 and
    rsi < 75 and
    macd > macd_signal):
    signal = "buy"
```

#### 특징
- **신뢰도**: 70-85%
- **포지션 크기**: 기본 포지션의 80-100%
- **손절매**: ATR × 1.5 (보통)
- **익절매**: ATR × 2.0 (2:1 비율)

### 3. 추세 추종 매수 (Trend Following Buy)

#### 조건
```python
# 추세 추종 매수 조건
if (price_breaks_above_resistance and
    volume_confirms_breakout and
    trend_strength > 60):
    signal = "trend_following_buy"
```

#### 특징
- **돌파 매수**: 저항선 돌파 시 매수
- **거래량 확인**: 돌파 시 거래량 증가 필수
- **재진입**: 추세 지속 시 추가 매수

---

## 📉 매도 신호 (Sell Signals)

### 1. 강한 매도 신호 (Strong Sell)

#### 조건
```python
# 강한 매도 신호 조건
if (trend_direction == "down" and
    current_price < sma_20 < sma_50 < sma_200 and
    rsi > 30 and  # 과매도 상태가 아님
    macd < macd_signal and  # MACD 하락 신호
    volume > volume_sma and  # 거래량 증가
    price_position > 0.2):  # 볼린저 밴드 하단 이상
    signal = "strong_sell"
```

#### 특징
- **신뢰도**: 85% 이상
- **청산 비율**: 보유 포지션의 100%
- **손절매**: ATR × 1.0 (공격적)

### 2. 일반 매도 신호 (Sell)

#### 조건
```python
# 일반 매도 신호 조건
if (trend_direction == "down" and
    current_price < sma_50 and
    rsi > 25 and
    macd < macd_signal):
    signal = "sell"
```

#### 특징
- **신뢰도**: 70-85%
- **청산 비율**: 보유 포지션의 80-100%
- **손절매**: ATR × 1.5 (보통)

### 3. 추세 반전 매도 (Trend Reversal Sell)

#### 조건
```python
# 추세 반전 매도 조건
if (price_breaks_below_support and
    volume_confirms_breakdown and
    trend_strength < 40):
    signal = "trend_reversal_sell"
```

#### 특징
- **지지선 이탈**: 지지선 하향 돌파 시 매도
- **거래량 확인**: 이탈 시 거래량 증가 필수
- **전량 매도**: 추세 반전 시 즉시 전량 매도

---

## 📈 추세 추종 전략

### 1. 피라미딩 (Pyramiding)

#### 개념
추세가 지속될 때 추가 매수를 통해 포지션을 확대하는 전략

#### 실행 방법
```python
# 피라미딩 조건
if (current_position > 0 and
    trend_strength_increases and
    price_makes_new_high and
    risk_management_allows):
    
    # 추가 매수 계산
    additional_position = base_position * 0.5  # 기본 포지션의 50%
    new_stop_loss = current_price - (atr * 1.5)
    
    # 추가 매수 실행
    execute_buy(additional_position)
    update_stop_loss(new_stop_loss)
```

#### 피라미딩 규칙
1. **기본 포지션 확립**: 첫 번째 매수로 기본 포지션 확립
2. **추세 확인**: 추세가 강화되는지 확인
3. **단계적 추가**: 25-50%씩 단계적으로 추가 매수
4. **리스크 관리**: 전체 포지션의 손절매 수준 조정

### 2. 트레일링 스탑 (Trailing Stop)

#### 개념
가격이 상승함에 따라 손절매 수준을 상향 조정하는 전략

#### 실행 방법
```python
# 트레일링 스탑 계산
def calculate_trailing_stop(current_price, atr, trailing_multiplier=2.0):
    trailing_stop = current_price - (atr * trailing_multiplier)
    return max(trailing_stop, current_stop_loss)  # 하향 조정 금지

# 트레일링 스탑 업데이트
if current_price > entry_price:
    new_stop_loss = calculate_trailing_stop(current_price, atr)
    if new_stop_loss > current_stop_loss:
        update_stop_loss(new_stop_loss)
```

#### 트레일링 스탑 규칙
1. **시작 조건**: 수익이 발생하기 시작하면 트레일링 스탑 활성화
2. **조정 주기**: 매일 또는 주요 변동 시 조정
3. **하향 조정 금지**: 손절매 수준은 절대 하향 조정하지 않음
4. **ATR 활용**: 변동성에 따른 동적 조정

### 3. 포지션 사이징 (Position Sizing)

#### 기본 포지션 크기 계산
```python
# 켈리 공식 기반 포지션 사이징
def calculate_position_size(win_rate, avg_win, avg_loss, account_size):
    kelly_percentage = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
    kelly_percentage = max(0, min(kelly_percentage, 0.25))  # 최대 25%로 제한
    
    position_size = account_size * kelly_percentage
    return position_size

# 리스크 기반 포지션 사이징
def calculate_risk_based_position(account_size, risk_per_trade, stop_loss_pips):
    risk_amount = account_size * risk_per_trade
    position_size = risk_amount / stop_loss_pips
    return position_size
```

#### 포지션 크기 조정 요소
1. **계좌 크기**: 전체 자산의 1-5% (단일 포지션)
2. **신호 강도**: 강한 신호일수록 큰 포지션
3. **변동성**: 변동성이 클수록 작은 포지션
4. **상관관계**: 상관관계가 높은 자산은 포지션 분산

---

## 🛡️ 리스크 관리

### 1. 손절매 전략

#### ATR 기반 손절매
```python
# ATR 기반 손절매 계산
def calculate_stop_loss(entry_price, atr, risk_level):
    multipliers = {
        "conservative": 2.0,
        "moderate": 1.5,
        "aggressive": 1.0
    }
    
    multiplier = multipliers[risk_level]
    stop_loss = entry_price - (atr * multiplier)
    return stop_loss
```

#### 시간 기반 손절매
```python
# 시간 기반 손절매
def time_based_stop_loss(entry_time, max_hold_days=30):
    current_time = datetime.now()
    days_held = (current_time - entry_time).days
    
    if days_held > max_hold_days:
        return "time_stop_loss"
    return None
```

### 2. 익절매 전략

#### 목표 수익률 기반
```python
# 목표 수익률 기반 익절매
def target_profit_exit(entry_price, target_percentage=0.20):
    target_price = entry_price * (1 + target_percentage)
    
    if current_price >= target_price:
        return "target_profit_exit"
    return None
```

#### 추세 반전 기반
```python
# 추세 반전 기반 익절매
def trend_reversal_exit(trend_strength, threshold=40):
    if trend_strength < threshold:
        return "trend_reversal_exit"
    return None
```

### 3. 포트폴리오 리스크 관리

#### 최대 손실 제한
```python
# 일일 최대 손실 제한
def daily_loss_limit(account_size, max_daily_loss=0.02):
    daily_loss = (initial_account - current_account) / initial_account
    
    if daily_loss > max_daily_loss:
        return "daily_loss_limit"
    return None
```

#### 최대 낙폭 제한
```python
# 최대 낙폭 제한
def max_drawdown_limit(peak_value, current_value, max_drawdown=0.15):
    drawdown = (peak_value - current_value) / peak_value
    
    if drawdown > max_drawdown:
        return "max_drawdown_limit"
    return None
```

---

## 📊 성과 측정

### 1. 주요 성과 지표

#### 승률 (Win Rate)
```python
win_rate = winning_trades / total_trades * 100
```

#### 수익률 (Return)
```python
total_return = (final_value - initial_value) / initial_value * 100
annualized_return = ((final_value / initial_value) ** (365 / days) - 1) * 100
```

#### 샤프 비율 (Sharpe Ratio)
```python
sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
```

#### 최대 낙폭 (Maximum Drawdown)
```python
max_drawdown = max((peak - current) / peak for peak in equity_curve)
```

### 2. 거래 통계

#### 평균 수익/손실
```python
avg_win = sum(winning_trades) / len(winning_trades)
avg_loss = sum(losing_trades) / len(losing_trades)
profit_factor = avg_win / avg_loss
```

#### 연속 승/패
```python
max_consecutive_wins = max_consecutive_sequence(winning_trades)
max_consecutive_losses = max_consecutive_sequence(losing_trades)
```

---

## 🎯 전략 최적화

### 1. 파라미터 최적화

#### 이동평균 기간 최적화
```python
# 이동평균 기간 최적화
def optimize_moving_averages(symbol, start_date, end_date):
    best_params = {}
    best_sharpe = -999
    
    for short_ma in range(10, 30, 5):
        for long_ma in range(50, 200, 10):
            if short_ma < long_ma:
                sharpe = backtest_strategy(symbol, short_ma, long_ma)
                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_params = {"short": short_ma, "long": long_ma}
    
    return best_params
```

#### RSI 기간 최적화
```python
# RSI 기간 최적화
def optimize_rsi_period(symbol, start_date, end_date):
    best_period = 14
    best_sharpe = -999
    
    for period in range(10, 25, 2):
        sharpe = backtest_rsi_strategy(symbol, period)
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_period = period
    
    return best_period
```

### 2. 시장 상황별 전략 조정

#### 강세장 전략
- 더 공격적인 포지션 사이징
- 더 긴 홀딩 기간
- 더 높은 목표 수익률

#### 약세장 전략
- 더 보수적인 포지션 사이징
- 더 짧은 홀딩 기간
- 더 낮은 목표 수익률

#### 횡보장 전략
- 범위 내 거래 (Range Trading)
- 더 작은 포지션 크기
- 빠른 익절매

---

## ⚠️ 주의사항

### 1. 추세추종의 한계
- **후행 지표**: 추세가 이미 형성된 후에 진입
- **횡보장 손실**: 횡보장에서는 잦은 손실 발생
- **추세 반전 위험**: 추세 반전 시 큰 손실 가능성

### 2. 심리적 요인
- **FOMO (Fear of Missing Out)**: 추세 추종 시 늦게 진입하는 두려움
- **손실 회복 욕구**: 손실 후 더 큰 포지션으로 복구하려는 유혹
- **과도한 자신감**: 연속 승리 후 과도한 포지션 확대

### 3. 시장 상황별 대응
- **고변동성 시장**: 더 보수적인 포지션 사이징
- **저변동성 시장**: 더 공격적인 포지션 사이징
- **뉴스 이벤트**: 주요 뉴스 발표 전 포지션 축소

---

## 📚 참고 자료

### 추천 도서
1. "추세추종 투자법" - 마이클 코벨
2. "시스템 트레이딩" - 커티스 페이스
3. "추세추종의 기술" - 알렉산더 엘더

### 주요 지표 공식
- **RSI**: 100 - (100 / (1 + RS)), RS = 평균 상승 / 평균 하락
- **MACD**: EMA(12) - EMA(26), Signal = EMA(9) of MACD
- **볼린저 밴드**: 중간선 = SMA(20), 상단 = 중간선 + 2×표준편차, 하단 = 중간선 - 2×표준편차
- **ATR**: True Range의 이동평균, True Range = max(고가-저가, |고가-전일종가|, |저가-전일종가|)

---

## 🎯 결론

추세추종 투자 방법론은 시장의 방향성을 활용하는 효과적인 전략입니다. 하지만 성공적인 추세추종을 위해서는:

1. **철저한 리스크 관리**가 필수적입니다
2. **일관된 전략 실행**이 중요합니다
3. **지속적인 모니터링과 조정**이 필요합니다
4. **심리적 훈련**이 동반되어야 합니다

이 문서의 내용을 바탕으로 본인의 투자 스타일에 맞는 추세추종 전략을 개발하고 실행하시기 바랍니다.

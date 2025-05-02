CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ETF 기본 정보
CREATE TABLE etf_sectors
(
    etf_id                  SERIAL PRIMARY KEY,
    symbol                  VARCHAR(10)  NOT NULL UNIQUE, -- ETF 심볼
    name                    VARCHAR(100) NOT NULL,        -- ETF 이름
    country                 VARCHAR(30),                  -- 국가
    sector                  VARCHAR(50),                  -- 섹터
    description             TEXT,                         -- ETF 설명
    expense_ratio           DECIMAL(5, 4),                -- 운용 보수 비율
    inception_date          DATE,                         -- 상장일
    assets_under_management DECIMAL(20, 2),               -- 운용 자산 규모
    last_updated            TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ETF 구성 종목 정보
CREATE TABLE etf_components
(
    component_id      SERIAL PRIMARY KEY,    -- 구성 종목 ID
    etf_id            INTEGER REFERENCES etf_sectors (etf_id),
    stock_symbol      VARCHAR(10)  NOT NULL, -- 종목 심볼
    stock_name        VARCHAR(100) NOT NULL, -- 종목 이름
    weight_percentage DECIMAL(7, 4),         -- 비중
    sector            VARCHAR(50),           -- 섹터
    industry          VARCHAR(50),           -- 산업군(섹터보다 디테일)
    last_updated      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 경제 지표 메타데이터
CREATE TABLE market_metadata
(
    indicator_id   SERIAL PRIMARY KEY,   -- 경제 지표 ID
    indicator_name VARCHAR(50) NOT NULL, -- 경제 지표 이름
    country        VARCHAR(30),          -- 국가
    source         VARCHAR(50) NOT NULL, -- 데이터 출처
    description    TEXT,                 -- 지표 설명
    last_updated   TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 경제 지표 시계열 데이터
CREATE TABLE market_timeseries
(
    indicator_id    INTEGER NOT NULL REFERENCES market_metadata (indicator_id),
    date            DATE    NOT NULL, -- 날짜
    indicator_value DECIMAL(20, 6),   -- 경제 지표 값
    last_updated    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (indicator_id, date)  -- date를 기본 키에 포함
);

-- 하이퍼테이블로 변환
SELECT create_hypertable('market_timeseries', 'date');

-- 가격 및 거래량 데이터 (시계열)
CREATE TABLE price_data
(
    symbol         VARCHAR(10) NOT NULL, -- 종목 심볼
    time           TIMESTAMPTZ NOT NULL, -- 시계열 데이터 시간
    open           DECIMAL(20, 6),       -- 시가
    high           DECIMAL(20, 6),       -- 고가
    low            DECIMAL(20, 6),       -- 저가
    close          DECIMAL(20, 6),       -- 종가
    adjusted_close DECIMAL(20, 6),       -- 수정 종가
    volume         BIGINT,               -- 거래량
    is_etf         BOOLEAN,              -- ETF 여부
    country        VARCHAR(30),          -- 국가
    PRIMARY KEY (symbol, time)           -- 종목 심볼과 시간으로 복합 기본 키 설정
);

-- 하이퍼테이블로 변환
SELECT create_hypertable('price_data', 'time');

-- 경기 사이클 정보
CREATE TABLE economic_cycle
(
    cycle_id     SERIAL PRIMARY KEY,
    start_date   DATE        NOT NULL, -- 경기 사이클 시작일
    end_date     DATE,                 -- 경기 사이클 종료일
    phase        VARCHAR(15) NOT NULL, -- '초기 회복', '초기 확장', '본격 확장', '과열기', '침체기'
    description  TEXT,
    confidence   DECIMAL(5, 2),        -- 모델 신뢰도
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 국면별 섹터 강세 매핑
CREATE TABLE sector_performance
(
    performance_id    SERIAL PRIMARY KEY,
    phase             VARCHAR(15) NOT NULL,                 -- 경기 사이클 단계
    sector            VARCHAR(50),                          -- 섹터
    country           VARCHAR(30) NOT NULL,                 -- 국가
    historical_return DECIMAL(8, 4),                        -- 역사적 수익률
    volatility        DECIMAL(8, 4),                        -- 변동성
    sharpe_ratio      DECIMAL(8, 4),                        -- 샤프 비율
    success_rate      DECIMAL(5, 2),                        -- 성공률
    last_updated      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP -- 마지막 업데이트 시간
);

-- 모델이 생성한 신호 기록
CREATE TABLE trading_signals
(
    signal_id       SERIAL,
    symbol          VARCHAR(10) NOT NULL, -- 종목 심볼
    time            TIMESTAMPTZ NOT NULL, -- 신호 발생 시간
    signal_type     VARCHAR(20) NOT NULL, -- 'BUY', 'SELL', 'HOLD'
    signal_strength DECIMAL(5, 2),        -- 신호 강도
    price           DECIMAL(20, 6),       -- 가격
    volume          BIGINT,               -- 거래량
    strategy_name   VARCHAR(50),          -- 전략 이름
    rationale       TEXT,                 -- 신호 발생 이유
    primary key (signal_id, time)         -- 신호 ID와 시간으로 복합 기본 키 설정
);

-- 하이퍼테이블로 변환
SELECT create_hypertable('trading_signals', 'time');

-- 백테스트 결과 저장
CREATE TABLE backtest_results
(
    backtest_id       SERIAL PRIMARY KEY,
    strategy_name     VARCHAR(50) NOT NULL, -- 전략 이름
    start_date        DATE        NOT NULL, -- 백테스트 시작일
    end_date          DATE        NOT NULL, -- 백테스트 종료일
    total_return      DECIMAL(10, 4),       -- 총 수익률
    annualized_return DECIMAL(10, 4),       -- 연환산 수익률
    sharpe_ratio      DECIMAL(8, 4),        -- 샤프 비율
    max_drawdown      DECIMAL(8, 4),        -- 최대 낙폭
    win_rate          DECIMAL(5, 2),        -- 승률
    parameters        JSONB,                -- 전략 파라미터
    execution_time    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
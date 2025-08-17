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
    indicator_id       SERIAL PRIMARY KEY,                   -- 경제 지표 ID
    indicator_name     VARCHAR(50) NOT NULL,                 -- 경제 지표 이름
    country            VARCHAR(30),                          -- 국가
    source             VARCHAR(50) NOT NULL,                 -- 데이터 출처
    description        TEXT,                                 -- 지표 설명

    external_series_id VARCHAR(100),                         -- 외부 API 시리즈 식별자 (e.g. FRED의 GDPC1 등)
    frequency          VARCHAR(10),                          -- 데이터 빈도 (D=일간, M=월간, Q=분기, A=연간 등)
    unit               VARCHAR(30),                          -- 값의 단위 (percent, index, USD, bps 등)
    release_lag_days   INTEGER,                              -- 발표 지연 일수 (평균)
    category           VARCHAR(50),                          -- 지표 분류 (growth, inflation, labor, survey 등)
    source_url         TEXT,                                 -- 원본 데이터 페이지 URL
    next_release_date  DATE,                                 -- 다음 발표(예정) 일자
    is_active          BOOLEAN     DEFAULT TRUE,             -- 활성 여부 (더 이상 갱신하지 않으면 FALSE)
    notes              TEXT,                                 -- 특이사항 (계산 방식, 계절조정 여부 등)

    last_updated       TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP -- 메타데이터 최종 수정 시각
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

INSERT INTO market_metadata
(indicator_name,
 country,
 source,
 description,
 external_series_id,
 frequency,
 unit,
 release_lag_days,
 category,
 source_url,
 next_release_date,
 is_active,
 notes)
VALUES
    -- 1) 실질 GDP (분기, 연율)
    ('Real GDP (annualized quarterly)',
     'US',
     'FRED',
     'Real Gross Domestic Product, seasonally adjusted annual rate',
     'GDPC1',
     'Q',
     'index',
     30,
     'growth',
     'https://fred.stlouisfed.org/series/GDPC1',
     NULL,
     TRUE,
     '계절조정된 분기 연율치'),

    -- 2) 실업률
    ('Unemployment Rate',
     'US',
     'FRED',
     'Civilian Unemployment Rate',
     'UNRATE',
     'M',
     'percent',
     5,
     'labor',
     'https://fred.stlouisfed.org/series/UNRATE',
     NULL,
     TRUE,
     '월간 발표'),

    -- 3) ISM 제조업 PMI
    ('ISM Manufacturing PMI',
     'US',
     'FRED',
     'Institute for Supply Management Manufacturing PMI',
     'NAPM',
     'M',
     'index',
     3,
     'survey',
     'https://fred.stlouisfed.org/series/NAPM',
     NULL,
     TRUE,
     'ISM 제조업 PMI'),

    -- 4) 소비자물가지수 (CPI-U)
    ('Consumer Price Index (CPI-U)',
     'US',
     'FRED',
     'Consumer Price Index for All Urban Consumers: All Items',
     'CPIAUCSL',
     'M',
     'index',
     15,
     'inflation',
     'https://fred.stlouisfed.org/series/CPIAUCSL',
     NULL,
     TRUE,
     '계절조정 여부 확인 필요'),

    -- 5) 연방기금금리
    ('Federal Funds Rate',
     'US',
     'FRED',
     'Effective Federal Funds Rate',
     'FEDFUNDS',
     'D',
     'percent',
     1,
     'policy',
     'https://fred.stlouisfed.org/series/FEDFUNDS',
     NULL,
     TRUE,
     '연방 기금 금리'),

    -- 6) 2Y–10Y 국채 금리차
    ('2Y–10Y Treasury Yield Spread',
     'US',
     'Computed',
     'Difference between 2-year and 10-year U.S. Treasury yields',
     'DGS2MINUSDGS10',
     'D',
     'bps',
     NULL,
     'yield curve',
     NULL,
     NULL,
     TRUE,
     'DGS2 – DGS10 로 계산'),
    ('2Y Treasury Yield',
     'US',
     'FRED',
     '2-year U.S. Treasury constant maturity yield',
     'DGS2',
     'D',
     'percent',
     NULL, -- release_lag_days
     'yield',
     'https://fred.stlouisfed.org/series/DGS2',
     NULL, -- next_release_date
     TRUE, -- is_active
     '2년물 금리' -- notes
    ),
    -- 8) 10Y Treasury Yield
    ('10Y Treasury Yield',
     'US',
     'FRED',
     '10-year U.S. Treasury constant maturity yield',
     'DGS10',
     'D',
     'percent',
     NULL,
     'yield',
     'https://fred.stlouisfed.org/series/DGS10',
     NULL,
     TRUE,
     '10년물 금리',);


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
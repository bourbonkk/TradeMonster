import datetime
from decimal import Decimal
from pathlib import Path
from unittest import TestCase
from testcontainers.postgres import PostgresContainer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from database.models import (
    EtfSector, EtfComponent, MarketMetadata, MarketTimeseries, PriceData, TradingSignal,
    BacktestResult, EconomicCycle, SectorPerformance)


def get_project_root():
    """프로젝트 루트 디렉토리를 찾는 함수"""
    # 현재 테스트 파일의 위치: tests/database/test_models.py
    current_file = Path(__file__)  # 현재 파일의 경로

    # tests/database에서 두 단계 상위로 이동하여 프로젝트 루트 찾기
    project_root = current_file.parent.parent.parent
    return project_root


def read_ddl_file():
    """DDL SQL 파일을 읽는 함수"""
    project_root = get_project_root()
    ddl_path = project_root / "sql" / "ddl.sql"

    # 파일 존재 여부 확인
    if not ddl_path.exists():
        raise FileNotFoundError(f"DDL 파일을 찾을 수 없습니다: {ddl_path}")

    # 파일 내용 읽기
    with open(ddl_path, "r") as f:
        sql_commands = f.read()

    return sql_commands


class TestDatabaseOperations(TestCase):
    """데이터베이스 작업 테스트 클래스"""

    @classmethod
    def setUpClass(cls):
        # 1. 컨테이너 실행
        cls.postgres = PostgresContainer("timescale/timescaledb:latest-pg17")
        cls.postgres.start()

        # 2. 엔진 및 세션 생성
        cls.engine = create_engine(cls.postgres.get_connection_url())
        cls.Session = sessionmaker(bind=cls.engine, autocommit=False)

        # 3. DDL SQL 파일 읽기 및 실행
        sql_commands = read_ddl_file()

        # 4. SQL 명령 실행
        with cls.engine.connect() as conn:
            conn.execute(text(sql_commands))
            conn.commit()

    @classmethod
    def tearDownClass(cls):
        # 1. 컨테이너 종료
        cls.postgres.stop()

    def setUp(self):
        # 각 테스트 시작 시 세션 생성
        self.session = self.Session()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_etf_sector_insertion(self):
        """
        ETF 섹터 데이터 삽입 테스트
        """
        # ETF 섹터 데이터 삽입 테스트
        spy = EtfSector(
            symbol='SPY',
            name='SPDR S&P 500 ETF Trust',
            country='USA',
            sector='Broad Market',
            description='The SPDR S&P 500 ETF Trust tracks the S&P 500 index',
            expense_ratio=Decimal('0.0945'),
            inception_date=datetime.date(1993, 1, 22),
            assets_under_management=Decimal('374200000000.00')
        )

        self.session.add(spy)
        self.session.commit()

        # 데이터 조회 확인
        result = self.session.query(EtfSector).filter_by(symbol='SPY').first()
        self.assertEqual(result.name, 'SPDR S&P 500 ETF Trust')
        self.assertEqual(result.country, 'USA')

    def test_etf_component_insertion(self):
        """
        ETF 구성 종목 데이터 삽입 테스트
        """
        # ETF 섹터 먼저 생성
        qqq = EtfSector(
            symbol='QQQ',
            name='Invesco QQQ Trust',
            country='USA',
            sector='Technology',
            description='The Invesco QQQ Trust tracks the Nasdaq-100 Index',
            expense_ratio=Decimal('0.0020'),
            inception_date=datetime.date(1999, 3, 10),
            assets_under_management=Decimal('191500000000.00')
        )
        self.session.add(qqq)
        self.session.flush()  # ID 생성을 위한 flush

        # ETF 구성 종목 추가
        aapl = EtfComponent(
            etf_id=qqq.etf_id,
            stock_symbol='AAPL',
            stock_name='Apple Inc.',
            weight_percentage=Decimal('12.3400'),
            sector='Technology',
            industry='Consumer Electronics'
        )
        msft = EtfComponent(
            etf_id=qqq.etf_id,
            stock_symbol='MSFT',
            stock_name='Microsoft Corp.',
            weight_percentage=Decimal('10.2500'),
            sector='Technology',
            industry='Software'
        )

        self.session.add_all([aapl, msft])
        self.session.commit()

        # 관계 확인 (ORM 관계 테스트)
        self.assertEqual(len(qqq.components), 2)
        self.assertEqual(qqq.components[0].stock_symbol, 'AAPL')
        self.assertEqual(qqq.components[1].stock_symbol, 'MSFT')

    def test_economic_cycle_insertion(self):
        """
        경제 사이클 데이터 삽입 테스트
        """
        economic_cycle = EconomicCycle(
            start_date=datetime.date(2020, 1, 1),
            end_date=datetime.date(2022, 12, 31),
            phase="Expansion",
            description="Economic expansion phase with increasing GDP and employment.",
            confidence=Decimal('0.0945'),
        )
        self.session.add(economic_cycle)
        self.session.commit()
        # 결과 확인
        result = self.session.query(EconomicCycle).filter_by(phase="Expansion").first()
        self.assertEqual(result.description, "Economic expansion phase with increasing GDP and employment.")
        self.assertEqual(result.confidence, Decimal('0.09'))

    def test_market_timeseries_insertion(self):
        """
        경제 지표 시계열 데이터 삽입 테스트
        """
        # 경제 지표 메타데이터 생성
        gdp = MarketMetadata(
            indicator_name='GDP',
            country='USA',
            source='Bureau of Economic Analysis',
            description='Gross Domestic Product, quarterly data'
        )
        self.session.add(gdp)
        self.session.flush()

        # 시계열 데이터 추가
        q1 = MarketTimeseries(
            indicator_id=gdp.indicator_id,
            date=datetime.date(2024, 1, 1),
            indicator_value=Decimal('26140.00')
        )
        q2 = MarketTimeseries(
            indicator_id=gdp.indicator_id,
            date=datetime.date(2024, 4, 1),
            indicator_value=Decimal('26580.00')
        )

        self.session.add_all([q1, q2])
        self.session.commit()

        # 결과 확인
        results = self.session.query(MarketTimeseries).filter_by(indicator_id=gdp.indicator_id).order_by(
            MarketTimeseries.date).all()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].indicator_value, Decimal('26140.00'))

    def test_price_data_insertion(self):
        """
        가격 데이터 삽입 및 쿼리 테스트
        """
        # 가격 데이터 삽입
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        today = datetime.datetime.now()

        aapl_yesterday = PriceData(
            symbol='AAPL',
            time=yesterday,
            open=Decimal('185.50'),
            high=Decimal('187.20'),
            low=Decimal('184.30'),
            close=Decimal('186.40'),
            adjusted_close=Decimal('186.40'),
            volume=65000000,
            is_etf=False,
            country='USA'
        )

        aapl_today = PriceData(
            symbol='AAPL',
            time=today,
            open=Decimal('186.40'),
            high=Decimal('189.80'),
            low=Decimal('186.10'),
            close=Decimal('189.50'),
            adjusted_close=Decimal('189.50'),
            volume=72000000,
            is_etf=False,
            country='USA'
        )

        self.session.add_all([aapl_yesterday, aapl_today])
        self.session.commit()

        # TimescaleDB 시간 기반 쿼리 테스트
        result = self.session.query(PriceData).filter(
            PriceData.symbol == 'AAPL',
            PriceData.time > yesterday
        ).all()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].close, Decimal('189.50'))

    def test_trading_signals_insertion(self):
        """
        트레이딩 신호 삽입 및 쿼리 테스트
        """
        # 트레이딩 신호 추가
        now = datetime.datetime.now()

        signal1 = TradingSignal(
            symbol='AAPL',
            time=now,
            signal_type='BUY',
            signal_strength=Decimal('0.85'),
            price=Decimal('189.50'),
            volume=1000,
            strategy_name='Moving Average Crossover',
            rationale='50-day MA crossed above 200-day MA'
        )

        self.session.add(signal1)
        self.session.commit()

        # 신호 조회
        result = self.session.query(TradingSignal).filter_by(symbol='AAPL').first()
        self.assertEqual(result.signal_type, 'BUY')
        self.assertEqual(result.strategy_name, 'Moving Average Crossover')

    def test_timescaledb_functions(self):
        """
        TimescaleDB 하이퍼테이블 및 기능 테스트
        """
        # TimescaleDB 하이퍼테이블 확인 (SQL 직접 실행)
        result = self.session.execute(text("SELECT * FROM timescaledb_information.hypertables"))
        hypertables = result.fetchall()

        # 하이퍼테이블 이름 추출
        hypertable_names = [row[1] for row in hypertables]  # 첫 번째 열이 테이블 이름이라고 가정

        # 우리 테이블이 하이퍼테이블로 등록되었는지 확인
        self.assertIn('market_timeseries', hypertable_names)
        self.assertIn('price_data', hypertable_names)
        self.assertIn('trading_signals', hypertable_names)

    def test_backtest_results_insertion(self):
        """
        백테스트 결과 삽입 및 쿼리 테스트
        """
        # 백테스트 결과 추가
        backtest = BacktestResult(
            strategy_name='Momentum Strategy',
            start_date=datetime.date(2023, 1, 1),
            end_date=datetime.date(2024, 1, 1),
            total_return=Decimal('0.2340'),
            annualized_return=Decimal('0.2340'),
            sharpe_ratio=Decimal('1.45'),
            max_drawdown=Decimal('0.1250'),
            win_rate=Decimal('65.40'),
            parameters={
                'lookback_period': 20,
                'momentum_threshold': 0.05,
                'stop_loss': 0.1
            }
        )

        self.session.add(backtest)
        self.session.commit()

        # 결과 확인
        result = self.session.query(BacktestResult).filter_by(strategy_name='Momentum Strategy').first()
        self.assertEqual(result.total_return, Decimal('0.2340'))
        self.assertEqual(result.parameters['lookback_period'], 20)

    def test_sector_performance_insertion(self):
        """
        섹터 성과 데이터 삽입 및 쿼리 테스트
        """
        # 섹터 성과 데이터 삽입
        sector_performance = SectorPerformance(
            phase='Expansion',
            sector='Technology',
            country='USA',
            historical_return=Decimal('0.15'),
            volatility=Decimal('0.20'),
            sharpe_ratio=Decimal('0.75'),
            success_rate=Decimal('0.80')
        )

        self.session.add(sector_performance)
        self.session.commit()

        # 결과 확인
        result = self.session.query(SectorPerformance).filter_by(phase='Expansion').first()
        self.assertEqual(result.sector, 'Technology')
        self.assertEqual(result.historical_return, Decimal('0.15'))

from sqlalchemy import Column, Integer, String, Text, Numeric, Date, ForeignKey, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMPTZ

Base = declarative_base()


class EtfSector(Base):
    __tablename__ = 'etf_sectors'

    etf_id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    country = Column(String(30))
    sector = Column(String(50))
    description = Column(Text)
    expense_ratio = Column(Numeric(5, 4))
    inception_date = Column(Date)
    assets_under_management = Column(Numeric(20, 2))
    last_updated = Column(TIMESTAMPTZ, default=func.current_timestamp())


class EtfComponent(Base):
    __tablename__ = 'etf_components'

    component_id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey('etf_sectors.etf_id'))
    stock_symbol = Column(String(10), nullable=False)
    stock_name = Column(String(100), nullable=False)
    weight_percentage = Column(Numeric(7, 4))
    sector = Column(String(50))
    industry = Column(String(50))
    last_updated = Column(TIMESTAMPTZ, default=func.current_timestamp())


class MarketMetadata(Base):
    __tablename__ = 'market_metadata'

    indicator_id = Column(Integer, primary_key=True)
    indicator_name = Column(String(50), nullable=False)
    country = Column(String(30))
    source = Column(String(50), nullable=False)
    description = Column(Text)
    last_updated = Column(TIMESTAMPTZ, default=func.current_timestamp())


class MarketTimeseries(Base):
    __tablename__ = 'market_timeseries'

    indicator_id = Column(Integer, ForeignKey('market_metadata.indicator_id'), primary_key=True, nullable=False)
    date = Column(Date, primary_key=True, nullable=False)
    indicator_value = Column(Numeric(20, 6))
    last_updated = Column(TIMESTAMPTZ, default=func.current_timestamp())

    # Note: TimescaleDB hypertable configuration is handled at the database level


class PriceData(Base):
    __tablename__ = 'price_data'

    symbol = Column(String(10), primary_key=True)
    time = Column(TIMESTAMPTZ, primary_key=True)
    open = Column(Numeric(20, 6))
    high = Column(Numeric(20, 6))
    low = Column(Numeric(20, 6))
    close = Column(Numeric(20, 6))
    adjusted_close = Column(Numeric(20, 6))
    volume = Column(BigInteger)
    is_etf = Column(Boolean)
    country = Column(String(30))

    # Note: TimescaleDB hypertable configuration is handled at the database level


class EconomicCycle(Base):
    __tablename__ = 'economic_cycle'

    cycle_id = Column(Integer, primary_key=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    phase = Column(String(15), nullable=False)
    description = Column(Text)
    confidence = Column(Numeric(5, 2))
    last_updated = Column(TIMESTAMPTZ, default=func.current_timestamp())


class SectorPerformance(Base):
    __tablename__ = 'sector_performance'

    performance_id = Column(Integer, primary_key=True)
    phase = Column(String(15), nullable=False)
    sector = Column(String(50))
    country = Column(String(30), nullable=False)
    historical_return = Column(Numeric(8, 4))
    volatility = Column(Numeric(8, 4))
    sharpe_ratio = Column(Numeric(8, 4))
    success_rate = Column(Numeric(5, 2))
    last_updated = Column(TIMESTAMPTZ, default=func.current_timestamp())


class TradingSignal(Base):
    __tablename__ = 'trading_signals'

    signal_id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    time = Column(TIMESTAMPTZ, primary_key=True, nullable=False)
    signal_type = Column(String(20), nullable=False)
    signal_strength = Column(Numeric(5, 2))
    price = Column(Numeric(20, 6))
    volume = Column(BigInteger)
    strategy_name = Column(String(50))
    rationale = Column(Text)

    # Note: TimescaleDB hypertable configuration is handled at the database level


class BacktestResult(Base):
    __tablename__ = 'backtest_results'

    backtest_id = Column(Integer, primary_key=True)
    strategy_name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_return = Column(Numeric(10, 4))
    annualized_return = Column(Numeric(10, 4))
    sharpe_ratio = Column(Numeric(8, 4))
    max_drawdown = Column(Numeric(8, 4))
    win_rate = Column(Numeric(5, 2))
    parameters = Column(JSONB)
    execution_time = Column(TIMESTAMPTZ, default=func.current_timestamp())

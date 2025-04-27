from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

from database.sector_type import GlobalSectorType

Base = declarative_base()


class ETFSector(Base):
    """
    섹터 ETF 자체에 대한 기본 정보를 저장합니다.
    심볼, 이름, 섹터, 비용 비율 등의 메타데이터가 포함됩니다.
    """
    __tablename__ = 'etf_sectors'

    etf_id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    market = Column(String, nullable=False)  # 'US' 또는 'KR'
    global_sector = Column(Enum(GlobalSectorType), nullable=True)  # 통합 분류
    description = Column(String)
    expense_ratio = Column(Float)
    inception_date = Column(Date)
    assets_under_management = Column(Float)
    last_updated = Column(Date, default=datetime.datetime.now().date())

    components = relationship("ETFComponent", back_populates="etf")
    prices = relationship("PriceData", back_populates="etf",
                          primaryjoin="and_(ETFSector.symbol==PriceData.symbol, PriceData.is_etf==True)")


class ETFComponent(Base):
    """
    ETF에 포함된 구성 종목 정보를 저장합니다.
    어떤 종목이 어떤 ETF에 얼마만큼의 비중으로 포함되어 있는지 관리합니다.
    """
    __tablename__ = 'etf_components'

    component_id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey('etf_sectors.etf_id'))
    stock_symbol = Column(String, nullable=False)
    stock_name = Column(String)
    weight_percentage = Column(Float)
    sector = Column(String)
    industry = Column(String)
    last_updated = Column(Date, default=datetime.datetime.now().date())

    etf = relationship("ETFSector", back_populates="components")


class PriceData(Base):
    """
    가격 및 거래량 데이터를 저장합니다.
    ETF와 구성 종목 모두의 가격/거래량이 이 테이블에 저장됩니다.
    is_etf 필드로 ETF인지 개별 종목인지 구분합니다.
    """
    __tablename__ = 'price_data'

    price_id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adjusted_close = Column(Float)
    volume = Column(Float)
    is_etf = Column(Boolean, default=False)

    etf = relationship("ETFSector", back_populates="prices",
                       primaryjoin="and_(PriceData.symbol==ETFSector.symbol, PriceData.is_etf==True)")


class MarketData(Base):
    """
    경제 지표 등 추가 시장 데이터를 저장합니다.
    """
    __tablename__ = 'market_data'

    market_data_id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    indicator_name = Column(String, nullable=False)
    indicator_value = Column(Float)


class RelativeStrength(Base):
    """
    계산된 상대 강도 값을 저장합니다.
    """
    __tablename__ = 'relative_strength'

    rs_id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    etf_symbol = Column(String, nullable=False)
    benchmark_symbol = Column(String, nullable=False)  # 예: 'SPY' 또는 '005930' (삼성전자)
    relative_strength = Column(Float)


# 데이터베이스 생성 함수
def create_database(db_path='sqlite:///data/sector_etf.db'):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    return engine

"""
etf 의 가격 정보를 수집하는 클래스
"""
import logging

import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from collector.base import BaseCollector
from database.models import PriceData

logger = logging.getLogger(__name__)


def convert_to_price_data(data: dict[str, pd.DataFrame], is_etf: bool, country: str) -> list[PriceData]:
    """
    yfinance로 수집한 가격 정보를 변환하는 메서드
    """
    result = []
    for symbol, df in data.items():
        for _, row in df.iterrows():
            row = row.to_dict()
            result.append(PriceData(
                symbol=symbol,
                time=row['Date'],
                open=row['Open'],
                high=row['High'],
                low=row['Low'],
                close=row['Close'],
                adjusted_close=row['Adj Close'],
                volume=row['Volume'],
                is_etf=is_etf,
                country=country
            ))
    return result


class PriceHistoryCollector(BaseCollector):
    """
    미국 ETF의 가격 정보를 수집하는 클래스
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.is_etf = False
        self.country = "US"
        self.full_collection = False

    def collect(self, *args, **kwargs) -> dict[str, pd.DataFrame]:
        symbol = kwargs.get('symbol')
        start_time = kwargs.get('start_time')
        end_time = kwargs.get('end_time')
        self.is_etf = kwargs.get('is_etf')
        self.full_collection = kwargs.get('full_collection')
        self.country = kwargs.get('country', 'US')

        logger.info("Collecting data for %s from %s to %s", symbol, start_time, end_time)

        try:
            df = yf.download(
                tickers=symbol,
                start=start_time,
                end=end_time,
                interval='1d',
                progress=False,
                auto_adjust=False
            )

            if df.empty:
                logger.warning("No price data found for %s", symbol)
                return {symbol: pd.DataFrame()}

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.reset_index(inplace=True)
            return {symbol: df}

        except Exception as e:
            logger.error("Error collecting data for %s: %s", symbol, e)
            return {symbol: pd.DataFrame()}

    def validate(self, data: dict[str, pd.DataFrame]) -> bool:
        """
        수집된 데이터 유효성 검증
        """
        if not data:
            logger.error("No data collected")
            return False
        if not isinstance(data, dict):
            logger.error("Data is not a dictionary")
            return False
        if len(data) == 0:
            logger.error("Data is empty")
            return False
        for symbol, df in data.items():
            if df.empty:
                logger.error("DataFrame for %s is empty", symbol)
                return False
        return True

    def transform(self, data: dict[str, pd.DataFrame]) -> list[PriceData]:
        return convert_to_price_data(data, self.is_etf, self.country)

    def save(self, data: list[PriceData]) -> bool:
        try:
            if self.full_collection:
                self.db_session.add_all(data)
            else:
                for row in data:
                    # 기존에 같은 (symbol, time) 데이터가 있는지 확인
                    exists = self.db_session.query(PriceData).filter_by(symbol=row.symbol, time=row.time).first()
                    if not exists:
                        self.db_session.add(row)

            self.db_session.commit()
            logger.info("Saved %d rows to price_data.", len(data))
            return True
        except Exception as e:
            logger.error("Failed to save price data: %s", e)
            self.db_session.rollback()
            return False

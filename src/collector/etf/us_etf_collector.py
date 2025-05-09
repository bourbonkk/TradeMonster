"""
미국 ETF의 기본 정보 수집기
etf_sectors 테이블에 ETF의 기본 정보를 저장합니다.
"""
import datetime
import logging
from typing import Any

import yfinance as yf

from collector.base import BaseCollector
from database.models import EtfSector

logger = logging.getLogger(__name__)


class UsEtfCollector(BaseCollector):
    """
    미국 ETF 데이터를 수집하는 클래스
    """

    def __init__(self, db_session):
        """
        Args:
            session: 데이터베이스 세션
        """
        self.db_session = db_session

    def collect(self, *args, **kwargs) -> Any:
        """
        yfinance 라이브러리를 사용하여 ETF의 기본 정보를 수집합니다.
        """
        symbol = kwargs.get('symbol')
        sector = kwargs.get('sector')
        logger.info("Collecting %s sector %s", symbol, sector.value)
        try:
            # ETF 정보 수집
            ticker = yf.Ticker(symbol)
            info = ticker.info
            etf_data = {
                'symbol': symbol,
                'name': info.get('shortName', ''),
                'sector': sector.value,
                'country': info.get('region', ''),
                'description': info.get('longBusinessSummary', ''),
                'expense_ratio': info.get('netExpenseRatio', 0),
                'inception_date': self._parse_date(info.get('fundInceptionDate', '')),
                'assets_under_management': info.get('totalAssets', 0),
            }
            return etf_data
        except Exception as e:
            logger.error("Error collecting data for %s: %s", symbol, e)
            return None

    def _parse_date(self, date_str: str) -> Any:
        """
        문자열을 날짜로 변환하는 메서드
        """
        if date_str:
            try:
                return datetime.datetime.fromtimestamp(int(date_str), datetime.UTC).date()
            except ValueError:
                logger.error("Invalid date format: %s", date_str)
                return None
        return None

    def validate(self, data: dict) -> bool:
        """
        수집된 데이터 유효성 검증
        """
        if not data:
            logger.error("No data collected")
            return False

        missing = [field for field in (
            'symbol', 'name', 'sector', 'description', 'expense_ratio',
            'inception_date', 'assets_under_management', 'country'
        ) if not data.get(field)]

        if missing:
            logger.error("Missing required fields: %s", ', '.join(missing))
            return False

        return True

    def transform(self, data: dict) -> EtfSector:
        """
        수집된 데이터를 변환하는 메서드
        """
        return EtfSector(
            symbol=data['symbol'],
            name=data['name'],
            sector=data['sector'],
            country=data['country'],
            description=data['description'],
            expense_ratio=data['expense_ratio'],
            inception_date=data['inception_date'],
            assets_under_management=data['assets_under_management'],
        )

    def save(self, data: EtfSector) -> bool:
        try:
            if self.db_session.query(EtfSector).filter_by(symbol=data.symbol).first():
                logger.info("ETF data for %s already exists, skipping save", data.symbol)
                return True
            self.db_session.add(data)
            self.db_session.commit()
            logger.info("Saved ETF data for %s", data.symbol)
            return True
        except Exception as e:
            logger.error("Error saving data for %s: %s", data.symbol, e)
            return False

"""
US ETF의 구성 종목을 수집하는 모듈입니다.
"""
import logging

import yfinance as yf
from sqlalchemy import select
from sqlalchemy.orm import Session

from collector.base import BaseCollector
from database.models import EtfComponent, EtfSector

logger = logging.getLogger(__name__)


class UsEtfComponentCollector(BaseCollector):
    """
    미국 ETF의 구성 종목을 수집하는 클래스
    TOP 10 종목을 수집합니다.
    """

    def __init__(self, db_session: Session):
        """
        Args:
            session: 데이터베이스 세션
        """
        self.db_session = db_session

    def collect(self, *args, **kwargs) -> dict:
        symbol = kwargs.get('symbol')
        sector = kwargs.get('sector')

        logger.info("Collecting %s sector %s", symbol, sector.value)
        try:
            ticker = yf.Ticker(symbol)
            top_holdings = ticker.funds_data.top_holdings

            if top_holdings is None or top_holdings.empty:
                logger.warning("No holdings found for %s", symbol)
                return {}

            # DataFrame을 딕셔너리로 변환하고, 필요한 필드만 추출
            component_data = {
                sym: {
                    'symbol': sym,
                    'name': row.get('Name', ''),
                    'weight': row.get('Holding Percent', 0),
                    'sector': sector.value,
                    'industry': sector.value  # 임시
                }
                for sym, row in top_holdings.to_dict(orient="index").items()
            }

            return {'etf_symbol': symbol, 'components': component_data}
        except Exception as e:
            logger.exception("Error collecting data for %s: %s", symbol, e)
            return {}

    def validate(self, data: dict) -> bool:
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
        if 'etf_symbol' not in data or 'components' not in data:
            logger.error("Data does not contain required keys")
            return False
        if not isinstance(data['components'], dict):
            logger.error("Components data is not a dictionary")
            return False
        if len(data['components']) == 0:
            logger.error("Components data is empty")
            return False
        return True

    def transform(self, data: dict) -> list:
        """
        수집된 데이터를 변환하는 메서드
        """
        etf_symbol = data["etf_symbol"]
        components = data["components"]

        stmt = select(EtfSector).where(EtfSector.symbol == etf_symbol)
        etf_info = self.db_session.execute(stmt).scalar_one_or_none()

        if not etf_info:
            logger.warning("ETF not found for symbol: %s", etf_symbol)
            return []

        transformed_components = []

        for component_data in components.values():
            component = EtfComponent(
                etf_id=etf_info.etf_id,
                stock_symbol=component_data["symbol"],
                stock_name=component_data["name"],
                weight_percentage=component_data["weight"],
                sector=component_data["sector"],
                industry=component_data["industry"],
            )
            transformed_components.append(component)
        return transformed_components

    def save(self, data: list) -> bool:
        try:
            self.db_session.add_all(data)
            self.db_session.commit()
            logger.info("ETF components saved successfully")
            return True
        except Exception as e:
            logger.error("Error saving ETF components: %s", e)
            self.db_session.rollback()
            return False

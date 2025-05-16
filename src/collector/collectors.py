"""
컬렉터 클래스
"""
from sqlalchemy.orm import Session

from collector.etf.price_history_collector import PriceHistoryCollector
from collector.etf.us_etf_collector import UsEtfCollector
from collector.etf.us_etf_component_collector import UsEtfComponentCollector
from database.models import EtfComponent


class Collectors:
    """
    데이터 수집을 위한 클래스
    """

    def __init__(self, config=None, db_session=None):
        self.config = config
        self.db_session: Session = db_session
        self.collectors = [
            UsEtfCollector(db_session),
            UsEtfComponentCollector(db_session),
        ]
        self.history_collector = PriceHistoryCollector(db_session)

    def run(self, *args, **kwargs):
        """
        모든 수집기를 실행합니다.
        """
        for collector in self.collectors:
            collector.run(*args, **kwargs)

    def collect_etf_price_history(self, *args, **kwargs):
        """
        가격 정보를 수집합니다.
        """
        self.history_collector.run(*args, **kwargs)

    def collect_all_component_price_history(self, *args, **kwargs):
        """
        구성 종목의 가격 정보를 수집합니다.
        """
        etf_component_list = self.db_session.query(EtfComponent).all()
        for etf_component in etf_component_list:
            kwargs['symbol'] = etf_component.stock_symbol
            self.history_collector.run(*args, **kwargs)

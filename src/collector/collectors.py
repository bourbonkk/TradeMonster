"""
컬렉터 클래스
"""
from collector.etf.us_etf_collector import UsEtfCollector
from collector.etf.us_etf_component_collector import UsEtfComponentCollector
from collector.etf.us_etf_price_collector import UsEtfPriceCollector


class Collectors:
    """
    데이터 수집을 위한 클래스
    """

    def __init__(self, config=None, db_session=None):
        self.config = config
        self.collectors = [
            UsEtfCollector(db_session),
            UsEtfComponentCollector(db_session),
            UsEtfPriceCollector(db_session),
        ]

    def run(self, *args, **kwargs):
        """
        모든 수집기를 실행합니다.
        """
        for collector in self.collectors:
            collector.run(*args, **kwargs)

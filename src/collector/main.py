"""
Main entry point for the collector module.
"""
import logging

from collector.collectors import Collectors
from database.etf_mapper import US_ETF_MAPPING
from database.session import get_session

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
if __name__ == "__main__":
    # Initialize the collectors
    session = get_session()
    collectors = Collectors(db_session=session)

    for symbol, sector in US_ETF_MAPPING.items():
        collectors.collect_etf_price_history(
            symbol=symbol,
            sector=sector,
            start_time='2002-01-01',
            end_time='2025-05-11',
            is_etf=True,
            full_collection=True,
        )

    collectors.collect_all_component_price_history(
        start_time='2002-01-01',
        end_time='2025-05-11',
        is_etf=False,
        full_collection=True,
    )

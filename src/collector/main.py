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
        collectors.run(
            symbol=symbol,
            sector=sector,
            # start_time='20020101',
            # end_time='20250101',
        )

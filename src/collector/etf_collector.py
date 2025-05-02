from datetime import datetime, timedelta

import yfinance as yf

from database.etf_mapper import US_ETF_MAPPING, KR_ETF_MAPPING, BENCHMARKS
from database.models import ETFSector, ETFComponent, PriceData


class ETFCollector:
    def __init__(self, db_session):
        self.session = db_session

    def collect_etf_info(self, market='US'):
        """ETF 기본 정보 수집"""
        etfs = US_ETF_MAPPING if market == 'US' else KR_ETF_MAPPING

        for symbol, sector_name in etfs.items():
            try:
                print(f"Collecting data for {symbol}...")
                ticker = yf.Ticker(symbol)
                info = ticker.info

                # ETF 정보 저장
                etf = ETFSector(
                    symbol=symbol,
                    name=info.get('shortName', sector_name),
                    sector=sector_name,
                    description=info.get('longBusinessSummary', ''),
                    expense_ratio=info.get('expenseRatio', 0),
                    inception_date=self._parse_date(info.get('inceptionDate', '')),
                    assets_under_management=info.get('totalAssets', 0),
                    last_updated=datetime.now().date()
                )

                self.session.merge(etf)
                self.session.commit()

                # 구성 종목 정보 수집
                self._collect_components(ticker, symbol)

            except Exception as e:
                print(f"Error collecting data for {symbol}: {e}")
                self.session.rollback()

    def _collect_components(self, ticker, etf_symbol):
        """ETF 구성 종목 정보 수집"""
        try:
            # 현재 yfinance로는 구성 종목 정보를 직접 가져오기 어려움
            # 실제 구현에서는 다른 데이터 소스를 사용하거나 웹 스크래핑 필요
            # 여기서는 예시로 최상위 보유종목 정보만 사용

            holdings = ticker.major_holders
            if holdings is not None and len(holdings) > 0:
                for i, holding in enumerate(holdings.values):
                    if i >= 10:  # 상위 10개만 저장
                        break

                    component = ETFComponent(
                        etf_id=self.session.query(ETFSector.etf_id).filter_by(symbol=etf_symbol).scalar(),
                        stock_symbol=f"UNKNOWN_{i}",  # 실제로는 정확한 종목 심볼 필요
                        stock_name=str(holding[0]) if len(holding) > 0 else "Unknown",
                        weight_percentage=float(str(holding[1]).strip('%')) / 100 if len(holding) > 1 else 0,
                        sector="Unknown",
                        industry="Unknown",
                        last_updated=datetime.now().date()
                    )

                    self.session.merge(component)

            self.session.commit()

        except Exception as e:
            print(f"Error collecting components for {etf_symbol}: {e}")
            self.session.rollback()

    def collect_price_data(self, start_date=None, end_date=None, market='US'):
        """가격 및 거래량 데이터 수집"""
        if end_date is None:
            end_date = datetime.now().date()

        if start_date is None:
            start_date = end_date - timedelta(days=3 * 365)  # 기본 3년치 데이터

        etfs = US_ETF_MAPPING if market == 'US' else KR_ETF_MAPPING

        # 벤치마크 추가
        benchmark = BENCHMARKS['US'] if market == 'US' else BENCHMARKS['KR']
        etfs[benchmark] = 'Benchmark'

        for symbol in etfs.keys():
            try:
                print(f"Collecting price data for {symbol}...")
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date)

                for date, row in hist.iterrows():
                    price = PriceData(
                        symbol=symbol,
                        date=date.date(),
                        open=row['Open'],
                        high=row['High'],
                        low=row['Low'],
                        close=row['Close'],
                        adjusted_close=row.get('Adj Close', row['Close']),
                        volume=row['Volume'],
                        is_etf=True
                    )

                    self.session.merge(price)

                self.session.commit()

            except Exception as e:
                print(f"Error collecting price data for {symbol}: {e}")
                self.session.rollback()

    def _parse_date(self, date_str):
        """날짜 문자열 파싱"""
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            try:
                return datetime.fromtimestamp(int(date_str)).date()
            except:
                return None


def collect_component_price_data(self, etf_symbol, start_date=None, end_date=None):
    """ETF 구성 종목들의 가격 및 거래량 데이터 수집"""

    # ETF 구성 종목 가져오기
    components = self.session.query(ETFComponent).join(ETFSector).filter(ETFSector.symbol == etf_symbol).all()

    if not components:
        print(f"No components found for ETF {etf_symbol}")
        return

    print(f"Collecting price data for {len(components)} components of {etf_symbol}...")

    for component in components:
        try:
            ticker = yf.Ticker(component.stock_symbol)
            hist = ticker.history(start=start_date, end=end_date)

            for date, row in hist.iterrows():
                price_data = PriceData(
                    symbol=component.stock_symbol,
                    date=date.date(),
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    adjusted_close=row.get('Adj Close', row['Close']),
                    volume=row['Volume'],
                    is_etf=False  # 구성 종목이므로 is_etf=False
                )

                self.session.merge(price_data)

            # 중간중간 커밋하여 대량의 데이터 처리 시 부하 분산
            self.session.commit()

        except Exception as e:
            print(f"Error collecting price data for component {component.stock_symbol}: {e}")
            self.session.rollback()
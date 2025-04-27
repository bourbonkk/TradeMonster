import pandas as pd
import numpy as np
from sqlalchemy import func
from database.models import PriceData, RelativeStrength


class RelativeStrengthAnalyzer:
    def __init__(self, db_session):
        self.session = db_session

    def calculate_relative_strength(self, etf_symbols, benchmark_symbol, start_date=None, end_date=None, window=None):
        """
        섹터 ETF의 벤치마크 대비 상대 강도 계산

        Args:
            etf_symbols (list): 분석할 ETF 심볼 리스트
            benchmark_symbol (str): 벤치마크 심볼(예: 'SPY', '069500')
            start_date: 시작일
            end_date: 종료일
            window (int): 이동 평균 윈도우 크기(일). None이면 이동 평균 적용 안함

        Returns:
            pandas.DataFrame: 상대 강도 데이터프레임
        """
        # 벤치마크 데이터 로드
        benchmark_data = pd.read_sql(
            self.session.query(PriceData.date, PriceData.adjusted_close)
            .filter(PriceData.symbol == benchmark_symbol)
            .filter(PriceData.date >= start_date if start_date else True)
            .filter(PriceData.date <= end_date if end_date else True)
            .statement,
            self.session.bind
        )

        if benchmark_data.empty:
            raise ValueError(f"No data found for benchmark {benchmark_symbol}")

        benchmark_data.set_index('date', inplace=True)
        benchmark_data.rename(columns={'adjusted_close': 'benchmark'}, inplace=True)

        relative_strength_results = {}

        for etf_symbol in etf_symbols:
            # ETF 데이터 로드
            etf_data = pd.read_sql(
                self.session.query(PriceData.date, PriceData.adjusted_close)
                .filter(PriceData.symbol == etf_symbol)
                .filter(PriceData.date >= start_date if start_date else True)
                .filter(PriceData.date <= end_date if end_date else True)
                .statement,
                self.session.bind
            )

            if etf_data.empty:
                print(f"No data found for ETF {etf_symbol}, skipping...")
                continue

            etf_data.set_index('date', inplace=True)
            etf_data.rename(columns={'adjusted_close': 'etf'}, inplace=True)

            # 데이터 병합
            combined = benchmark_data.join(etf_data, how='inner')

            if combined.empty:
                print(f"No matching dates for ETF {etf_symbol} and benchmark, skipping...")
                continue

            # 상대 강도 계산 (ETF 수익률 / 벤치마크 수익률)
            combined['etf_returns'] = combined['etf'].pct_change()
            combined['benchmark_returns'] = combined['benchmark'].pct_change()
            combined.dropna(inplace=True)

            # 누적 수익률 계산
            combined['etf_cum_returns'] = (1 + combined['etf_returns']).cumprod()
            combined['benchmark_cum_returns'] = (1 + combined['benchmark_returns']).cumprod()

            # 상대 강도 = ETF 누적 수익률 / 벤치마크 누적 수익률
            combined['relative_strength'] = combined['etf_cum_returns'] / combined['benchmark_cum_returns']

            # 이동 평균 적용 (선택적)
            if window:
                combined[f'rs_ma_{window}'] = combined['relative_strength'].rolling(window=window).mean()

            # 결과 저장
            relative_strength_results[etf_symbol] = combined['relative_strength']

            # 데이터베이스에 저장
            for date, rs in combined['relative_strength'].items():
                rs_record = RelativeStrength(
                    date=date,
                    etf_symbol=etf_symbol,
                    benchmark_symbol=benchmark_symbol,
                    relative_strength=rs
                )
                self.session.merge(rs_record)

            self.session.commit()

        # 모든 ETF의 상대 강도를 하나의 데이터프레임으로 결합
        rs_df = pd.DataFrame(relative_strength_results)

        return rs_df

    def normalize_relative_strength(self, rs_df, method='z_score'):
        """
        상대 강도 값 정규화

        Args:
            rs_df (DataFrame): 상대 강도 데이터프레임
            method (str): 정규화 방법 ('z_score', 'min_max', 'percent_rank')

        Returns:
            DataFrame: 정규화된 상대 강도 데이터프레임
        """
        if method == 'z_score':
            # Z-점수 정규화: (X - 평균) / 표준편차
            return (rs_df - rs_df.mean()) / rs_df.std()

        elif method == 'min_max':
            # Min-Max 정규화: (X - Min) / (Max - Min)
            return (rs_df - rs_df.min()) / (rs_df.max() - rs_df.min())

        elif method == 'percent_rank':
            # 백분위 랭크: 각 값이 전체 분포에서 차지하는 위치 (0~1)
            return rs_df.rank(pct=True)

        else:
            raise ValueError(f"Unknown normalization method: {method}")

    def get_sector_rotation(self, normalized_rs, top_n=3, lookback_period=20):
        """
        현재 강세 섹터 식별

        Args:
            normalized_rs (DataFrame): 정규화된 상대 강도 데이터프레임
            top_n (int): 상위 몇 개 섹터를 선택할지
            lookback_period (int): 최근 몇 일간의 데이터를 볼지

        Returns:
            list: 현재 강세 섹터 리스트
        """
        # 최근 데이터에서 평균 상대 강도 계산
        recent_rs = normalized_rs.iloc[-lookback_period:].mean()

        # 상위 N개 섹터 선택
        top_sectors = recent_rs.nlargest(top_n).index.tolist()

        return top_sectors
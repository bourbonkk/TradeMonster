import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class SectorRotationBacktester:
    def __init__(self, db_session):
        self.session = db_session
        self.initial_capital = 10000  # 초기 자본금 ($10,000)
        self.positions = {}  # 보유 포지션
        self.cash = self.initial_capital  # 보유 현금
        self.portfolio_value = []  # 포트폴리오 가치 기록
        self.trades = []  # 거래 기록

    def run_backtest(self, rs_analyzer, signal_generator, start_date, end_date,
                     etf_symbols, benchmark_symbol, rebalance_freq=20,
                     top_n=3, volume_threshold=1.5):
        """
        섹터 로테이션 전략 백테스팅

        Args:
            rs_analyzer: RelativeStrengthAnalyzer 인스턴스
            signal_generator: VolumeSignalGenerator 인스턴스
            start_date: 시작일
            end_date: 종료일
            etf_symbols: ETF 심볼 리스트
            benchmark_symbol: 벤치마크 심볼
            rebalance_freq: 리밸런싱 빈도 (일)
            top_n: 투자할 상위 섹터 수
            volume_threshold: 거래량 급증 기준

        Returns:
            dict: 백테스팅 결과
        """
        # 날짜 범위 설정
        dates = pd.date_range(start=start_date, end=end_date, freq='B')  # 영업일 기준

        # 거래일 초기화
        self.positions = {}
        self.cash = self.initial_capital
        self.portfolio_value = []
        self.trades = []

        # 모든 ETF의 가격 데이터 로드
        price_data = {}
        for symbol in etf_symbols + [benchmark_symbol]:
            data = signal_generator.get_price_volume_data(symbol, start_date, end_date)
            price_data[symbol] = data

        # 상대 강도 계산
        rs_data = rs_analyzer.calculate_relative_strength(
            etf_symbols=etf_symbols,
            benchmark_symbol=benchmark_symbol,
            start_date=start_date,
            end_date=end_date
        )

        # 백테스팅 시작
        last_rebalance_date = None

        for current_date in dates:
            date_str = current_date.strftime('%Y-%m-%d')

            # 오늘 거래 가능한지 확인 (모든 ETF가 가격 데이터를 가지고 있는지)
            tradable = True
            for symbol in etf_symbols:
                if date_str not in price_data[symbol].index:
                    tradable = False
                    break

            if not tradable:
                continue

            # 포트폴리오 가치 업데이트
            portfolio_value = self.cash
            for symbol, shares in self.positions.items():
                if date_str in price_data[symbol].index:
                    price = price_data[symbol].loc[date_str, 'adjusted_close']
                    position_value = shares * price
                    portfolio_value += position_value

            self.portfolio_value.append({
                'date': current_date,
                'value': portfolio_value
            })

            # 리밸런싱 시점인지 확인
            if last_rebalance_date is None or (current_date - last_rebalance_date).days >= rebalance_freq:
                # 현재 상대 강도 기준 상위 섹터 선택
                if date_str in rs_data.index:
                    current_rs = rs_data.loc[:date_str]
                    normalized_rs = rs_analyzer.normalize_relative_strength(current_rs)
                    top_sectors = rs_analyzer.get_sector_rotation(normalized_rs, top_n, lookback_period=20)

                    # 현재 섹터 중 거래량 신호가 있는 것만 필터링
                    buy_candidates = []
                    for sector in top_sectors:
                        if date_str in price_data[sector].index:
                            # 거래량 지표 계산
                            sector_data = price_data[sector].loc[:date_str].copy()
                            sector_data = signal_generator.calculate_volume_indicators(sector_data)
                            sector_data = signal_generator.generate_buy_signals(sector_data,
                                                                                threshold_volume=volume_threshold)

                            # 최근 5일 내 매수 신호가 있는지 확인
                            recent_data = sector_data.tail(5)
                            if recent_data['buy_signal'].any():
                                buy_candidates.append(sector)

                    # 전체 포트폴리오 청산
                    for symbol, shares in list(self.positions.items()):
                        if date_str in price_data[symbol].index:
                            price = price_data[symbol].loc[date_str, 'adjusted_close']
                            sell_value = shares * price
                            self.cash += sell_value

                            self.trades.append({
                                'date': current_date,
                                'symbol': symbol,
                                'action': 'SELL',
                                'shares': shares,
                                'price': price,
                                'value': sell_value
                            })

                            del self.positions[symbol]

                    # 매수 후보에 투자
                    if buy_candidates:
                        allocation_per_etf = self.cash / len(buy_candidates)

                        for symbol in buy_candidates:
                            if date_str in price_data[symbol].index:
                                price = price_data[symbol].loc[date_str, 'adjusted_close']
                                shares = allocation_per_etf / price
                                self.positions[symbol] = shares
                                self.cash -= allocation_per_etf

                                self.trades.append({
                                    'date': current_date,
                                    'symbol': symbol,
                                    'action': 'BUY',
                                    'shares': shares,
                                    'price': price,
                                    'value': allocation_per_etf
                                })

                    last_rebalance_date = current_date

        # 백테스팅 결과 분석
        portfolio_df = pd.DataFrame(self.portfolio_value)
        portfolio_df.set_index('date', inplace=True)

        # 벤치마크 성과
        benchmark_data = price_data[benchmark_symbol].copy()
        benchmark_data['normalized'] = benchmark_data['adjusted_close'] / benchmark_data['adjusted_close'].iloc[
            0] * self.initial_capital

        # 수익률 계산
        final_value = portfolio_df['value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100

        # 연간 수익률 계산
        days = (end_date - start_date).days
        annual_return = (final_value / self.initial_capital) ** (365 / days) - 1

        # 거래 기록 데이터프레임으로 변환
        trades_df = pd.DataFrame(self.trades)

        return {
            'portfolio_value': portfolio_df,
            'benchmark': benchmark_data[['adjusted_close', 'normalized']],
            'trades': trades_df,
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return * 100,
            'num_trades': len(self.trades)
        }


class SectorVolumeBacktester:
    def __init__(self, db_session):
        self.session = db_session
        self.initial_capital = 10000  # 초기 자본금 ($10,000)
        self.positions = {}  # 보유 포지션
        self.cash = self.initial_capital  # 보유 현금
        self.portfolio_value = []  # 포트폴리오 가치 기록
        self.trades = []  # 거래 기록

    def run_backtest(self, signal_generator, symbol, start_date, end_date,
                     benchmark_symbol=None):
        """
        단일 ETF에 대한 거래량 기반 전략 백테스팅

        Args:
            signal_generator: VolumeSignalGenerator 인스턴스
            symbol: 테스트할 ETF 심볼
            start_date: 시작일
            end_date: 종료일
            benchmark_symbol: 벤치마크 심볼 (선택적)

        Returns:
            dict: 백테스팅 결과
        """
        # 가격 및 거래량 데이터 로드
        data = signal_generator.get_price_volume_data(symbol, start_date, end_date)

        # 거래량 지표 및 신호 생성
        data = signal_generator.calculate_volume_indicators(data)
        data = signal_generator.generate_buy_signals(data)
        data = signal_generator.generate_sell_signals(data)

        # 벤치마크 데이터 로드 (있는 경우)
        benchmark_data = None
        if benchmark_symbol:
            benchmark_data = signal_generator.get_price_volume_data(benchmark_symbol, start_date, end_date)

        # 초기화
        self.positions = {}
        self.cash = self.initial_capital
        self.portfolio_value = []
        self.trades = []

        # 백테스팅 진행
        holding = False
        entry_price = 0

        for date, row in data.iterrows():
            # 매수 신호
            if row['buy_signal'] and not holding and self.cash > 0:
                price = row['adjusted_close']
                shares = self.cash / price
                self.positions[symbol] = shares
                entry_price = price
                self.cash = 0
                holding = True

                self.trades.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'BUY',
                    'shares': shares,
                    'price': price,
                    'value': shares * price
                })

            # 매도 신호
            elif row['sell_signal'] and holding:
                price = row['adjusted_close']
                shares = self.positions[symbol]
                sell_value = shares * price
                self.cash += sell_value
                del self.positions[symbol]
                holding = False

                self.trades.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'SELL',
                    'shares': shares,
                    'price': price,
                    'value': sell_value
                })

            # 포트폴리오 가치 업데이트
            portfolio_value = self.cash
            for sym, shares in self.positions.items():
                portfolio_value += shares * row['adjusted_close']

            self.portfolio_value.append({
                'date': date,
                'value': portfolio_value
            })

        # 마지막 날 포지션 청산
        if holding:
            last_price = data['adjusted_close'].iloc[-1]
            shares = self.positions[symbol]
            sell_value = shares * last_price
            self.cash += sell_value
            self.positions = {}

            self.trades.append({
                'date': data.index[-1],
                'symbol': symbol,
                'action': 'SELL (End)',
                'shares': shares,
                'price': last_price,
                'value': sell_value
            })

        # 결과 분석
        portfolio_df = pd.DataFrame(self.portfolio_value)
        portfolio_df.set_index('date', inplace=True)

        # 벤치마크 성과 (있는 경우)
        if benchmark_data is not None:
            benchmark_data['normalized'] = benchmark_data['adjusted_close'] / benchmark_data['adjusted_close'].iloc[
                0] * self.initial_capital

        # 단순 매수 후 보유 전략 (Buy and Hold)
        buy_hold_shares = self.initial_capital / data['adjusted_close'].iloc[0]
        data['buy_hold'] = data['adjusted_close'] * buy_hold_shares

        # 수익률 계산
        final_value = portfolio_df['value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100

        # 연간 수익률 계산
        days = (end_date - start_date).days
        annual_return = (final_value / self.initial_capital) ** (365 / days) - 1

        # 최대 낙폭 계산
        rolling_max = portfolio_df['value'].cummax()
        drawdown = (portfolio_df['value'] - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()

        # 거래 기록 데이터프레임으로 변환
        trades_df = pd.DataFrame(self.trades)

        return {
            'portfolio_value': portfolio_df,
            'etf_data': data,
            'benchmark': benchmark_data if benchmark_data is not None else None,
            'trades': trades_df,
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return * 100,
            'max_drawdown': max_drawdown,
            'num_trades': len(self.trades)
        }
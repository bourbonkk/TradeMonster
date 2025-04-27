import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib.dates import DateFormatter
import matplotlib.ticker as mtick


class ETFAnalysisVisualizer:
    def __init__(self, figsize=(12, 8)):
        self.figsize = figsize
        self.colors = {
            'portfolio': '#2C3E50',
            'benchmark': '#E74C3C',
            'buy': '#27AE60',
            'sell': '#C0392B',
            'price': '#3498DB',
            'volume': '#9B59B6',
            'up': '#2ECC71',
            'down': '#E74C3C'
        }

        # Seaborn 스타일 설정
        sns.set_style('whitegrid')

    def plot_relative_strength(self, rs_data, title='Sector Relative Strength', window=None):
        """
        섹터 상대 강도 차트

        Args:
            rs_data (DataFrame): 상대 강도 데이터
            title (str): 차트 제목
            window (int): 이동 평균 기간 (None이면 사용 안함)
        """
        plt.figure(figsize=self.figsize)

        # 원본 데이터 플롯
        for column in rs_data.columns:
            plt.plot(rs_data.index, rs_data[column], alpha=0.7, linewidth=1, label=column)

        # 이동 평균 플롯 (선택적)
        if window:
            for column in rs_data.columns:
                ma = rs_data[column].rolling(window=window).mean()
                plt.plot(rs_data.index, ma, linewidth=2, label=f'{column} {window}MA')

        # 차트 스타일링
        plt.axhline(y=1.0, color='black', linestyle='--', alpha=0.3)
        plt.title(title, fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Relative Strength (vs Benchmark)', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)

        # 날짜 형식 설정
        date_format = DateFormatter('%Y-%m')
        plt.gca().xaxis.set_major_formatter(date_format)
        plt.xticks(rotation=45)

        plt.tight_layout()
        return plt.gcf()

    def plot_top_sectors(self, normalized_rs, top_n=3, lookback=20):
        """
        상위 섹터 강조 차트

        Args:
            normalized_rs (DataFrame): 정규화된 상대 강도 데이터
            top_n (int): 표시할 상위 섹터 수
            lookback (int): 최근 몇 일 기준으로 할지
        """
        # 최근 데이터에서 평균 상대 강도 계산
        recent_rs = normalized_rs.iloc[-lookback:].mean()

        # 상위 N개 섹터 선택
        top_sectors = recent_rs.nlargest(top_n).index.tolist()

        plt.figure(figsize=self.figsize)

        # 모든 섹터 플롯 (흐리게)
        for column in normalized_rs.columns:
            if column in top_sectors:
                continue
            plt.plot(normalized_rs.index, normalized_rs[column], color='gray', alpha=0.3, linewidth=1)

        # 상위 섹터 강조 플롯
        for i, sector in enumerate(top_sectors):
            plt.plot(normalized_rs.index, normalized_rs[sector], linewidth=2.5, label=sector)

        # 차트 스타일링
        plt.title(f'Top {top_n} Sectors (Last {lookback} Days)', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Normalized Relative Strength', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)

        # 날짜 형식 설정
        date_format = DateFormatter('%Y-%m')
        plt.gca().xaxis.set_major_formatter(date_format)
        plt.xticks(rotation=45)

        plt.tight_layout()
        return plt.gcf()

    def plot_volume_signals(self, data, title=None):
        """
        거래량 및 신호 차트

        Args:
            data (DataFrame): 가격, 거래량, 신호 데이터
            title (str): 차트 제목
        """
        # 필요한 컬럼이 있는지 확인
        required_columns = ['adjusted_close', 'volume', 'price_ma', 'volume_ma', 'buy_signal', 'sell_signal']
        for col in required_columns:
            if col not in data.columns:
                print(f"Warning: Column '{col}' not found in data. Skipping.")
                return None

        # 차트 생성 (2개의 서브플롯)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

        # 가격 및 이동평균선 플롯
        ax1.plot(data.index, data['adjusted_close'], label='Price', color=self.colors['price'], linewidth=1.5)
        ax1.plot(data.index, data['price_ma'], label='Price MA', color='orange', linewidth=1, alpha=0.7)

        # 매수/매도 신호 표시
        buy_signals = data[data['buy_signal']].index
        sell_signals = data[data['sell_signal']].index

        ax1.scatter(buy_signals, data.loc[buy_signals, 'adjusted_close'],
                    color=self.colors['buy'], s=100, marker='^', label='Buy Signal')
        ax1.scatter(sell_signals, data.loc[sell_signals, 'adjusted_close'],
                    color=self.colors['sell'], s=100, marker='v', label='Sell Signal')

        # 가격 차트 스타일링
        ax1.set_title(title or 'Price and Trading Signals', fontsize=16)
        ax1.set_ylabel('Price', fontsize=12)
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.3)

        # 거래량 플롯
        ax2.bar(data.index, data['volume'], label='Volume', color=self.colors['volume'], alpha=0.5)
        ax2.plot(data.index, data['volume_ma'], label='Volume MA', color='red', linewidth=1)

        # 거래량 급증 강조
        volume_spikes = data[data['relative_volume'] > 1.5].index
        ax2.bar(volume_spikes, data.loc[volume_spikes, 'volume'], color='red', alpha=0.7)

        # 거래량 차트 스타일링
        ax2.set_ylabel('Volume', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.legend(loc='upper left', fontsize=10)
        ax2.grid(True, alpha=0.3)

        # 날짜 형식 설정
        date_format = DateFormatter('%Y-%m')
        ax2.xaxis.set_major_formatter(date_format)
        plt.xticks(rotation=45)

        plt.tight_layout()
        return fig

    def plot_backtest_results(self, results, benchmark_name='Benchmark'):
        """
        백테스팅 결과 시각화

        Args:
            results (dict): 백테스팅 결과 딕셔너리
            benchmark_name (str): 벤치마크 이름
        """
        # 차트 생성 (2개의 서브플롯)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

        # 포트폴리오 가치 플롯
        portfolio = results['portfolio_value']
        ax1.plot(portfolio.index, portfolio['value'], label='Strategy', color=self.colors['portfolio'], linewidth=2)

        # 벤치마크 플롯 (있는 경우)
        if 'benchmark' in results and results['benchmark'] is not None:
            benchmark = results['benchmark']
            ax1.plot(benchmark.index, benchmark['normalized'], label=benchmark_name,
                     color=self.colors['benchmark'], linewidth=1.5, alpha=0.7)

        # 단순 매수 후 보유 전략 플롯 (있는 경우)
        if 'etf_data' in results and 'buy_hold' in results['etf_data'].columns:
            buy_hold = results['etf_data']
            ax1.plot(buy_hold.index, buy_hold['buy_hold'], label='Buy & Hold',
                     color='green', linewidth=1.5, linestyle='--', alpha=0.7)

        # 거래 표시
        if 'trades' in results and not results['trades'].empty:
            trades = results['trades']

            # 매수 거래
            buys = trades[trades['action'].str.contains('BUY')]
            for _, trade in buys.iterrows():
                date = trade['date']
                price = trade['value'] / trade['shares']
                ax1.scatter(date, price, color=self.colors['buy'], s=100, marker='^')

            # 매도 거래
            sells = trades[trades['action'].str.contains('SELL')]
            for _, trade in sells.iterrows():
                date = trade['date']
                price = trade['value'] / trade['shares']
                ax1.scatter(date, price, color=self.colors['sell'], s=100, marker='v')

        # 차트 스타일링
        total_return = results['total_return']
        annual_return = results['annual_return']
        max_drawdown = results.get('max_drawdown', 0)

        ax1.set_title(
            f'Backtest Results: {total_return:.2f}% Return, {annual_return:.2f}% Annual, {max_drawdown:.2f}% Max DD',
            fontsize=16)
        ax1.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)

        # Y축 달러 형식으로 표시
        ax1.yaxis.set_major_formatter('${x:,.0f}')

        # 수익률 플롯 (두 번째 서브플롯)
        initial = results['initial_capital']

        # 전략 수익률
        portfolio_returns = (portfolio['value'] / initial - 1) * 100
        ax2.plot(portfolio.index, portfolio_returns, label='Strategy Returns',
                 color=self.colors['portfolio'], linewidth=2)

        # 벤치마크 수익률 (있는 경우)
        if 'benchmark' in results and results['benchmark'] is not None:
            benchmark = results['benchmark']
            benchmark_returns = (benchmark['normalized'] / initial - 1) * 100
            ax2.plot(benchmark.index, benchmark_returns, label=f'{benchmark_name} Returns',
                     color=self.colors['benchmark'], linewidth=1.5, alpha=0.7)

        # 수익률 차트 스타일링
        ax2.set_ylabel('Returns (%)', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.legend(loc='best', fontsize=10)
        ax2.grid(True, alpha=0.3)

        # Y축 퍼센트 형식으로 표시
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter())

        # 날짜 형식 설정
        date_format = DateFormatter('%Y-%m')
        ax2.xaxis.set_major_formatter(date_format)
        plt.xticks(rotation=45)

        plt.tight_layout()
        return fig

    def plot_sector_performance_summary(self, backtest_results_dict):
        """
        여러 섹터의 백테스팅 결과 비교

        Args:
            backtest_results_dict (dict): {섹터 이름: 백테스팅 결과} 형태의 딕셔너리
        """
        # 성능 지표 추출
        sectors = list(backtest_results_dict.keys())
        total_returns = [results['total_return'] for results in backtest_results_dict.values()]
        annual_returns = [results['annual_return'] for results in backtest_results_dict.values()]
        max_drawdowns = [results.get('max_drawdown', 0) for results in backtest_results_dict.values()]
        num_trades = [results['num_trades'] for results in backtest_results_dict.values()]

        # 전체 성과 비교 차트
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)

        # 총 수익률
        axes[0, 0].bar(sectors, total_returns, color=sns.color_palette('viridis', len(sectors)))
        axes[0, 0].set_title('Total Return (%)', fontsize=14)
        axes[0, 0].set_ylabel('Percent (%)')
        axes[0, 0].set_xticklabels(sectors, rotation=45, ha='right')
        axes[0, 0].yaxis.set_major_formatter(mtick.PercentFormatter())

        # 연간 수익률
        axes[0, 1].bar(sectors, annual_returns, color=sns.color_palette('viridis', len(sectors)))
        axes[0, 1].set_title('Annual Return (%)', fontsize=14)
        axes[0, 1].set_ylabel('Percent (%)')
        axes[0, 1].set_xticklabels(sectors, rotation=45, ha='right')
        axes[0, 1].yaxis.set_major_formatter(mtick.PercentFormatter())

        # 최대 낙폭
        axes[1, 0].bar(sectors, max_drawdowns, color=sns.color_palette('viridis', len(sectors)))
        axes[1, 0].set_title('Maximum Drawdown (%)', fontsize=14)
        axes[1, 0].set_ylabel('Percent (%)')
        axes[1, 0].set_xticklabels(sectors, rotation=45, ha='right')
        axes[1, 0].yaxis.set_major_formatter(mtick.PercentFormatter())

        # 거래 횟수
        axes[1, 1].bar(sectors, num_trades, color=sns.color_palette('viridis', len(sectors)))
        axes[1, 1].set_title('Number of Trades', fontsize=14)
        axes[1, 1].set_ylabel('Count')
        axes[1, 1].set_xticklabels(sectors, rotation=45, ha='right')

        plt.tight_layout()
        return fig
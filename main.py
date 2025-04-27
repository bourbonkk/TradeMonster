import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.etf_mapper import US_ETF_MAPPING, BENCHMARKS
from database.models import create_database
from collector.etf_collector import ETFCollector
from analysis.relative_strength import RelativeStrengthAnalyzer
from strategy.signals import VolumeSignalGenerator
from strategy.backtesting import SectorRotationBacktester, SectorVolumeBacktester
from visualization.charts import ETFAnalysisVisualizer
import matplotlib.pyplot as plt
import pandas as pd
import os


def main():
    # 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    os.makedirs('results', exist_ok=True)

    # 데이터베이스 초기화
    engine = create_database()
    Session = sessionmaker(bind=engine)
    session = Session()

    # 데이터 수집 (미국 시장)
    collector = ETFCollector(session)

    # ETF 정보 수집
    print("Collecting ETF information...")
    collector.collect_etf_info(market='US')

    # 가격 데이터 수집 (최근 3년)
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=3 * 365)
    print(f"Collecting price data from {start_date} to {end_date}...")
    collector.collect_price_data(start_date=start_date, end_date=end_date, market='US')

    # 시각화 도구 초기화
    visualizer = ETFAnalysisVisualizer()

    # 상대 강도 분석
    print("Analyzing relative strength...")
    analyzer = RelativeStrengthAnalyzer(session)
    us_etfs = list(US_ETF_MAPPING.keys())
    benchmark = BENCHMARKS['US']

    rs_data = analyzer.calculate_relative_strength(
        etf_symbols=us_etfs,
        benchmark_symbol=benchmark,
        start_date=start_date,
        end_date=end_date,
        window=20  # 20일 이동 평균
    )

    # 상대 강도 차트 생성
    print("Generating relative strength charts...")
    rs_fig = visualizer.plot_relative_strength(rs_data, title='Sector ETFs vs S&P 500', window=20)
    rs_fig.savefig('results/relative_strength.png')

    # 상대 강도 정규화
    normalized_rs = analyzer.normalize_relative_strength(rs_data, method='z_score')

    # 상위 섹터 차트 생성
    top_sectors_fig = visualizer.plot_top_sectors(normalized_rs, top_n=3, lookback=20)
    top_sectors_fig.savefig('results/top_sectors.png')

    # 현재 강세 섹터 식별
    top_sectors = analyzer.get_sector_rotation(normalized_rs, top_n=3, lookback_period=20)
    print(f"Current top sectors: {top_sectors}")

    # 거래량 기반 신호 생성 및 시각화
    print("\nAnalyzing volume signals...")
    signal_generator = VolumeSignalGenerator(session)

    volume_signal_figs = {}
    for sector in top_sectors:
        print(f"Processing {sector}...")
        data = signal_generator.get_price_volume_data(sector, start_date=start_date, end_date=end_date)

        # 거래량 지표 계산
        data = signal_generator.calculate_volume_indicators(data)

        # 매수/매도 신호 생성
        data = signal_generator.generate_buy_signals(data)
        data = signal_generator.generate_sell_signals(data)

        # 신호 시각화
        fig = visualizer.plot_volume_signals(data, title=f"{sector} Trading Signals")
        volume_signal_figs[sector] = fig
        fig.savefig(f'results/{sector}_signals.png')

        # 최근 신호 확인
        recent_days = 30
        recent_data = data.tail(recent_days)

        buy_days = recent_data[recent_data['buy_signal']].index.tolist()
        sell_days = recent_data[recent_data['sell_signal']].index.tolist()

        print(f"Recent {recent_days} days analysis for {sector}:")
        print(f"Buy signals: {buy_days}")
        print(f"Sell signals: {sell_days}")

        # 현재 시점 신호
        latest_day = data.index[-1]
        if data.loc[latest_day, 'buy_signal']:
            print(f"CURRENT BUY SIGNAL for {sector} on {latest_day}")
        elif data.loc[latest_day, 'sell_signal']:
            print(f"CURRENT SELL SIGNAL for {sector} on {latest_day}")
        else:
            print(f"No clear signal for {sector} on {latest_day}")

    # 백테스팅 수행
    print("\nRunning backtests...")

    # 1. 단일 섹터 거래량 기반 전략 백테스팅
    volume_backtest_results = {}
    volume_backtester = SectorVolumeBacktester(session)

    for sector in top_sectors:
        print(f"Backtesting volume strategy for {sector}...")
        backtest_results = volume_backtester.run_backtest(
            signal_generator=signal_generator,
            symbol=sector,
            start_date=start_date,
            end_date=end_date,
            benchmark_symbol=benchmark
        )

        volume_backtest_results[sector] = backtest_results

        # 백테스팅 결과 시각화
        backtest_fig = visualizer.plot_backtest_results(backtest_results, benchmark_name='S&P 500')
        backtest_fig.savefig(f'results/{sector}_backtest.png')

        # 결과 출력
        print(f"  {sector} Backtest Results:")
        print(f"  Initial capital: ${backtest_results['initial_capital']:.2f}")
        print(f"  Final value: ${backtest_results['final_value']:.2f}")
        print(f"  Total return: {backtest_results['total_return']:.2f}%")
        print(f"  Annual return: {backtest_results['annual_return']:.2f}%")
        print(f"  Number of trades: {backtest_results['num_trades']}")
        if 'max_drawdown' in backtest_results:
            print(f"  Maximum drawdown: {backtest_results['max_drawdown']:.2f}%")
        print()

    # 섹터 성능 비교 차트
    summary_fig = visualizer.plot_sector_performance_summary(volume_backtest_results)
    summary_fig.savefig('results/sector_performance_comparison.png')

    # 2. 섹터 로테이션 전략 백테스팅
    print("Backtesting sector rotation strategy...")
    rotation_backtester = SectorRotationBacktester(session)

    rotation_backtest_results = rotation_backtester.run_backtest(
        rs_analyzer=analyzer,
        signal_generator=signal_generator,
        start_date=start_date,
        end_date=end_date,
        etf_symbols=us_etfs,
        benchmark_symbol=benchmark,
        rebalance_freq=20,  # 20일마다 리밸런싱
        top_n=3,  # 상위 3개 섹터 선택
        volume_threshold=1.5  # 거래량 임계값
    )

    # 섹터 로테이션 백테스팅 결과 시각화
    rotation_fig = visualizer.plot_backtest_results(rotation_backtest_results, benchmark_name='S&P 500')
    rotation_fig.savefig('results/rotation_strategy_backtest.png')

    # 결과 출력
    print("\nSector Rotation Strategy Backtest Results:")
    print(f"Initial capital: ${rotation_backtest_results['initial_capital']:.2f}")
    print(f"Final value: ${rotation_backtest_results['final_value']:.2f}")
    print(f"Total return: {rotation_backtest_results['total_return']:.2f}%")
    print(f"Annual return: {rotation_backtest_results['annual_return']:.2f}%")
    print(f"Number of trades: {rotation_backtest_results['num_trades']}")

    # 포트폴리오 성과 표 생성
    portfolio_stats = {
        'Strategy': ['Sector Rotation'] + top_sectors,
        'Total Return (%)': [rotation_backtest_results['total_return']] +
                            [volume_backtest_results[sector]['total_return'] for sector in top_sectors],
        'Annual Return (%)': [rotation_backtest_results['annual_return']] +
                             [volume_backtest_results[sector]['annual_return'] for sector in top_sectors],
        'Number of Trades': [rotation_backtest_results['num_trades']] +
                            [volume_backtest_results[sector]['num_trades'] for sector in top_sectors],
    }

    stats_df = pd.DataFrame(portfolio_stats)
    print("\nStrategy Comparison:")
    print(stats_df.to_string(index=False))

    # 결과 저장
    stats_df.to_csv('results/strategy_comparison.csv', index=False)

    # 현재 투자 추천 생성
    print("\nGenerating current investment recommendations...")

    # 상대 강도 기준 상위 섹터
    rs_top_sectors = analyzer.get_sector_rotation(normalized_rs, top_n=3, lookback_period=20)

    # 거래량 신호가 있는 섹터만 필터링
    recommended_sectors = []
    for sector in rs_top_sectors:
        data = signal_generator.get_price_volume_data(sector, start_date=end_date - datetime.timedelta(days=30),
                                                      end_date=end_date)
        if data.empty:
            continue

        data = signal_generator.calculate_volume_indicators(data)
        data = signal_generator.generate_buy_signals(data)

        # 최근 5일 내 매수 신호가 있는지 확인
        recent_data = data.tail(5)
        if recent_data['buy_signal'].any():
            recommended_sectors.append(sector)

    print("\nCurrent investment recommendations:")
    if recommended_sectors:
        for sector in recommended_sectors:
            print(f"BUY: {sector} - Strong relative performance with positive volume signals")
    else:
        print("No clear buy recommendations at this time. Consider waiting for stronger signals.")

    # 세션 종료
    session.close()
    print("\nAnalysis complete. Results saved to 'results' directory.")


if __name__ == "__main__":
    main()
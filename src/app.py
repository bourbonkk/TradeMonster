from flask import Flask, render_template, jsonify
from sqlalchemy.orm import sessionmaker
import datetime
import os

from database.models import create_database
from data_collection.etf_collector import ETFDataCollector
from analysis import RelativeStrengthAnalyzer
from strategy import VolumeSignalGenerator

app = Flask(__name__)

# 데이터베이스 연결
engine = create_database()
Session = sessionmaker(bind=engine)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/etf_sectors')
def get_etf_sectors():
    session = Session()

    # ETF 수집기 인스턴스 생성
    collector = ETFDataCollector(session)

    # 섹터 데이터 반환
    sectors = {
        'US': collector.us_sector_etfs,
        'KR': collector.kr_sector_etfs
    }

    session.close()
    return jsonify(sectors)


@app.route('/api/relative_strength')
def get_relative_strength():
    session = Session()

    # 분석기 인스턴스 생성
    analyzer = RelativeStrengthAnalyzer(session)
    collector = ETFDataCollector(session)

    # 날짜 범위 설정
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=365)  # 1년 데이터

    # 상대 강도 계산
    us_etfs = list(collector.us_sector_etfs.keys())
    benchmark = collector.benchmarks['US']

    rs_data = analyzer.calculate_relative_strength(
        etf_symbols=us_etfs,
        benchmark_symbol=benchmark,
        start_date=start_date,
        end_date=end_date
    )

    # 정규화
    normalized_rs = analyzer.normalize_relative_strength(rs_data, method='z_score')

    # JSON 직렬화 가능한 형식으로 변환
    rs_json = {
        'dates': rs_data.index.strftime('%Y-%m-%d').tolist(),
        'raw_data': {col: rs_data[col].tolist() for col in rs_data.columns},
        'normalized_data': {col: normalized_rs[col].tolist() for col in normalized_rs.columns}
    }

    session.close()
    return jsonify(rs_json)


@app.route('/api/top_sectors')
def get_top_sectors():
    session = Session()

    # 분석기 인스턴스 생성
    analyzer = RelativeStrengthAnalyzer(session)
    collector = ETFDataCollector(session)

    # 날짜 범위 설정
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=365)  # 1년 데이터

    # 상대 강도 계산
    us_etfs = list(collector.us_sector_etfs.keys())
    benchmark = collector.benchmarks['US']

    rs_data = analyzer.calculate_relative_strength(
        etf_symbols=us_etfs,
        benchmark_symbol=benchmark,
        start_date=start_date,
        end_date=end_date
    )

    # 정규화
    normalized_rs = analyzer.normalize_relative_strength(rs_data, method='z_score')

    # 상위 섹터 가져오기
    top_sectors = analyzer.get_sector_rotation(normalized_rs, top_n=3, lookback_period=20)

    # 섹터 이름 매핑
    sector_names = collector.us_sector_etfs
    top_sector_names = {sector: sector_names.get(sector, sector) for sector in top_sectors}

    session.close()
    return jsonify({
        'top_sectors': top_sectors,
        'sector_names': top_sector_names
    })


@app.route('/api/signals/<symbol>')
def get_signals(symbol):
    session = Session()

    # 신호 생성기 인스턴스 생성
    signal_generator = VolumeSignalGenerator(session)

    # 날짜 범위 설정
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=180)  # 6개월 데이터

    # 데이터 가져오기
    data = signal_generator.get_price_volume_data(symbol, start_date=start_date, end_date=end_date)

    # 지표 및 신호 계산
    data = signal_generator.calculate_volume_indicators(data)
    data = signal_generator.generate_buy_signals(data)
    data = signal_generator.generate_sell_signals(data)

    # JSON 직렬화 가능한 형식으로 변환
    data_json = {
        'dates': data.index.strftime('%Y-%m-%d').tolist(),
        'price': data['adjusted_close'].tolist(),
        'volume': data['volume'].tolist(),
        'price_ma': data['price_ma'].tolist(),
        'volume_ma': data['volume_ma'].tolist(),
        'buy_signals': data.index[data['buy_signal']].strftime('%Y-%m-%d').tolist(),
        'sell_signals': data.index[data['sell_signal']].strftime('%Y-%m-%d').tolist()
    }

    session.close()
    return jsonify(data_json)


@app.route('/api/recommendations')
def get_recommendations():
    session = Session()

    # 분석기 및 신호 생성기 인스턴스 생성
    analyzer = RelativeStrengthAnalyzer(session)
    signal_generator = VolumeSignalGenerator(session)
    collector = ETFDataCollector(session)

    # 날짜 범위 설정
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=365)  # 1년 데이터

    # 상대 강도 계산
    us_etfs = list(collector.us_sector_etfs.keys())
    benchmark = collector.benchmarks['US']

    rs_data = analyzer.calculate_relative_strength(
        etf_symbols=us_etfs,
        benchmark_symbol=benchmark,
        start_date=start_date,
        end_date=end_date
    )

    # 정규화
    normalized_rs = analyzer.normalize_relative_strength(rs_data, method='z_score')

    # 상위 섹터 가져오기
    top_sectors = analyzer.get_sector_rotation(normalized_rs, top_n=5, lookback_period=20)

    # 거래량 신호가 있는 섹터만 필터링
    recommended_sectors = []
    for sector in top_sectors:
        data = signal_generator.get_price_volume_data(
            sector,
            start_date=end_date - datetime.timedelta(days=30),
            end_date=end_date
        )

        if data.empty:
            continue

        data = signal_generator.calculate_volume_indicators(data)
        data = signal_generator.generate_buy_signals(data)

        # 최근 5일 내 매수 신호가 있는지 확인
        recent_data = data.tail(5)
        if recent_data['buy_signal'].any():
            recommended_sectors.append({
                'symbol': sector,
                'name': collector.us_sector_etfs.get(sector, sector),
                'latest_price': float(data['adjusted_close'].iloc[-1]),
                'latest_volume': float(data['volume'].iloc[-1]),
                'relative_strength': float(normalized_rs[sector].iloc[-1]),
                'signal_date': recent_data[recent_data['buy_signal']].index[-1].strftime('%Y-%m-%d')
            })

    session.close()
    return jsonify({
        'recommendations': recommended_sectors,
        'update_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


if __name__ == '__main__':
    # 템플릿 디렉토리 생성
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    # HTML 템플릿 생성
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sector ETF Analysis Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .card {
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .recommendation-card {
            border-left: 5px solid #28a745;
        }
    </style>
</head>
<body>
    <div class="container-fluid mt-4">
        <h1 class="text-center mb-4">Sector ETF Analysis Dashboard</h1>

        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Relative Strength Chart</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="rsChart" height="300"></canvas>
                    </div>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0">Top Sectors</h5>
                    </div>
                    <div class="card-body">
                        <div id="topSectors"></div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">Current Recommendations</h5>
                    </div>
                    <div class="card-body">
                        <div id="recommendations"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-warning">
                        <h5 class="mb-0">Trading Signals</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label for="symbolSelect" class="form-label">Select Symbol:</label>
                            <select id="symbolSelect" class="form-select"></select>
                        </div>
                        <canvas id="signalChart" height="300"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Load ETF sectors and populate dropdown
        fetch('/api/etf_sectors')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('symbolSelect');
                const us_sectors = data.US;

                for (const [symbol, sector] of Object.entries(us_sectors)) {
                    const option = document.createElement('option');
                    option.value = symbol;
                    option.textContent = `${symbol} - ${sector}`;
                    select.appendChild(option);
                }

                // Load signals for first symbol
                if (select.options.length > 0) {
                    loadSignals(select.options[0].value);
                }
            });

        // Load top sectors
        function loadTopSectors() {
            fetch('/api/top_sectors')
                .then(response => response.json())
                .then(data => {
                    const topSectorsDiv = document.getElementById('topSectors');
                    topSectorsDiv.innerHTML = '';

                    data.top_sectors.forEach((sector, index) => {
                        const sectorName = data.sector_names[sector];
                        const div = document.createElement('div');
                        div.className = 'mb-2 p-2 bg-light rounded';
                        div.innerHTML = `<strong>${index + 1}. ${sector}</strong> - ${sectorName}`;
                        topSectorsDiv.appendChild(div);
                    });
                });
        }

        // Load recommendations
        function loadRecommendations() {
            fetch('/api/recommendations')
                .then(response => response.json())
                .then(data => {
                    const recommendationsDiv = document.getElementById('recommendations');
                    recommendationsDiv.innerHTML = '';

                    if (data.recommendations.length === 0) {
                        recommendationsDiv.innerHTML = '<p>No clear buy recommendations at this time.</p>';
                        return;
                    }

                    data.recommendations.forEach(rec => {
                        const div = document.createElement('div');
                        div.className = 'recommendation-card card mb-2';
                        div.innerHTML = `
                            <div class="card-body py-2">
                                <h6>${rec.symbol} - ${rec.name}</h6>
                                <p class="mb-1">Price: $${rec.latest_price.toFixed(2)}</p>
                                <p class="mb-1">Rel. Strength: ${rec.relative_strength.toFixed(2)}</p>
                                <p class="mb-0 text-success"><small>Signal Date: ${rec.signal_date}</small></p>
                            </div>
                        `;
                        recommendationsDiv.appendChild(div);
                    });

                    const updateTimeDiv = document.createElement('div');
                    updateTimeDiv.className = 'mt-2 text-muted';
                    updateTimeDiv.innerHTML = `<small>Last updated: ${data.update_time}</small>`;
                    recommendationsDiv.appendChild(updateTimeDiv);
                });
        }

        // Load relative strength data
        function loadRelativeStrength() {
            fetch('/api/relative_strength')
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('rsChart').getContext('2d');

                    const datasets = [];
                    const colors = [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                        '#FF9F40', '#8BC34A', '#FF5722', '#3F51B5', '#607D8B',
                        '#E91E63', '#9C27B0'
                    ];

                    let colorIndex = 0;
                    for (const [symbol, values] of Object.entries(data.normalized_data)) {
                        datasets.push({
                            label: symbol,
                            data: values,
                            borderColor: colors[colorIndex % colors.length],
                            backgroundColor: 'transparent',
                            pointRadius: 0,
                            borderWidth: 2
                        });
                        colorIndex++;
                    }

                    new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: data.dates,
                            datasets: datasets
                        },
                        options: {
                            responsive: true,
                            interaction: {
                                mode: 'index',
                                intersect: false,
                            },
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Normalized Relative Strength (Z-Score)'
                                },
                                tooltip: {
                                    mode: 'index',
                                    intersect: false
                                }
                            },
                            scales: {
                                x: {
                                    ticks: {
                                        maxTicksLimit: 10
                                    }
                                },
                                y: {
                                    grid: {
                                        drawOnChartArea: true
                                    }
                                }
                            }
                        }
                    });
                });
        }

        // Load signals for a specific symbol
        function loadSignals(symbol) {
            fetch(`/api/signals/${symbol}`)
                .then(response => response.json())
                .then(data => {
                    const ctx = document.getElementById('signalChart').getContext('2d');

                    // Destroy existing chart if it exists
                    if (window.signalChartInstance) {
                        window.signalChartInstance.destroy();
                    }

                    // Create buy signal points
                    const buySignalPoints = data.buy_signals.map(date => {
                        const index = data.dates.indexOf(date);
                        return index >= 0 ? data.price[index] : null;
                    });

                    // Create sell signal points
                    const sellSignalPoints = data.sell_signals.map(date => {
                        const index = data.dates.indexOf(date);
                        return index >= 0 ? data.price[index] : null;
                    });

                    // Create the dataset for buy signals
                    const buySignalData = data.dates.map((date, i) => {
                        return data.buy_signals.includes(date) ? data.price[i] : null;
                    });

                    // Create the dataset for sell signals
                    const sellSignalData = data.dates.map((date, i) => {
                        return data.sell_signals.includes(date) ? data.price[i] : null;
                    });

                    window.signalChartInstance = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: data.dates,
                            datasets: [
                                {
                                    label: 'Price',
                                    data: data.price,
                                    borderColor: '#3498DB',
                                    backgroundColor: 'transparent',
                                    pointRadius: 0,
                                    borderWidth: 2,
                                    yAxisID: 'y'
                                },
                                {
                                    label: 'Price MA',
                                    data: data.price_ma,
                                    borderColor: '#FF9F40',
                                    backgroundColor: 'transparent',
                                    pointRadius: 0,
                                    borderWidth: 1,
                                    borderDash: [5, 5],
                                    yAxisID: 'y'
                                },
                                {
                                    label: 'Buy Signals',
                                    data: buySignalData,
                                    borderColor: '#2ECC71',
                                    backgroundColor: '#2ECC71',
                                    pointRadius: 6,
                                    pointStyle: 'triangle',
                                    pointRotation: 180,
                                    showLine: false,
                                    yAxisID: 'y'
                                },
                                {
label: 'Sell Signals',
                                    data: sellSignalData,
                                    borderColor: '#E74C3C',
                                    backgroundColor: '#E74C3C',
                                    pointRadius: 6,
                                    pointStyle: 'triangle',
                                    showLine: false,
                                    yAxisID: 'y'
                                },
                                {
                                    label: 'Volume',
                                    data: data.volume,
                                    borderColor: '#9B59B6',
                                    backgroundColor: 'rgba(155, 89, 182, 0.3)',
                                    pointRadius: 0,
                                    borderWidth: 1,
                                    type: 'bar',
                                    yAxisID: 'y1'
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            interaction: {
                                mode: 'index',
                                intersect: false,
                            },
                            plugins: {
                                title: {
                                    display: true,
                                    text: `${symbol} Trading Signals`
                                },
                                tooltip: {
                                    mode: 'index',
                                    intersect: false
                                }
                            },
                            scales: {
                                x: {
                                    ticks: {
                                        maxTicksLimit: 10
                                    }
                                },
                                y: {
                                    type: 'linear',
                                    display: true,
                                    position: 'left',
                                    title: {
                                        display: true,
                                        text: 'Price'
                                    }
                                },
                                y1: {
                                    type: 'linear',
                                    display: true,
                                    position: 'right',
                                    grid: {
                                        drawOnChartArea: false
                                    },
                                    title: {
                                        display: true,
                                        text: 'Volume'
                                    }
                                }
                            }
                        }
                    });
                });
        }

        // Event listener for symbol select
        document.getElementById('symbolSelect').addEventListener('change', function() {
            loadSignals(this.value);
        });

        // Load initial data
        loadRelativeStrength();
        loadTopSectors();
        loadRecommendations();

        // Refresh data every 5 minutes
        setInterval(() => {
            loadTopSectors();
            loadRecommendations();
        }, 300000); // 5 minutes
    </script>
</body>
</html>
        ''')

    app.run(debug=True, port=5000)
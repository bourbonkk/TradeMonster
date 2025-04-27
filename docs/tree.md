# 필요한 라이브러리 설치
pip install yfinance pandas numpy matplotlib scikit-learn sqlalchemy sqlite3

# 기본 프로젝트 구조
 TradeMonster/  
 ├── data/                     # 데이터 저장소  
 ├── database/                 # 데이터베이스 관련 코드  
 │   ├── __init__.py           
 │   ├── models.py             # 데이터베이스 모델  
 │   └── db_operations.py      # 데이터베이스 CRUD 작업  
 ├── data_collection/          # 데이터 수집 코드  
 │   ├── __init__.py  
 │   ├── etf_collector.py      # ETF 데이터 수집기  
 │   └── market_collector.py   # 시장 데이터 수집기  
 ├── analysis/                 # 분석 코드  
 │   ├── __init__.py  
 │   ├── normalization.py      # 정규화 함수들  
 │   ├── indicators.py         # 기술적 지표 계산  
 │   └── relative_strength.py  # 상대 강도 분석  
 ├── visualization/            # 시각화 코드  
 │   ├── __init__.py  
 │   └── charts.py             # 차트 그리기 함수들  
 ├── strategy/                 # 투자 전략 구현  
 │   ├── __init__.py  
 │   ├── signals.py            # 매매 신호 생성  
 │   └── backtesting.py        # 백테스팅 기능  
 ├── config.py                 # 설정 파일  
 └── main.py                   # 메인 실행 파일  
ETFSectors (섹터 ETF 정보)
- etf_id (PK)
- symbol
- name
- sector
- description
- expense_ratio
- inception_date
- assets_under_management
- last_updated

ETFComponents (ETF에 포함된 종목 정보)
- component_id (PK)
- etf_id (FK)
- stock_symbol
- stock_name
- weight_percentage
- sector
- industry
- last_updated

PriceData (가격 데이터)
- price_id (PK)
- symbol (ETF 또는 종목 심볼)
- date
- open
- high
- low
- close
- adjusted_close
- volume
- is_etf (ETF인지 개별 종목인지 구분)

MarketData (추가적인 시장 지표)
- market_data_id (PK)
- date
- indicator_name (e.g., 'VIX', 'Fed_Rate', 'CPI')
- indicator_value

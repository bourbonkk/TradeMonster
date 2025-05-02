# 미국 ETF 매핑
from database import GlobalSectorType


US_ETF_MAPPING = {
    'XLK': GlobalSectorType.TECHNOLOGY,  # Technology Select Sector SPDR (1998-12-16)
    'SMH': GlobalSectorType.SEMICONDUCTOR,  # VanEck Semiconductor ETF (2000-05-05, 현재 버전은 2011-12 리뉴얼)
    'XLF': GlobalSectorType.FINANCIAL,  # Financial Select Sector SPDR (1998-12-16)
    'KBE': GlobalSectorType.BANKING,  # SPDR S&P Bank ETF (2005-11-08)
    'XLV': GlobalSectorType.HEALTHCARE,  # Health Care Select Sector SPDR (1998-12-16)
    'IBB': GlobalSectorType.BIOTECHNOLOGY,  # iShares Biotechnology ETF (2001-02-05)
    'XLP': GlobalSectorType.CONSUMER_STAPLES,  # Consumer Staples Select Sector SPDR (1998-12-16)
    'XLY': GlobalSectorType.CONSUMER_DISCRETIONARY,  # Consumer Discretionary Select Sector SPDR (1998-12-16)
    'XLC': GlobalSectorType.COMMUNICATION,  # Communication Services Select Sector SPDR (2018-06-18)
    'XLI': GlobalSectorType.INDUSTRIALS,  # Industrial Select Sector SPDR (1998-12-16)
    'CARZ': GlobalSectorType.AUTOMOTIVE,  # First Trust S-Network Future Vehicles & Tech ETF (2011-05-09)
    'XLE': GlobalSectorType.ENERGY,  # Energy Select Sector SPDR (1998-12-16)
    'XLB': GlobalSectorType.MATERIALS,  # Materials Select Sector SPDR (1998-12-16)
    'XLU': GlobalSectorType.UTILITIES,  # Utilities Select Sector SPDR (1998-12-16)
    'XLRE': GlobalSectorType.REAL_ESTATE,  # Real Estate Select Sector SPDR (2015-10-07)
}

# 한국 ETF 매핑
KR_ETF_MAPPING = {
    '091170': GlobalSectorType.SEMICONDUCTOR,  # KODEX 반도체 (2008-11-24)
    '091160': GlobalSectorType.BANKING,  # KODEX 은행 (2008-11-24)
    '091180': GlobalSectorType.AUTOMOTIVE,  # KODEX 자동차 (2008-11-24)
    '152100': GlobalSectorType.CHEMICALS,  # KODEX 에너지화학 (2012-01-31)
    '244620': GlobalSectorType.BIOTECHNOLOGY,  # KODEX 바이오 (2017-06-29)
    '105780': GlobalSectorType.FINANCIAL,  # TIGER 금융 (2009-11-17)
    '089490': GlobalSectorType.TECHNOLOGY,  # TIGER IT (2008-09-25)
    '143860': GlobalSectorType.HEALTHCARE,  # KBSTAR 헬스케어 (2015-11-18)
    '102780': GlobalSectorType.CONSTRUCTION,  # KODEX 건설 (2009-09-22)
    '102970': GlobalSectorType.STEEL,  # KODEX 철강 (2009-09-22)
    '266370': GlobalSectorType.ENTERTAINMENT,  # KODEX 엔터테인먼트 (2021-07-13)
    '139230': GlobalSectorType.REITS,  # KODEX 부동산 (2009-06-25)
    '140710': GlobalSectorType.MEDIA,  # KODEX 미디어&통신 (2015-10-13)
    '228790': GlobalSectorType.SHIPPING,  # KODEX 해운 (2017-01-31)
    '102960': GlobalSectorType.RETAIL,  # TIGER 소비재 (2009-09-22)
    '227550': GlobalSectorType.INDUSTRIALS,  # TIGER 200 산업재 (2016-12-22)
}


BENCHMARKS = {
    'US': 'SPY',  # S&P 500 ETF (상장일: 1993-01-29)
    'KR': '069500',  # KODEX 200 (상장일: 2002-10-14)
}

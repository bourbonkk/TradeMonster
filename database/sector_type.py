import enum


class GlobalSectorType(enum.Enum):
    # 정보 기술 관련 섹터
    TECHNOLOGY = "Technology"  # 기술 섹터 전체
    SEMICONDUCTOR = "Semiconductor"  # 반도체
    SOFTWARE = "Software"  # 소프트웨어
    HARDWARE = "Hardware"  # 하드웨어

    # 금융 관련 섹터
    FINANCIAL = "Financial"  # 금융 섹터 전체
    BANKING = "Banking"  # 은행
    INSURANCE = "Insurance"  # 보험
    INVESTMENT = "Investment Services"  # 투자 서비스

    # 헬스케어 관련 섹터
    HEALTHCARE = "Healthcare"  # 헬스케어 전체
    PHARMACEUTICALS = "Pharmaceuticals"  # 제약
    BIOTECHNOLOGY = "Biotechnology"  # 바이오테크
    MEDICAL_DEVICES = "Medical Devices"  # 의료기기

    # 소비자 관련 섹터
    CONSUMER_STAPLES = "Consumer Staples"  # 필수소비재
    CONSUMER_DISCRETIONARY = "Consumer Discretionary"  # 임의소비재
    RETAIL = "Retail"  # 소매
    LUXURY = "Luxury Goods"  # 명품

    # 통신 및 미디어
    COMMUNICATION = "Communication Services"  # 통신 서비스
    MEDIA = "Media"  # 미디어
    TELECOM = "Telecommunications"  # 통신
    INTERNET = "Internet Services"  # 인터넷 서비스

    # 산업 관련 섹터
    INDUSTRIALS = "Industrials"  # 산업재 전체
    AEROSPACE_DEFENSE = "Aerospace & Defense"  # 항공우주 및 방위
    CONSTRUCTION = "Construction"  # 건설
    MACHINERY = "Machinery"  # 기계

    # 자동차 관련
    AUTOMOTIVE = "Automotive"  # 자동차 전체
    AUTO_PARTS = "Auto Parts"  # 자동차 부품

    # 에너지 및 자원 관련
    ENERGY = "Energy"  # 에너지 전체
    OIL_GAS = "Oil & Gas"  # 석유 및 가스
    RENEWABLE_ENERGY = "Renewable Energy"  # 재생 에너지

    # 소재 관련
    MATERIALS = "Materials"  # 소재 전체
    CHEMICALS = "Chemicals"  # 화학
    METALS_MINING = "Metals & Mining"  # 금속 및 광업
    STEEL = "Steel"  # 철강

    # 유틸리티 및 부동산
    UTILITIES = "Utilities"  # 유틸리티
    REAL_ESTATE = "Real Estate"  # 부동산
    REITS = "REITs"  # 부동산 투자 신탁

    # 기타 특수 섹터
    ENTERTAINMENT = "Entertainment"  # 엔터테인먼트
    GAMING = "Gaming"  # 게임
    TOURISM = "Tourism & Hospitality"  # 관광 및 호텔
    SHIPPING = "Shipping & Logistics"  # 해운 및 물류
    DEFENSE = "Defense"  # 방위산업
    EDUCATION = "Education"  # 교육

    @classmethod
    def get_by_name(cls, name):
        for sector in cls:
            if sector.value == name:
                return sector
        return None

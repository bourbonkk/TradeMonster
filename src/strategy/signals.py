import pandas as pd
from database.models import PriceData


class VolumeSignalGenerator:
    def __init__(self, db_session):
        self.session = db_session

    def get_price_volume_data(self, symbol, start_date=None, end_date=None):
        """
        특정 심볼의 가격 및 거래량 데이터 로드
        """
        query = self.session.query(
            PriceData.date,
            PriceData.close,
            PriceData.adjusted_close,
            PriceData.volume
        ).filter(PriceData.symbol == symbol)

        if start_date:
            query = query.filter(PriceData.date >= start_date)
        if end_date:
            query = query.filter(PriceData.date <= end_date)

        data = pd.read_sql(query.statement, self.session.bind)
        data.set_index('date', inplace=True)

        return data

    def calculate_volume_indicators(self, data, price_ma_period=20, volume_ma_period=20):
        """
        거래량 지표 계산

        Args:
            data (DataFrame): 가격 및 거래량 데이터
            price_ma_period (int): 가격 이동평균 기간
            volume_ma_period (int): 거래량 이동평균 기간

        Returns:
            DataFrame: 지표가 추가된 데이터프레임
        """
        # 기본 이동평균
        data['price_ma'] = data['adjusted_close'].rolling(window=price_ma_period).mean()
        data['volume_ma'] = data['volume'].rolling(window=volume_ma_period).mean()

        # 상대적 거래량 (현재 거래량 / 평균 거래량)
        data['relative_volume'] = data['volume'] / data['volume_ma']

        # 거래량 변화율
        data['volume_change'] = data['volume'].pct_change()

        # OBV (On-Balance Volume)
        data['obv'] = 0
        data.loc[data['adjusted_close'] > data['adjusted_close'].shift(1), 'obv'] = data['volume']
        data.loc[data['adjusted_close'] < data['adjusted_close'].shift(1), 'obv'] = -data['volume']
        data['obv'] = data['obv'].cumsum()

        # 가격 변동성
        data['price_volatility'] = data['adjusted_close'].rolling(window=price_ma_period).std()

        # 거래량 스파이크 (상위 10% 거래량)
        volume_percentile = data['volume'].quantile(0.9)
        data['volume_spike'] = data['volume'] > volume_percentile

        return data

    def generate_buy_signals(self, data, threshold_volume=1.5, trend_days=5):
        """
        매수 신호 생성

        Args:
            data (DataFrame): 지표가 포함된 데이터프레임
            threshold_volume (float): 거래량 급증 기준 (평균 대비)
            trend_days (int): 상승 추세 확인 기간

        Returns:
            DataFrame: 매수 신호 컬럼이 추가된 데이터프레임
        """
        # 초기화
        data['buy_signal'] = False

        # 가격이 이동평균선 위에 있는지 (상승 추세)
        data['above_ma'] = data['adjusted_close'] > data['price_ma']

        # n일 연속 상승 추세
        data['uptrend'] = data['above_ma'].rolling(window=trend_days).sum() >= trend_days * 0.8

        # 거래량 급증
        data['high_volume'] = data['relative_volume'] > threshold_volume

        # OBV 상승세
        data['obv_increasing'] = data['obv'] > data['obv'].shift(5)

        # 매수 신호: 상승 추세 + 거래량 급증 + OBV 상승
        data['buy_signal'] = (data['uptrend'] & data['high_volume'] & data['obv_increasing'])

        return data

    def generate_sell_signals(self, data, threshold_volume=1.5, trend_days=5):
        """
        매도 신호 생성

        Args:
            data (DataFrame): 지표가 포함된 데이터프레임
            threshold_volume (float): 거래량 급증 기준 (평균 대비)
            trend_days (int): 하락 추세 확인 기간

        Returns:
            DataFrame: 매도 신호 컬럼이 추가된 데이터프레임
        """
        # 초기화
        data['sell_signal'] = False

        # 가격이 이동평균선 아래에 있는지 (하락 추세)
        data['below_ma'] = data['adjusted_close'] < data['price_ma']

        # n일 연속 하락 추세
        data['downtrend'] = data['below_ma'].rolling(window=trend_days).sum() >= trend_days * 0.8

        # 거래량 급증
        data['high_volume'] = data['relative_volume'] > threshold_volume

        # OBV 하락세
        data['obv_decreasing'] = data['obv'] < data['obv'].shift(5)

        # 매도 신호: 하락 추세 + 거래량 급증 + OBV 하락
        data['sell_signal'] = (data['downtrend'] & data['high_volume'] & data['obv_decreasing'])

        return data
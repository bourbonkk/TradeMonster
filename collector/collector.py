import abc
import logging
from typing import Any


logger = logging.getLogger('collector')


class BaseCollector(abc.ABC):
    """데이터 수집을 위한 기본 추상 클래스"""

    @abc.abstractmethod
    def collect(self, *args, **kwargs) -> Any:
        """데이터 수집 실행 메서드"""
        pass

    @abc.abstractmethod
    def validate(self, data: Any) -> bool:
        """수집된 데이터 유효성 검증"""
        pass

    @abc.abstractmethod
    def transform(self, data: Any) -> Any:
        """데이터 변환 메서드"""
        pass

    @abc.abstractmethod
    def save(self, data: Any) -> bool:
        """데이터 저장 메서드"""
        pass

    def run(self, *args, **kwargs) -> bool:
        """전체 수집 프로세스 실행"""
        try:
            data = self.collect(*args, **kwargs)
            if not self.validate(data):
                logger.error("Data validation failed")
                return False

            transformed_data = self.transform(data)
            return self.save(transformed_data)
        except Exception as e:
            logger.exception(f"Error in collection process: {e}")
            return False

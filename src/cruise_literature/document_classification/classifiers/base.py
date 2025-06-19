from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Any


class BaseClassifier(ABC):
    def __int__(self):
        pass

    @abstractmethod
    def preprocessing(self, input_data: List[str]) -> List[str]:
        """Actions happening before train and predict."""
        pass

    @abstractmethod
    def postprocessing(self, predicted_label: List[Any]) -> List[int]:
        """Actions happening after predict."""
        pass

    @abstractmethod
    def train(self, input_data: List[str], true_label: List[int]) -> None:
        pass

    @abstractmethod
    def predict(self, input_data: List[str]) -> List[int]:
        pass

    @staticmethod
    @abstractmethod
    def load_model(file: str) -> BaseClassifier:
        pass

    @abstractmethod
    def save_model(self, file: str) -> None:
        pass

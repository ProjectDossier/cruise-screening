from typing import List, Dict, Union
import random
from .base import BaseClassifier


class DummyClassifier(BaseClassifier):
    def __init__(self):
        pass

    def preprocessing(self, input_data):
        pass

    def predict(self, input_data) -> Dict[str, Union[List[Dict[str, float]], str]]:
        predictions = [{"probability": 1, "label": random.choice([0, 1])} for _ in input_data]
        return {"predictions": predictions, "status": "OK"}

    def postprocessing(self, input_data):
        pass

    def train(self, input_data: List[str], true_labels: List[int]) -> None:
        pass

    @staticmethod
    def load_model(file: str) -> BaseClassifier:
        pass

    def save_model(self, file: str) -> None:
        pass

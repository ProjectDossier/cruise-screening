from __future__ import annotations

import datetime
import os
from typing import List, Any, Tuple, Dict
import re
from .base import BaseClassifier
import fasttext


def write_temp_fasttext_train_file(
    input_data: List[str], outfile: str, labels: List[int]
):
    with open(outfile, "w") as fp:
        for text, label in zip(input_data, labels):
            fp.write(f"__label__{label} {text}\n")


def delete_temp_fasttext_train_file(outfile) -> None:
    os.remove(outfile)


class FastTextClassifier(BaseClassifier):
    temp_file_path: str = None
    model: fasttext.FastText._FastText = None

    def __init__(self):
        super().__init__()
        self.temp_file_path: str = f"tmp_file_fasttext_{datetime.datetime.now()}.txt"

    def postprocessing(self, predicted_label: List[Any]) -> list[dict[str, Any]]:
        return [
            {"probability": prob[0], "label": int(label[0][9:])}
            for label, prob in zip(predicted_label[0], predicted_label[1])
        ]

    def preprocessing(self, input_data: List[str]) -> List[str]:
        input_data = [re.sub(r"[\W]+", " ", elem) for elem in input_data]
        input_data = [re.sub(r"[\n\r\t ]+", " ", elem) for elem in input_data]
        return input_data

    def train(self, input_data: List[str], true_labels: List[int]) -> None:
        input_data = self.preprocessing(input_data=input_data)

        write_temp_fasttext_train_file(
            input_data=input_data, outfile=self.temp_file_path, labels=true_labels
        )
        self.model = fasttext.train_supervised(input=self.temp_file_path, epoch=70)

        delete_temp_fasttext_train_file(self.temp_file_path)

    def predict(self, input_data: List[str]) -> List[Tuple[int, float]]:
        input_data = self.preprocessing(input_data=input_data)
        predictions = self.model.predict(input_data)
        predictions = self.postprocessing(predicted_label=predictions)
        return {"predictions": predictions, "status": "OK"}

    @staticmethod
    def load_model(file: str) -> FastTextClassifier:
        return fasttext.load_model(file)

    def save_model(self, file: str) -> None:
        self.model.save_model(file)

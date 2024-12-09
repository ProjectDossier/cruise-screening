import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from classifiers.binary.fasttext_classifier import FastTextClassifier

router = APIRouter()

class ClassifyInput(BaseModel):
    xy_train: Dict[str, Dict[str, str]]
    x_pred: Dict[str, Dict[str, str]]
    
class ClassifyOutput(BaseModel):
    y_pred: Dict[str, str]
    algorithm_id: str

@router.post("/")
async def classify(data: ClassifyInput) -> ClassifyOutput:
    try:
        xy_train = data.xy_train
        x_pred = data.x_pred

        algorithm = FastTextClassifier()
        algorithm.train(
            input_data=[x["title"] for x in xy_train.values()],
            true_labels=[x["decision"] for x in xy_train.values()],
        )

        predictions = algorithm.predict([x["title"] for x in x_pred.values()])
        return ClassifyOutput(y_pred=predictions, algorithm_id="FastText")
    except Exception as e:
        logging.error(f"Error during classification: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable: Unable to process the request.")

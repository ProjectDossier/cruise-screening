import logging
from fastapi import APIRouter
from pydantic import BaseModel
from externalModels.transformers_model import TransformersModel
from typing import Dict

router = APIRouter()
model = TransformersModel("bigscience/T0_3B")

class QuestionInput(BaseModel):
    text: str

@router.post("/")
async def question(data: QuestionInput) -> Dict[str, str]:
    try:
        response = model.generate_response(data.text)
        logging.debug("text: %s, response: %s", data.text, response)
        return {"response": response, "status": "OK"}
    except Exception as e:
        logging.error(f"Error during question answering: {e}")
        return {"response": "Error", "status": "ERROR"}

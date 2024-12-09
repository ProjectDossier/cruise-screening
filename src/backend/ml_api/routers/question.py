import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from externalModels.transformers_model import TransformersModel
from typing import Dict

router = APIRouter()
model = TransformersModel("bigscience/T0_3B")

class QuestionInput(BaseModel):
    text: str
    
class QuestionResponse(BaseModel):
    response: str

@router.post("/")
async def question(data: QuestionInput) -> QuestionResponse:
    try:
        response = model.generate_response(data.text)
        logging.debug("text: %s, response: %s", data.text, response)
        return QuestionResponse(response=response)
    except Exception as e:
        logging.error(f"Error during question answering: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable: Unable to process the request.")

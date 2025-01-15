import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from external_models.transformers_model import models
from typing import Dict

router = APIRouter()

class QuestionInput(BaseModel):
    text: str
    model: str
    
class QuestionResponse(BaseModel):
    response: str

@router.post("/")
async def question(data: QuestionInput) -> QuestionResponse:
    try:
        model = models[data.model]
        response = model.generate_response(data.text)
        logging.debug("text: %s, response: %s", data.text, response)
        return QuestionResponse(response=response)
    except Exception as e:
        logging.error(f"Error during question answering: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable: Unable to process the request.")

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from external_models.transformers_model import models
from typing import Dict

router = APIRouter()

class SummarizeInputRequest(BaseModel):
    text: str
    model: str
    
class SummarizeOutputResponse(BaseModel):
    response: str
    
@router.post("/")
async def summarize(data: SummarizeInputRequest) -> SummarizeOutputResponse:
    try:
        model = models[data.model]
        summary = model.generate_response(f"Summarize the following text: {data.text}")
        return SummarizeOutputResponse(response=summary)
    except Exception as e:
        logging.error(f"Error during summarization: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable: Unable to process the request.")


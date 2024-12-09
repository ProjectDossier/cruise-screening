import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from externalModels.transformers_model import TransformersModel
from typing import Dict

router = APIRouter()

models = {
    "bigscience/T0_3B" : TransformersModel("bigscience/T0_3B"),
    "google/flan-t5-small" : TransformersModel("google/flan-t5-small"),
    "geektech/flan-t5-base-gpt4-relation" : TransformersModel("geektech/flan-t5-base-gpt4-relation"),
}

class SummarizeInputRequest(BaseModel):
    text: str
    model: str
    
class SummarizeOutputResponse(BaseModel):
    response: str
    
class GetModelsResponse(BaseModel):
    models: list

@router.post("/")
async def summarize(data: SummarizeInputRequest) -> SummarizeOutputResponse:
    try:
        model = models[data.model]
        summary = model.generate_response(f"Summarize the following text: {data.text}")
        return SummarizeOutputResponse(response=summary)
    except Exception as e:
        logging.error(f"Error during summarization: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable: Unable to process the request.")
    
@router.get("/")
async def get_models() -> GetModelsResponse:
    return GetModelsResponse(models=list(models.keys()))

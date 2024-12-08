import logging
from fastapi import APIRouter
from pydantic import BaseModel
from externalModels.transformers_model import TransformersModel
from typing import Dict

router = APIRouter()
model = TransformersModel("bigscience/T0_3B")

class SummarizeInput(BaseModel):
    text: str

@router.post("/")
async def summarize(data: SummarizeInput) -> Dict[str, str]:
    try:
        summary = model.generate_response(f"Summarize the following text: {data.text}")
        return {"response": summary}
    except Exception as e:
        logging.error(f"Error during summarization: {e}")
        return {"error": str(e)}

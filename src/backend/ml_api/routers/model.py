from fastapi import APIRouter
from pydantic import BaseModel
from external_models.transformers_model import models

router = APIRouter()
class GetModelsResponse(BaseModel):
    models: list

@router.get("/")
async def get_models() -> GetModelsResponse:
    return GetModelsResponse(models=list(models.keys()))
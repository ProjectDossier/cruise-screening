from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
# import psutil

from external_models.transformers_model import models, TransformersModel

router = APIRouter()

class ModelConfig(BaseModel):
    model_name: str

MAX_MODELS = 5

# def check_memory():
#     available_memory = psutil.virtual_memory().available / (1024 * 1024)
#     return available_memory

@router.post("/")
async def add_model(config: ModelConfig):
    if len(models) >= MAX_MODELS:
        raise HTTPException(status_code=400, detail="Max model limit reached.")
    # if check_memory() < 1500:
    #     raise HTTPException(status_code=400, detail="Insufficient RAM.")
    if config.model_name in models:
        raise HTTPException(status_code=400, detail="Model already exists.")
    try:
        models[config.model_name] = TransformersModel(config.model_name)
        return {"status": "Model added", "model_name": config.model_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
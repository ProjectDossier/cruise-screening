from fastapi import FastAPI
from routers import classify, summarize, question
from utils.logging_config import setup_logging

setup_logging()

app = FastAPI()

app.include_router(classify.router, prefix="/classify", tags=["Classification"])
app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])
app.include_router(question.router, prefix="/question", tags=["Question Answering"])

@app.get("/")
async def index():
    return {
        "message": "Machine learning API",
        "routes": [
            {"path": "/classify", "methods": ["POST"]},
            {"path": "/summarize", "methods": ["POST"]},
            {"path": "/question", "methods": ["POST"]},
        ],
    }

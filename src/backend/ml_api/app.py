from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from routers import classify, summarize, question, model
from utils.logging_config import setup_logging

setup_logging()

app = FastAPI()

app.include_router(classify.router, prefix="/classify", tags=["Classification"])
app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])
app.include_router(question.router, prefix="/question", tags=["Question Answering"])
app.include_router(model.router, prefix="/model", tags=["Models"])

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index():
    return """
    <html>
        <head>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    font-family: 'Apple System', sans-serif;
                    text-align: center;
                }
                h1 {
                    font-size: 4em;
                    margin-bottom: 20px;
                }
                a {
                    font-size: 1.5em;
                    color: #007bff;
                    text-decoration: none;
                    font-weight: bold;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div>
                <h1>Machine Learning API</h1>
                <a href="/docs">Go to API Documentation</a>
            </div>
        </body>
    </html>
    """

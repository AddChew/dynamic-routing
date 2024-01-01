from pydantic import BaseModel
from fastapi.security.api_key import APIKeyHeader
from fastapi import FastAPI, Depends, Security, HTTPException, status


api_key = "example"
api_key_header = APIKeyHeader(name = 'accessKey', auto_error = False)
app = FastAPI()


class Prediction(BaseModel):
    label: str
    score: float


async def verify_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != api_key:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Missing or invalid accessKey in request header.'
        )


@app.post(
        path = "/model",
        tags = ["Model Inference"],
        summary = "Model Inference on input data",
        dependencies = [Depends(verify_api_key)]
)
async def predict(text: str) -> Prediction:
    return {
        "label": "positive",
        "score": 0.99
    }
from fastapi import FastAPI
from src.projects import router as proj_router


app = FastAPI()
app.include_router(proj_router)
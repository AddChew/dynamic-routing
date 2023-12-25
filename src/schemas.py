from pydantic import BaseModel
from src.models import Users, Projects
from tortoise.contrib.pydantic import pydantic_model_creator


class Message(BaseModel):
    detail: str


class Token(BaseModel):
    access_token: str
    token_type: str


User = pydantic_model_creator(Users, name = "User")
Project = pydantic_model_creator(Projects, name = "Project")
from pydantic import BaseModel
from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

from src.models import Users, Projects


class Message(BaseModel):
    """
    Message pydantic model.
    """
    detail: str


class Token(BaseModel):
    """
    Token pydantic model.
    """
    access_token: str
    token_type: str


Tortoise.init_models(["src.models"], "models")
User = pydantic_model_creator(Users, name = "User")
Project = pydantic_model_creator(Projects, name = "Project")

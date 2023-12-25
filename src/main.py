import os

from typing import Annotated, List
from importlib import import_module
from src.models import Users, Projects

from src.schemas import Token, User, Project
from tortoise.exceptions import IntegrityError
from tortoise.contrib.fastapi import register_tortoise

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Form
from src.auth import authenticate_user, create_access_token, pwd_context, get_current_user


app = FastAPI()
auth_router = APIRouter(
    prefix = "/auth",
    tags = ["Authentication"]
)
proj_router = APIRouter(
    prefix = "/{username}",
    tags = ["Projects"]
)


@auth_router.post("/register")
async def register(username: Annotated[str, Form()], password: Annotated[str, Form()]) -> User:
    try:
        user = await Users.create(
            username = username,
            hashed_password = pwd_context.hash(password)
        )
        return await User.from_tortoise_orm(user)
    except IntegrityError:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "User already exists."
        )


@auth_router.post("/login", include_in_schema = False)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = await authenticate_user(
        username = form_data.username, 
        password = form_data.password
    )
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password."
        )
    access_token = create_access_token(data = {"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@proj_router.get("/")
async def read_projects(username: str, current_user: Annotated[User, Depends(get_current_user)]) -> List[Project]:
    if username != current_user.username:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Insufficient permissions."
        )
    return await current_user.projects.all()


app.include_router(auth_router)
app.include_router(proj_router)
register_tortoise(
    app,
    db_url = "sqlite://db.sqlite3",
    modules = {"models": ["src.models"]},
    generate_schemas = True,
    add_exception_handlers = True,
)
    

# @proj_router.post("/")
# async def create_project(username, project):
#     module = import_module(f"src.users.{username}.{project}.app")
#     app.mount(f"/{username}/{project}", module.app)
#     return f"create {username} project {project}!"


# @proj_router.put("/{project}")
# async def update_project(username, project):
#     return f"update {username} project {project}!"


# @proj_router.delete("/{project}")
# async def delete_project(username, project):
#     return f"delete {username} project {project}!"
import os

from typing import Annotated, List
from contextlib import asynccontextmanager
from importlib import import_module, reload
from starlette.routing import Mount

from tortoise import Tortoise
from tortoise.exceptions import IntegrityError

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Form, UploadFile, File

from src import projects as proj
from src.models import Users, Projects
from src.schemas import Token, User, Project
from src.auth import authenticate_user, create_access_token, pwd_context, get_current_user


ROOT_MODULE = os.getenv("root_module", "src")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Setup and tear down Tortoise-ORM inside a FastAPI app, upon app start up and shut down events.
    
    Args:
        app (FastAPI): FastAPI app to bind Tortoise-ORM to.
    """
    await Tortoise.init(
        db_url = os.getenv("db_url", "sqlite://db.sqlite3"),
        modules = {"models": ["src.models"]}
    )
    await Tortoise.generate_schemas()
    projects = await Projects.all().prefetch_related("owner")

    for project in projects:
        project_name = project.name
        username = project.owner.username

        module = import_module(f"{ROOT_MODULE}.users.{username}.{project_name}.app")
        app.mount(f"/{username}/{project_name}", module.app)

    yield
    await Tortoise.close_connections()


app = FastAPI(
    title = "Dynamic Routing",
    description = "API Documentation for Dynamic Routing Service.",
    lifespan = lifespan,
)
auth_router = APIRouter(
    prefix = "/auth",
    tags = ["Authentication"]
)
proj_router = APIRouter(
    prefix = "/{username}",
    tags = ["Projects"]
)


def unmount_app(path: str):
    """
    Remove route from app.

    Args:
        path (str): Path of route to be removed.
    """
    global app
    for index, route in enumerate(app.routes):
        if isinstance(route, Mount) and route.path == path:
            del app.routes[index]
            break


@auth_router.post("/register")
async def register(username: Annotated[str, Form()], password: Annotated[str, Form(format = "password")]) -> User:
    """
    Register new user.
    """
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
    """
    Login user and return access token.
    """
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
async def read_projects(current_user: Annotated[User, Depends(get_current_user)]) -> List[Project]:
    """
    Read list of projects belonging to current user.
    """
    projects = await current_user.projects.all()
    return [await Project.from_tortoise_orm(project) for project in projects]


@proj_router.post("/")
async def create_project(
    project_name: Annotated[str, Form()],
    project_script: Annotated[UploadFile, File(description = "Project app script (i.e. app.py)")],
    current_user: Annotated[User, Depends(get_current_user)]
    ) -> Project:
    """
    Create a new project.
    """
    try:
        project = await Projects.create(
            name = project_name,
            owner = current_user
        )

    except IntegrityError:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "Project already exists."
        )

    username = current_user.username

    proj.create_project(
        username = username,
        project_name = project_name
    )

    await proj.save_file(
        username = username,
        project_name = project_name,
        file = project_script,
    )

    module = import_module(f"{ROOT_MODULE}.users.{username}.{project_name}.app")
    app.mount(f"/{username}/{project_name}", module.app)

    return await Project.from_tortoise_orm(project)


@proj_router.put("/{project_name}")
async def update_project(
    project: Annotated[Project, Depends(proj.get_project)],
    project_script: Annotated[UploadFile, File(description = "Project app script (i.e. app.py)")],
    ) -> Project:
    """
    Update an existing project.
    """
    username = project.owner.username
    project_name = project.name

    await proj.save_file(
        username = username,
        project_name = project_name,
        file = project_script,
    )

    mount_path = f"/{username}/{project_name}"
    unmount_app(path = mount_path)

    module = reload(import_module(f"{ROOT_MODULE}.users.{username}.{project_name}.app"))
    app.mount(f"/{username}/{project_name}", module.app)

    return await Project.from_tortoise_orm(project)


@proj_router.delete("/{project_name}")
async def delete_project(project: Annotated[Project, Depends(proj.get_project)]) -> List[Project]:
    """
    Delete an existing project.
    """
    current_user = project.owner
    username = current_user.username
    project_name = project.name

    mount_path = f"/{username}/{project_name}"
    unmount_app(path = mount_path)

    await project.delete()
    proj.delete_project(
        username = username,
        project_name = project_name,
    )

    projects = await current_user.projects.all()
    if not projects:
        proj.delete_user(username = username)

    return [Project.from_tortoise_orm(project) for project in projects]


app.include_router(auth_router)
app.include_router(proj_router)


# TODO: migrate to postgres from sqlite
# TODO: setup docker and docker compose
# TODO: update readme

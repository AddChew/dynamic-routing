from src import projects as proj
from typing import Annotated, List

from starlette.routing import Mount
from src.models import Users, Projects
from importlib import import_module, reload

from src.schemas import Token, User, Project
from tortoise.exceptions import IntegrityError
from tortoise.contrib.fastapi import register_tortoise

from fastapi.security import OAuth2PasswordRequestForm
from src.auth import authenticate_user, create_access_token, pwd_context, get_current_user
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Form, UploadFile, File


app = FastAPI(
    title = "Dynamic Routing",
    description = "API Documentation for Dynamic Routing Service.",
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
    global app
    for index, route in enumerate(app.routes):
        if isinstance(route, Mount) and route.path == path:
            del app.routes[index]
            break


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
async def read_projects(current_user: Annotated[User, Depends(get_current_user)]) -> List[Project]:
    projects = await current_user.projects.all()
    return [Project.from_tortoise_orm(project) for project in projects]


@proj_router.post("/")
async def create_project(
    project_name: Annotated[str, Form()], 
    project_script: Annotated[UploadFile, File(description = "Project app script (i.e. app.py)")], 
    current_user: Annotated[User, Depends(get_current_user)]
    ) -> Project:
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

    module = import_module(f"src.users.{username}.{project_name}.app")
    app.mount(f"/{username}/{project_name}", module.app)

    return await Project.from_tortoise_orm(project)


@proj_router.put("/{project_name}")
async def update_project(
    project: Annotated[Project, Depends(proj.get_project)], 
    project_script: Annotated[UploadFile, File(description = "Project app script (i.e. app.py)")], 
    ) -> Project:
    username = project.owner.username
    project_name = project.name

    await proj.save_file(
        username = username,
        project_name = project_name, 
        file = project_script,
    )

    mount_path = f"/{username}/{project_name}"
    unmount_app(path = mount_path)

    module = reload(import_module(f"src.users.{username}.{project_name}.app"))
    app.mount(f"/{username}/{project_name}", module.app)

    return await Project.from_tortoise_orm(project)


@proj_router.delete("/{project_name}")
async def delete_project(project: Annotated[Project, Depends(proj.get_project)]) -> List[Project]:
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
register_tortoise(
    app,
    db_url = "sqlite://db.sqlite3",
    modules = {"models": ["src.models"]},
    generate_schemas = True,
    add_exception_handlers = True,
)

# TODO: logic to mount and regenerate all the endpoints when app restarts
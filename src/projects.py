import os
import aiofiles

from src.schemas import User
from typing import Annotated
from src.models import Projects

from src.auth import get_current_user
from fastapi import UploadFile, Depends, HTTPException, status


USERS_DIR = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))), "users")


def create_project(username: str, project_name: str):
    user_dir = os.path.join(USERS_DIR, username)
    project_dir = os.path.join(user_dir, project_name)

    os.makedirs(project_dir, exist_ok = True)
    
    init_file = "__init__.py"
    user_init = os.path.join(user_dir, init_file)
    project_init = os.path.join(project_dir, init_file)

    if not os.path.isfile(user_init):
        with open(user_init, "w") as f:
            pass

    if not os.path.isfile(project_init):
        with open(project_init, "w") as f:
            pass


async def save_file(username: str, project_name: str, file: UploadFile):
    save_path = os.path.join(USERS_DIR, username, project_name, "app.py")
    async with aiofiles.open(save_path, "wb") as f:
        while content := await file.read(1024):
            await f.write(content)


async def get_project(project_name: str, current_user: Annotated[User, Depends(get_current_user)]):
    project = await Projects.get_or_none(
        name = project_name,
        owner = current_user,
    )
    if project is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Project does not exist."
        )
    await project.fetch_related("owner")
    return project
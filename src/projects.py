import os
import shutil

from typing import Annotated
import aiofiles
from fastapi import UploadFile, Depends, HTTPException, status

from src.schemas import User
from src.models import Projects
from src.auth import get_current_user


users_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))), "users")


def create_project(username: str, project_name: str):
    """
    Create project folder and its init file.

    Args:
        username (str): Username of project owner.
        project_name (str): Name of project.
    """
    user_dir = os.path.join(users_dir, username)
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
    """
    Save uploaded file to disk.

    Args:
        username (str): Username of project owner.
        project_name (str): Name of project.
        file (UploadFile): Uploaded file.
    """
    save_path = os.path.join(users_dir, username, project_name, "app.py")
    async with aiofiles.open(save_path, "wb") as f:
        while content := await file.read(1024):
            await f.write(content)


async def get_project(project_name: str, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve project based on project name and owner.

    Args:
        project_name (str): Name of project to retrieve.
        current_user (Annotated[User, Depends): Current authenticated user.

    Raises:
        HTTPException: Raised when project does not exist.

    Returns:
        QuerySetSingle[Projects]: Project object.
    """
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


def delete_project(username: str, project_name: str):
    """
    Delete project folder.

    Args:
        username (str): Username of project owner.
        project_name (str): Name of project to delete.
    """
    project_dir = os.path.join(users_dir, username, project_name)
    shutil.rmtree(path = project_dir, ignore_errors = True)


def delete_user(username: str):
    """
    Delete user folder.

    Args:
        username (str): Name of folder to delete.
    """
    user_dir = os.path.join(users_dir, username)
    shutil.rmtree(path = user_dir, ignore_errors = True)

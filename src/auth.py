from typing import Annotated
from datetime import datetime, timedelta
from jose import jwt, JWTError

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from src.models import Users


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "401be69b6314c2abcd9a0a9a2f52a09a4777f132a10f9e3cd6885fe8c126bfe6"


pwd_context = CryptContext(
    schemes = ["bcrypt"],
    deprecated = "auto"
)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl = "auth/login"
)


async def authenticate_user(username: str, password: str):
    """
    Authenticate user.

    Args:
        username (str): User name for authentication.
        password (str): Password for authentication.

    Returns:
        QuerySetSingle[Users | None]: User object if authentication is successful else None.
    """
    user = await Users.get_or_none(username = username)
    if user is None:
        return None

    if not pwd_context.verify(password, user.hashed_password):
        return None

    return user


def create_access_token(data: dict) -> str:
    """
    Generate JSON web token.

    Args:
        data (dict): Data to encode for the generation of JSON web token.

    Returns:
        str: Encoded JSON web token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt


async def get_current_user(username: str, token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Retrieve current user.

    Args:
        username (str): Username.
        token (Annotated[str, Depends): Access token.

    Raises:
        credentials_exception: Raised when credentials are invalid.
        HTTPException: Raised when user has insufficient permissions.

    Returns:
        QuerySetSingle[Users]: User object.
    """
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Invalid credentials."
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        token_username = payload.get("sub")
        if token_username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    if username != token_username:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Insufficient permissions."
        )

    user = await Users.get_or_none(
        username = username
    )
    if user is None:
        raise credentials_exception
    return user

from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models.user import User
from app.api.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token",
    auto_error=False
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


# Get current user
def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    # Convert to integer user_id
    user_id = int(token_data.sub)
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


# Current user
CurrentUser = Annotated[User, Depends(get_current_user)]


# Get current user optional, if token is None, return None. It is used for anonymous user - guest.
def get_current_user_optional(
    session: SessionDep, token: TokenDep | None = Depends(reusable_oauth2)
) -> User | None:
    if token is None:
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        # If the token is invalid, we can treat it as an anonymous user.
        return None

    user_id = int(token_data.sub)
    user = session.get(User, user_id)
    if not user or not user.is_active:
        # If user not found or inactive, treat as an anonymous user.
        return None
    return user


# Current user optional, if token is None, return None. It is used for anonymous user - guest.
CurrentUserOptional = Annotated[User | None, Depends(get_current_user_optional)]


# Get current active superuser
def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
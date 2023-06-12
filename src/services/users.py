import logging
import uuid
from logging import config as logging_config
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from core.config import app_settings
from core.logger import LOGGING
from models.users import User, get_user_db

logging_config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = app_settings.jwt_secret
    verification_token_secret = app_settings.jwt_secret

    async def on_after_register(
            self, user: User, request: Optional[Request] = None
    ):
        logger.info(f'User {user.id} has registered.')

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(
            f'User {user.id} has forgot their password. Reset token: {token}'
        )

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(
            f'Verification requested for user {user.id}. '
            f'Verification token: {token}'
        )


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=app_settings.jwt_secret,
        lifetime_seconds=app_settings.token_lifetime
    )


auth_backend = AuthenticationBackend(
    name='jwt', transport=bearer_transport, get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager, [auth_backend]
)

current_active_user = fastapi_users.current_user(active=True)

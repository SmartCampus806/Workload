from typing import Tuple

from typing import Optional

import bcrypt

from src.dtos import UserCreate
from src.exceptions import MyException
from src.services import UserService
from src.services.jwt_token_service import JWTService
from src.utils.logger import Logger


class AuthService:
    def __init__(self, token_service: JWTService, user_service: UserService, log: Logger):
        self.log = log
        self.user_service = user_service
        self.token_service = token_service

    async def register_user(self, user: UserCreate) -> Tuple[str, str]:
        user = await self.user_service.create_user(user_dto=user)
        access = await self.token_service.create_access_token(user_id=user.id)
        refresh = await self.token_service.create_refresh_token(user_id=user.id)
        return access, refresh

    async def login(self, email: str, password: str) -> Tuple[str, str]:
        user = await self.user_service.get_by_email(email=email)
        if not user:
            raise MyException("User not found")
        if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password):
            raise MyException("Password incorrect")

        access = await self.token_service.create_access_token(user_id=user.id)
        await self.token_service.clear_refresh_tokens(user_id=user.id)
        refresh = await self.token_service.create_refresh_token(user_id=user.id)
        return access, refresh

    async def refresh(self, refresh_token: str) -> Optional[Tuple[str, str]]:
        refresh_token = await self.token_service.find_refresh_token(refresh_token)
        if refresh_token is None:
            raise MyException("Refresh Token not found")

        await self.token_service.clear_refresh_tokens(user_id=refresh_token.user_id)
        refresh = await self.token_service.create_refresh_token(user_id=refresh_token.user_id)
        access = await self.token_service.create_access_token(user_id=refresh_token.user_id)
        return access, refresh

    async def logout(self, user_id: int) -> None:
        await self.token_service.clear_refresh_tokens(user_id=user_id)

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any

from src.exceptions import MyException
from src.models import RefreshToken
from src.repositories.token_repository import RefreshTokenRepository
from src.repositories.user_repository import UserRepository
from src.utils.configuration import AppConfig


class JWTService:
    def __init__(self, refresh_token_repository: RefreshTokenRepository, user_repository: UserRepository ,config: AppConfig):
        self.secret_key = config.jwt.secret
        self.algorithm = config.jwt.algorithm
        self.expires_delta_access = timedelta(seconds=config.jwt.expires_delta_access)
        self.expires_delta_refresh = timedelta(seconds=config.jwt.expires_delta_refresh)
        self.refresh_token_repository = refresh_token_repository
        self.user_repository = user_repository

    async def create_access_token(self, user_id: int) -> str:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise MyException("User not found, pleas login")
        expire = datetime.utcnow() + self.expires_delta_access
        to_encode = {'sub' : user_id,
                     'role': user.role,
                     'exp' : expire}
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def create_refresh_token(self, user_id: int) -> str:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise MyException("User not found")
        expire = datetime.utcnow() + self.expires_delta_refresh
        to_encode = {"sub": user_id, 'role': user.role, "exp": expire}
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        await self.refresh_token_repository.create_token(RefreshToken(user_id=user_id, expired_at=expire, token=token))
        return token

    async def clear_refresh_tokens(self, user_id: int) -> None:
        await self.refresh_token_repository.delete_tokens_by_user(user_id=user_id)

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")

    async def find_refresh_token(self, token: str) -> RefreshToken:
        return await self.refresh_token_repository.get_by_token(token=token)

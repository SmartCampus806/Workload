from src.dtos import UserCreate, UserDto
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.utils.logger import Logger


class UserService:

    def __init__(self, user_repo: UserRepository, log: Logger):
        self.repo = user_repo
        self.log = log

    async def create_user(self, user_dto: UserCreate) -> User:
        return await self.repo.create_user(User(email=user_dto.email, hashed_password=user_dto.password))

    async def get_by_id(self, id: int) -> User:
        return await self.repo.get_by_id(id)

    async def get_by_email(self, email: str) -> User:
        return await self.repo.get_by_email(email)

from src.dtos.create_dtos import CreateGroup
from src.models import Groups
from src.repositories import GroupRepository
from src.utils import map_dto_to_model
from src.utils.logger import Logger


class GroupService:
    def __init__(self, group_repository: GroupRepository, log: Logger):
        self.group_repository = group_repository
        self.log = log

    async def create_lesson(self, dto: CreateGroup):
        model = map_dto_to_model(dto, Groups())
        return await self.group_repository.create(model)

    async def get_by_id(self, id: int) -> Groups:
        return await self.group_repository.get_by_id(id)

    async def get_by_name(self, name: str) -> Groups:
        return await self.group_repository.get_by_name(name)

    async def get_by_name_like(self, name: str) -> list[Groups]:
        return await self.group_repository.get_by_name_like(name)

    async def get_all(self) -> list[Groups]:
        return await self.group_repository.get_all()

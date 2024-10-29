from src.dtos.create_dtos import CreateLesson
from src.models import Lesson
from src.repositories import LessonRepository
from src.utils import map_dto_to_model
from src.utils.logger import Logger


class LessonService:
    def __init__(self, lesson_repository: LessonRepository, log: Logger):
        self.lesson_repository = lesson_repository
        self.log = log

    async def create_lesson(self, dto: CreateLesson):
        model = map_dto_to_model(dto, Lesson())
        return await self.lesson_repository.create(model)

    async def get_by_id(self, id: int) -> Lesson:
        return await self.lesson_repository.get_by_id(id)

    async def get_by_name(self, name: str) -> Lesson:
        return await self.lesson_repository.get_by_name(name)

    async def get_by_name_like(self, name: str) -> list[Lesson]:
        return await self.lesson_repository.get_by_name_like(name)

    async def get_all(self) -> list[Lesson]:
        return await self.lesson_repository.get_all()

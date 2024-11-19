from sqlalchemy import select

from src.utils import Database
from src.models import WorkloadContainer


class WorkloadService:
    def __init__(self, database: Database):
        self.database = database

    async def get_workload_containers(self) -> list[WorkloadContainer]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(WorkloadContainer).distinct())
            return result.scalars().unique().all()

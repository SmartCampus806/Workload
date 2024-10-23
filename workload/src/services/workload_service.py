from src.models import Groups, Workload, Lesson
from src.utils.configuration import AppConfig
from src.utils.database_manager import Database


class WorkloadService:
    def __init__(self, database:Database, config: AppConfig):
        self.database = database
        self.config = config

    async def test(self):
        async with self.database.session_factory() as session:
            group = Groups(name="test_group", students_count=12)
            session.add(group)
            group2 = Groups(name="test_group2", students_count=12)
            session.add(group2)

            lesson = Lesson(name='lesson1', year='2024/2025', semestr='Осенний', faculty=8)
            session.add(lesson)

            workload = Workload(type='Лекция', workload=12, lesson=lesson, groups=[group, group2])
            session.add(workload)

            lesson.workloads = [workload]
            group.workloads =[workload]

            await session.commit()




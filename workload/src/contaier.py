from dependency_injector import containers, providers

from src.repositories import LessonRepository
from src.services import ParseEmployeeService, ExportService, FilterService
from src.services.parse_workload_service import ParseWorkloadService
from src.utils.configuration import Config
from src.utils.database_manager import Database
from src.utils.logger import Logger


class MainContainer(containers.DeclarativeContainer):
    config = providers.Singleton(Config)
    logger = providers.Singleton(Logger)
    database = providers.Singleton(Database, config)

    lesson_repository = providers.Factory(LessonRepository, database, logger)

    parse_workload_service = providers.Factory(ParseWorkloadService, database, config)
    parse_employee_service = providers.Factory(ParseEmployeeService, database, logger)
    export_service = providers.Factory(ExportService, database)
    filter_service = providers.Factory(FilterService, database)

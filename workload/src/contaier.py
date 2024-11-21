from dependency_injector import containers, providers

from src.repositories import EmployeeRepository, WorkloadRepository, LessonRepository, GroupRepository
from src.services import EmployeeService, ParseEmployeeService, WorkloadService, EmployeeService2, ExportService
from src.services.group_service import GroupService
from src.services.lesson_service import LessonService
from src.services.parse_workload_service import ParseWorkloadService
from src.services.workload_service2 import WorkloadService2
from src.utils.configuration import Config
from src.utils.database_manager import Database
from src.utils.logger import Logger


class MainContainer(containers.DeclarativeContainer):
    config = providers.Singleton(Config)
    logger = providers.Singleton(Logger)
    database = providers.Singleton(Database, config, logger)

    employee_repository = providers.Factory(EmployeeRepository, database, logger)
    workload_repository = providers.Factory(WorkloadRepository, database, logger)
    lesson_repository = providers.Factory(LessonRepository, database, logger)
    group_repository = providers.Factory(GroupRepository, database, logger)

    employee_service = providers.Factory(EmployeeService, employee_repository, logger)
    group_service = providers.Factory(GroupService, group_repository, logger)
    parse_workload_service = providers.Factory(ParseWorkloadService, database, config)
    workload_service = providers.Factory(WorkloadService, database)
    workload_service2 = providers.Factory(WorkloadService2, workload_repository, group_repository,
                                          employee_repository, lesson_repository, logger)
    lesson_service = providers.Factory(LessonService, lesson_repository, logger)
    parse_employee_service = providers.Factory(ParseEmployeeService, employee_repository, logger)
    employee_service_2 = providers.Factory(EmployeeService2, database, logger)
    export_service = providers.Factory(ExportService, database)

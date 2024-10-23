from dependency_injector import containers, providers

from src.repositories import EmployeeRepository
from src.services import EmployeeService
from src.services.workload_service import WorkloadService
from src.utils.configuration import Config
from src.utils.database_manager import Database
from src.utils.logger import Logger


class MainContainer(containers.DeclarativeContainer):
    config = providers.Singleton(Config)
    logger = providers.Singleton(Logger)
    database = providers.Singleton(Database, logger)

    employee_repository = providers.Factory(EmployeeRepository, database, logger)

    employee_service = providers.Factory(EmployeeService, database, logger)
    workload_service = providers.Factory(WorkloadService, database, config)

from dependency_injector import containers, providers


from src.utils.configuration import Config
from src.utils.database_manager import Database
from src.utils.logger import Logger


class MainContainer(containers.DeclarativeContainer):
    config = providers.Singleton(Config)
    logger = providers.Singleton(Logger)
    database = providers.Singleton(Database, logger)

    employee_repository = providers.Factory(database, logger)

    employee_service = providers.Factory(database, logger)

from dependency_injector import containers, providers

from src.repositories.token_repository import RefreshTokenRepository
from src.repositories.user_repository import UserRepository
from src.services import UserService
from src.services.auth_service import AuthService
from src.services.jwt_token_service import JWTService
from src.utils.configuration import Config
from src.utils.database_manager import Database
from src.utils.logger import Logger


class MainContainer(containers.DeclarativeContainer):
    config = providers.Singleton(Config)
    logger = providers.Factory(Logger)
    database = providers.Singleton(Database, logger)

    user_repository = providers.Factory(UserRepository, database, logger)
    refresh_token_repository = providers.Factory(RefreshTokenRepository, database, logger)

    user_service = providers.Factory(UserService, user_repository, logger)
    jwt_service = providers.Factory(JWTService, refresh_token_repository,user_service, config)
    auth_service = providers.Factory(AuthService, jwt_service, user_service, logger)

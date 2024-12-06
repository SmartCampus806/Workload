from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from src.utils.configuration import Config
from src.utils.logger import Logger


class Database:
    def __init__(self, config: Config,
                 # log: Logger
                 ):
        # self.log = log

        self.url = (f"postgresql+asyncpg://{config.database.username}:{config.database.password}@{config.database.host}:"
                    f"{config.database.port}/{config.database.database}")

        self.engine: AsyncEngine = create_async_engine(url=self.url, echo=True, echo_pool=True,
                                                       max_overflow=5, pool_size=5)
        self.session_factory = async_sessionmaker(bind=self.engine, autoflush=False,
                                                  autocommit=False, expire_on_commit=False)

        # self.log.info(f"Database init with url: postgresql+asyncpg://{config.database.username}:***********@"
        #               f"{config.database.host}:{config.database.port}/{config.database.database}")

    async def despose(self) -> None:
        await self.engine.dispose()

    async def get_session(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session
            await session.close()

    async def execute(self, query):
        async with self.session_factory() as session:
            return await session.execute(query)

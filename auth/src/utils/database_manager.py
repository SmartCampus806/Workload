from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from src.utils.logger import Logger


class Database:
    def __init__(self, log: Logger):
        self.log = log

        # Вынести в config
        self.url = f"postgresql+asyncpg://user:password@localhost:5432/test"
        self.engine: AsyncEngine = create_async_engine(url=self.url, echo=True, echo_pool=True, max_overflow=5, pool_size=5)
        self.session_factory = async_sessionmaker(bind=self.engine, autoflush=False,
                                                  autocommit=False, expire_on_commit=False)

        self.log.info("Database init")

    async def despose(self) -> None:
        await self.engine.dispose()

    async def get_session(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session
            await session.close()
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from src.models import Groups, Base

# Асинхронная фикстура для создания сессии
@pytest.fixture
async def session():
    # Создаем асинхронный engine для базы данных в памяти
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=True)

    # Создаем все таблицы в базе данных
    async with engine.begin():
        await engine.run_sync(Base.metadata.create_all)

    # Создаем сессию
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)()
    # async with async_session() as session:
    #     yield session   # Сессия будет использована в тестах
    #     await session.commit()  # Фиксируем изменения после завершения теста

# Тесты
@pytest.mark.asyncio
async def test_create_user(session):
    session2 = session
    # Создаем пользователя и добавляем в базу данных
    # async with session_factory() as session:
    new_user = Groups(name='John Doe', students_count=30)
    session2.add(new_user)  # Теперь сессия доступна для использования
    await session2.commit()

    # Проверяем, что пользователь был добавлен
    result = await session2.execute(select(Groups).filter_by(name='John Doe'))
    user = result.scalars().first()
    assert user is not None
    assert user.name == 'John Doe'
    assert user.students_count == 30
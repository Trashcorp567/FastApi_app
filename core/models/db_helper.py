from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session, AsyncSession
from asyncio import current_task
from core.config import settings


class DbHelper:
    def __init__(self, url: str, echo: bool = True):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    def get_scoped_session(self):
        return async_scoped_session(
            self.session_factory,
            scopefunc=current_task,
        )

    async def session_dependency(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session
            await session.close()

    async def scoped_session_dependency(self) -> AsyncSession:
        session = self.get_scoped_session()
        yield session
        await session.close()


db_helper = DbHelper(
    url=settings.url,
    echo=settings.echo,
)


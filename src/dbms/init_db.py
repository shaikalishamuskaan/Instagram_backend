import asyncio

from dbms.db import engine
from dbms.models import Base


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
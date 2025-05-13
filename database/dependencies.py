from database.db import sessionLocal


async def get_db():
    async with sessionLocal() as session:
        yield session

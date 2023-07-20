import asyncio

import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from settings import (check_period, keep_unavailable, name, password,
                      port, username)

from .constants import SOURCE_STATUS_CHANGED, UNAVAILIBLE_SOURCE_DELETED
from .logging_config import status_check_logger
from .models import Source

engine = create_async_engine(
    f'postgresql+asyncpg://{username}:{password}@db:{port}/{name}')


AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)


async def check_source_status(source):
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.get(source.full_link, timeout=2)
            status_code = response.status
        except asyncio.exceptions.TimeoutError:
            status_code = 0

        if status_code == 200:
            source.status_check_error = 0
            source.is_available = True
        else:
            source.status_check_error += 1
            source.is_available = False

        async_session = AsyncSessionLocal()
        async with async_session as session:
            print(source.status_check_error)
            print(keep_unavailable)
            if source.status_check_error > keep_unavailable:
                print(source.status_check_error)
                print(keep_unavailable)
                session.delete(source)
                await session.commit()
                status_check_logger.info(
                    UNAVAILIBLE_SOURCE_DELETED.format(
                        source.id, keep_unavailable))
            else:
                if source.status_code != str(status_code):
                    status_check_logger.info(
                        SOURCE_STATUS_CHANGED.format(
                            source.id, source.status_code, status_code))
                source.status_code = str(status_code)
                session.add(source)
                await session.commit()
        await async_session.close()

        if 'response' in locals() and not response.closed:
            response.release()


async def create_tasks():
    async with AsyncSessionLocal() as session:
        sources = await session.execute(select(Source))
        sources = sources.scalars().all()

    tasks = [asyncio.ensure_future(
                check_source_status(source)) for source in sources]
    await asyncio.wait(tasks)


async def schedule_monitoring():
    while True:
        await create_tasks()
        await asyncio.sleep(60)  # Пауза в 1 час


def start_async_monitoring():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(schedule_monitoring())

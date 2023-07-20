import asyncio

import aiohttp
from settings import (check_period, keep_unavailable, name, password, port,
                      username)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

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
            response = await session.get(source.full_link, timeout=3)
            status_code = response.status
        except asyncio.exceptions.TimeoutError:
            status_check_logger.info(f'Таймаут для ресурса {source.id}.')
            status_code = 0
        except aiohttp.client_exceptions.ClientConnectorError:
            status_check_logger.info(
                f'Не получилось связаться с {source.id}, возможно {source.domain} не существует.')
            status_code = 0
        except Exception as ex:
            status_check_logger.info(f'Ошибка при запросе к {source.id} - {ex}.')

        if status_code == 200:
            source.status_check_error = 0
            source.is_available = True
            status_check_logger.info(
                f'Ресурс {source.id} доступен, код ответа - {status_code}.')
        else:
            source.status_check_error += 1
            source.is_available = False
            status_check_logger.info(
                f'Ресурс {source.id} недоступен, код ответа - {status_code}.')

        async_session = AsyncSessionLocal()
        async with async_session as session:
            if source.status_check_error > keep_unavailable:
                await session.delete(source)
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
    if tasks:
        await asyncio.wait(tasks)


async def schedule_monitoring():
    while True:
        status_check_logger.info('Запуск нового цикла мониторинга.')
        await create_tasks()

        status_check_logger.info(f'Пауза в мониторинге {check_period} секунд.')
        await asyncio.sleep(check_period)  # Пауза в N секунд


def start_async_monitoring():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(schedule_monitoring())

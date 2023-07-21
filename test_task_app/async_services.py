import asyncio

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from settings import name, password, port, username

from .constants import NEW_SOURCE_SAVED, SOURCE_TIMEOUT
from .logging_config import status_check_logger
from .models import Source

engine = create_async_engine(
    f'postgresql+asyncpg://{username}:{password}@db:{port}/{name}')

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False)


async def create_new_source(source: tuple):
    """
    Функция принимает на вход кортеж из url и pattern match ресурса,
    делает запрос к ресурсу и сохраняет его статус ответ.
    """
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.get(source[0], timeout=2)
            status_code = response.status
        except asyncio.exceptions.TimeoutError:
            status_code = 0
            status_check_logger.info(SOURCE_TIMEOUT.format(source[0]))
        protocol, domain, zone, path, params = source[-1].groups()
        if status_code == 200:
            is_available = True
        else:
            is_available = False
        if params:
            params_list = params.split('&')
            params_dict = dict([tuple(a.split('=')) for a in params_list])
        else:
            params_dict = None
    new_source = Source(
        protocol=protocol,
        domain=domain,
        domain_zone=zone,
        path=path,
        params=params_dict,
        full_link=source[0],
        status_code=str(status_code),
        is_available=is_available)
    async_session = AsyncSessionLocal()
    async with async_session as session:
        session.add(new_source)
        await session.commit()
        await session.refresh(new_source)
        status_check_logger.info(
            NEW_SOURCE_SAVED.format(domain, new_source.id))


async def create_from_dict(urls_for_saving: dict):
    tasks = [
        asyncio.ensure_future(
            create_new_source(link)) for link in urls_for_saving.items()]
    await asyncio.wait(tasks)


def start_async(urls_for_saving: dict):
    asyncio.run(create_from_dict(urls_for_saving))

from multiprocessing import Process

import click

from . import app
from .logging_config import all_actions_logger
from .monitoring import start_async_monitoring


@app.cli.command('start_monitoring')
def start_monitoring():
    """Функция для запуска процесса мониторинга."""
    monitoring_process = Process(
        target=start_async_monitoring)
    monitoring_process.start()
    all_actions_logger.info('Запуск процесса мониторинга')

    click.echo('Мониторинг запущен')

# Приложение проводит логирование своей работы с ротацией лог-файлов
# при достижении размера файла 1 мегабайт.
# При этом логгируются все полученные запросы и ответы приложения,
# информация о добавлении в БД новой записи, либо об изменении существующих.
# Также логируются результаты опроса статус кодов сайтов
# - записывается результат по каждому сайту отдельно
# и общий итог каждой проверки.

import logging
from logging.handlers import RotatingFileHandler

formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
# Настройки логгирования запросов и ответов,
# добавления в БД новой записи, либо изменения существующей.

all_actions_handler = RotatingFileHandler(
    'logs/all_actions.log',
    maxBytes=1024 * 1024, backupCount=1)

all_actions_handler.setFormatter(formatter)
all_actions_handler.setLevel(logging.DEBUG)

all_actions_logger = logging.getLogger('all_actions')
all_actions_logger.setLevel(logging.DEBUG)
all_actions_logger.addHandler(all_actions_handler)


# Настройки логгирования опроса статус кодов сайтов,
# - записывается результат по каждому сайту отдельно
# и общий итог каждой проверки.

status_check_handler = RotatingFileHandler(
    'logs/status_check.log',
    maxBytes=1024 * 1024, backupCount=1)
status_check_handler.setFormatter(formatter)
status_check_handler.setLevel(logging.DEBUG)

status_check_logger = logging.getLogger('status_check')
status_check_logger.setLevel(logging.DEBUG)
status_check_logger.addHandler(status_check_handler)

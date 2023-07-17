# Настройки мониторинга
KEEP_UNAWAILABLE_FOR = 60*60*24   # удалять если ресурс недоступен 24 часа
CHECK_SOURCE_STATUS_EVERY = 60  # проверять каждые 1200 секунд


# регулярные выражения для проверки соответствия
UUID_PATTERN = r'[\da-z]{8}-[\da-z]{4}-[\da-z]{4}-[\da-z]{4}-[\da-z]{12}'
URL_PATTERN = r'(?P<protocol>https|http):\/\/(?P<domain>[\.\-\w]+)\.(?P<zone>\w+)\/?(?P<path>[\w\._\-%\/]+)?\??(?P<params>[&=\-\w]+)?'

# информационные сообщения для api_views
URL_REQUIRED = 'В запросе отсутствует URL.'
INVALID_URL = 'Указан невалидный URL'
URL_SAVING_ERROR = 'Некорректная ссылка {}.'
NEW_SOURCE_CREATED = 'Новый ресурс создан'
ZIP_REQUIRED = 'Zip-архив не передан.'
ZIP_EMPTY = 'Пустой архив.'
INVALID_FILE_EXTENTION = 'Файл должен быть в формате csv'
UUID_REQUIRED = 'Укажите uuid ресурса'
INVALID_UUID = 'Укажите корректный uuid ресурса'
UUID_NOT_FOUND = 'Ресурс с uuid {} не найден в базе.'
SCREENSHOT_REQUIRED = 'Загрузите картинку'
SCREENSHOT_SAVED = 'Скриншот сохранен.'
UNABLE_TO_GET_LOGS = 'Ошибка получения логов.'
STARTED_SAVING_PROCESS = 'Запущен процесс записи объектов из файла.'
COMPLETED_SAVING_PROCESS = 'Добавлено {} ресурса(ов).'


NEW_SOURCE_SAVED = 'Добавлен новый ресурс домен - {}, id - {}'
SOURCE_TIMEOUT = 'Сработал таумаут ожидания ответа для {}'
SOURCE_DELETED = 'Удален ресурс с id {}'


# информационные сообщения для мониторинга
UNAVAILIBLE_SOURCE_DELETED = 'Ресурс {} недоступен дольше {} и был удален.'
SOURCE_STATUS_CHANGED = 'Изменился статус доступности ресурса {} с {} на {}.'

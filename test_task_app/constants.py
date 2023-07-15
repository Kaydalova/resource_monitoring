KEEP_UNAWAILABLE = 60*60*24
CHECK_STATUS_PERIOD_IN_SECONDS = 60*60


# регулярные выражения для проверки соответствия
UUID_PATTERN = '[\da-z]{8}-[\da-z]{4}-[\da-z]{4}-[\da-z]{4}-[\da-z]{12}'

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
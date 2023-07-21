# Настройки мониторинга
KEEP_UNavailable_FOR = 60*60*24   # удалять если ресурс недоступен 24 часа
CHECK_SOURCE_STATUS_EVERY = 60  # проверять каждые 1200 секунд


# регулярные выражения для проверки соответствия
UUID_PATTERN = r'[\da-z]{8}-[\da-z]{4}-[\da-z]{4}-[\da-z]{4}-[\da-z]{12}'
URL_PATTERN = r'(?P<protocol>https|http):\/\/(?P<domain>[\.\-\w]+)\.(?P<zone>\w+)\/?(?P<path>[\w\._\-%\/]+)?\??(?P<params>[&=\-\w]+)?'
DATETIME_PATTERN = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$'


# информационные сообщения для views
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

COMPLETED_SAVING_PROCESS = 'Добавлено {} ресурса(ов).'
NEW_SOURCE_SAVED = 'Добавлен новый ресурс домен - {}, id - {}'
SOURCE_TIMEOUT = 'Сработал таумаут ожидания ответа для {}'
SOURCE_DELETED = 'Удален ресурс с id {}'
DATE_FROM_REQUIRED = 'Введите дату начала периода'
DATE_TO_REQUIRED = 'Введите дату окончания периода'
INVALID_DATE_FORMAT = 'Неверный формат даты. Введите дату в формате yyyy-mm-dd HH:mm'
DATE_CLEARED = 'Фильтр по дате очищен'


# информационные сообщения для логгирования
DOWNLOAD_LOGS_PDF = 'Загрузка PDF файла с журналом логов.'
SHOW_ALL_SOURCES = 'Новый запрос на просмотр таблицы ресурсов.'
SHOW_LOGS = 'Новый запрос на просмотр журнала логов.'
SHOW_NEWS = 'Новый запрос на просмотр ленты новостей.'
SHOW_SOURCE_PAGE = 'Просмотр страницы ресурса {}.'
ADD_SOURCES = 'Запрос на просмотр страницы добавления ресурсов'
STARTED_SAVING_PROCESS = 'Запущен процесс записи объектов из файла.'
DELETE_SOURCE = 'Новый запрос на удаление ресурса'


# информационные сообщения для мониторинга
UNAVAILIBLE_SOURCE_DELETED = 'Ресурс {} недоступен дольше {} проверок и был удален.'
SOURCE_STATUS_CHANGED = 'Изменился статус доступности ресурса {} с {} на {}.'


# информационные сообщения для auth
ALL_DATA_REQUIRED = 'Для регистрации необходимо указать email, username и пароль'
USERNAME_TAKEN = 'Пользователь с username {} уже существует'
USER_CREATED = 'Пользователь {} успешно создан!'
USERNAME_NOT_FOUND = 'Пользователь {} не найден.'
WRONG_PASSWORD = 'Неверный пароль для {}.'
GENERATED_TOKEN = 'Сгенерирован токен для пользователя {}.'
WRONG_PASSWORD_OR_USERNAME = 'Неверные учетные данные.'
USER_LOGED_IN = 'Пользователь {} вошел.'
USER_LOGED_OUT = 'Пользователь {} вышел.'


DATA_REQUIRED = 'Обязательное поле'
PASSWORD_LENGTH = 'Пароль должен быть от 8 до 16 символов'
WRONG_USERNAME = 'Username должен содержать только буквы и цифры'
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 16

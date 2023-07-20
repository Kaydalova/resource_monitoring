import re
import subprocess
from multiprocessing import Process

from flask import jsonify, request

from . import app, db
from .async_services import start_async
from .constants import (INVALID_FILE_EXTENTION, INVALID_URL, INVALID_UUID,
                        NEW_SOURCE_CREATED, SCREENSHOT_REQUIRED,
                        SCREENSHOT_SAVED, STARTED_SAVING_PROCESS,
                        UNABLE_TO_GET_LOGS, URL_REQUIRED, UUID_NOT_FOUND,
                        UUID_PATTERN, UUID_REQUIRED, ZIP_EMPTY, ZIP_REQUIRED)
from .logging_config import all_actions_logger, status_check_logger
from .models import Source
from .services import (check_file_extension, check_source_with_pattern,
                       check_urls_in_csv, create_new_source,
                       unzip_the_zip_and_save)
from settings import logs_limit_config


@app.route('/api/add_source', methods=['POST'])
def add_source_api_view():
    """
    Эндроинт принимает на вход ссылку на веб_ресурс
    и раскладывает ее на протокол, домен, доменную зону и путь.
    Если в ссылке присутствуют параметры - преобразует их в словарь.
    Полученные данные сохраняет в таблице базы данных,
    присвоив уникальный идентификационный номер (uuid).
    Возвращать пользователю ответ в формате json с разложенными данными
    и статусом обработки.
    """

    all_actions_logger.info('Новый запрос к /api/add_source.')
    data = request.get_json()

    if 'url' not in data:
        all_actions_logger.info(URL_REQUIRED)
        return jsonify({'error': URL_REQUIRED}), 400

    pattern_match = check_source_with_pattern(data['url'])

    if not pattern_match:
        all_actions_logger.info(INVALID_URL)
        return jsonify({'error': INVALID_URL}), 400

    if not Source.query.filter(Source.full_link == data['url']).first():
        new_source = create_new_source(pattern_match, data['url'])
        all_actions_logger.info(NEW_SOURCE_CREATED)
        return jsonify({
            'url': new_source.to_dict(),
            'status': NEW_SOURCE_CREATED}), 201
    return jsonify({
        'error': 'Такой адрес уже есть в базе.'}), 400


@app.route('/api/add_sources_zip', methods=['POST'])
def add_zip_sources_api_view():
    """
    Эндпоинт принимает zip архив с csv файлом с перечнем ссылок.
    Возвращает общий статус обработки файла:
    - общее количество ссылок
    - количество ссылок с ошибками
    - количество ссылок направленных на сохранение в БД
    """
    all_actions_logger.info('Новый запрос к /api/add_source_zip.')
    # проверка есть ли в запросе файл
    if 'file' not in request.files:
        all_actions_logger.info(ZIP_REQUIRED)
        return jsonify({'error': ZIP_REQUIRED}), 400

    # проверка формата архива
    if not check_file_extension(request.files['file'].filename, 'zip'):
        all_actions_logger.info(ZIP_REQUIRED)
        return jsonify({'error': ZIP_REQUIRED}), 400

    # распаковка и проверка формата внутреннего файла csv
    csv_file = unzip_the_zip_and_save(request.files['file'])

    if len(csv_file) == 0:
        all_actions_logger.info(ZIP_EMPTY)
        return jsonify({'error': ZIP_EMPTY}), 400

    if not check_file_extension(csv_file[0], 'csv'):
        all_actions_logger.info(INVALID_FILE_EXTENTION)
        return jsonify({'error': INVALID_FILE_EXTENTION}), 400

    # Проверка всех ссылок в csv файле, поиск некорректных ссылок
    zip_filename = request.files['file'].filename.rsplit('.', 1)[0]
    csv_filename = csv_file[0]
    all_urls, urls_for_saving = check_urls_in_csv(
        zip_filename, csv_filename)
    error_urls = all_urls - len(urls_for_saving)

    # Сохранение корректных ссылок из CSV файла в другом процессе
    all_actions_logger.info(STARTED_SAVING_PROCESS)
    saving_urls_process = Process(
        target=start_async, args=(urls_for_saving,))
    saving_urls_process.start()

    return jsonify({
        'all_urls': all_urls,
        'error_urls': error_urls,
        'urls_for_saving': len(urls_for_saving)}), 200


@app.route('/api/add_screenshot', methods=['POST'])
def add_screenshot_api_view():
    """
    Эндпоинт принимает POST запрос, который содержит
    uuid ресурса и картинку (предполагается скриншот сайта).
    Скриншот сохраняется в БД в таблице ресурсов.
    """
    all_actions_logger.info('Новый запрос к /api/add_screenshot')
    source_id = request.form.get('source_id')
    # проверка указан ли source_id
    if not source_id:
        all_actions_logger.info(UUID_REQUIRED)
        return jsonify({'error': UUID_REQUIRED}), 400

    # проверка является ли переданный source_id валидным uuid
    if not re.fullmatch(UUID_PATTERN, source_id):
        all_actions_logger.info(INVALID_UUID)
        return jsonify({'error': INVALID_UUID}), 400

    screenshot = request.files.get('screenshot')
    # проверка отправлена ли картинка
    if not screenshot:
        all_actions_logger.info(SCREENSHOT_REQUIRED)
        return jsonify({'error': SCREENSHOT_REQUIRED}), 400

    db_source = Source.query.filter_by(id=source_id).first()
    # существует ли файл с указанным uuid
    if not db_source:
        all_actions_logger.info(UUID_NOT_FOUND.format(source_id))
        return jsonify({'error': UUID_NOT_FOUND.format(source_id)}), 400

    db_source.screenshot = screenshot.read()
    db.session.add(db_source)
    db.session.commit()
    all_actions_logger.info(SCREENSHOT_SAVED)
    status_check_logger.info(f'Добавлен скриншот для ресурса {source_id}')
    return jsonify({'success': SCREENSHOT_SAVED}), 200


@app.route('/api/all_sources', methods=['GET'])
def get_all_sources_api_view():
    """
    Эндпоинт принимает GET запрос и выводит все сохраненные ссылки из БД
    с последним статус-кодом ответа ресурса для каждой ссылки.
    Можно сделать выборки по доменной зоне, id, доступности.
    Добавить возможность пагинации json-ответа.
    """
    all_actions_logger.info('Новый запрос к /api/all_sources')
    page = request.args.get('page')
    per_page = request.args.get('per_page')
    domain_zone = request.args.get('domain_zone')
    id = request.args.get('id')
    is_awailable = request.args.get('is_awailable')

    query = Source.query

    if domain_zone:
        query = query.filter(Source.domain_zone == domain_zone)
    if id:
        query = query.filter(Source.id == id)
    if is_awailable:
        query = query.filter(Source.is_awailable == is_awailable)
    total = query.count()
    if page and per_page:
        query = query.paginate(page=int(page), per_page=int(per_page))

    all_sources = query
    sources_list = []
    for source in all_sources:
        sources_list.append({
            'id': source.id,
            'domain_zone': source.domain_zone,
            'full_link': source.full_link,
            'status_code': source.status_code,
            'is_awailable': source.is_awailable
        })
    all_actions_logger.info('Список всех ресурсов отправлен')
    return jsonify({
        'total': total,
        'page': page,
        'per_page': per_page,
        'links': sources_list
    })


@app.route('/api/logs', methods=['GET'])
def get_logs_api_view():
    """
    Эндпоинт принимает GET запрос и возвращает
    последние 50 строчек лог-файла.
    Количество строчек может быть изменено в параметрах запроса.
    """
    all_actions_logger.info('Новый запрос к /api/logs')
    logs_limit = int(request.args.get('logs_limit', logs_limit_config))
    try:
        output = subprocess.check_output(
            ['tail', '-n', str(
                logs_limit), 'logs/all_actions.log'], universal_newlines=True)
        return output, 200
    except subprocess.CalledProcessError:
        all_actions_logger.warning(UNABLE_TO_GET_LOGS)
        return jsonify({'error': UNABLE_TO_GET_LOGS}), 500

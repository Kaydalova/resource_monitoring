import math
import re
from multiprocessing import Process

from flask import (flash, redirect, render_template, request, send_file,
                   session, url_for)
from flask_login import login_required
from fpdf import FPDF

from settings import logs_per_page, news_per_page

from . import app, db
from .async_services import start_async
from .constants import (ADD_SOURCES, COMPLETED_SAVING_PROCESS, DATE_CLEARED,
                        DATE_FROM_REQUIRED, DATE_TO_REQUIRED, DATETIME_PATTERN,
                        DELETE_SOURCE, DOWNLOAD_LOGS_PDF, INVALID_DATE_FORMAT,
                        INVALID_FILE_EXTENTION, INVALID_URL,
                        NEW_SOURCE_CREATED, NEW_SOURCE_SAVED, SHOW_ALL_SOURCES,
                        SHOW_LOGS, SHOW_NEWS, SHOW_SOURCE_PAGE, SOURCE_DELETED,
                        STARTED_SAVING_PROCESS, ZIP_EMPTY, ZIP_REQUIRED)
from .logging_config import all_actions_logger, status_check_logger
from .models import Source
from .services import (check_file_extension, check_source_with_pattern,
                       check_urls_in_csv, create_new_source,
                       unzip_the_zip_and_save)


@app.route('/add_source', methods=['GET', 'POST'])
@login_required
def create_source_view():
    """
    Функция для добавления  в приложение новых веб-ресурсов.
    Формы добавляют веб-ресурсы как поштучно, так и загрузкой файла.
    """
    all_actions_logger.info(ADD_SOURCES)

    # проверка, что есть либо файл, либо ресурс:
    if request.method == 'POST' and not request.files.get(
                'file') and not request.form.get('url'):
        flash('Выберите файл и вставьте ссылку на ресурс.')
        return render_template('create_source.html')

    if request.method == 'POST' and request.files.get('file'):

        # проверка формата архива
        if not check_file_extension(request.files['file'].filename, 'zip'):
            all_actions_logger.info(ZIP_REQUIRED)

        # распаковка и проверка формата внутреннего файла csv
        csv_file = unzip_the_zip_and_save(request.files['file'])

        if len(csv_file) == 0:
            all_actions_logger.info(ZIP_EMPTY)
            flash(ZIP_EMPTY)

        if not check_file_extension(csv_file[0], 'csv'):
            all_actions_logger.info(INVALID_FILE_EXTENTION)
            flash(INVALID_FILE_EXTENTION)

        # Проверка всех ссылок в csv файле, поиск некорректных ссылок
        zip_filename = request.files['file'].filename.rsplit('.', 1)[0]
        csv_filename = csv_file[0]
        all_urls, urls_for_saving = check_urls_in_csv(
            zip_filename, csv_filename)

        # Сохранение корректных ссылок из CSV файла в другом процессе
        all_actions_logger.info(STARTED_SAVING_PROCESS)
        saving_urls_process = Process(
            target=start_async, args=(urls_for_saving,))
        saving_urls_process.start()
        all_actions_logger.info(
            COMPLETED_SAVING_PROCESS.format(len(urls_for_saving)))
        flash(COMPLETED_SAVING_PROCESS.format(len(urls_for_saving)))

    if request.method == 'POST' and request.form.get('url'):
        url = request.form.get('url')
        pattern_match = check_source_with_pattern(url)

        if not pattern_match:
            all_actions_logger.info(INVALID_URL)
            flash(INVALID_URL)
        else:
            new_source = create_new_source(pattern_match, url)
            if not new_source:
                all_actions_logger.info(INVALID_URL)
                flash(INVALID_URL)
            else:
                status_check_logger.info(
                    NEW_SOURCE_SAVED.format(new_source.domain, new_source.id))
                all_actions_logger.info(NEW_SOURCE_CREATED)
                flash(NEW_SOURCE_CREATED)
    return render_template('create_source.html')


@app.route('/', methods=['GET'])
@login_required
def get_sources_view():
    """
    Функция для отображения таблицы со всеми ссылками из базы данных
    с разбивкой на страницы (пагинация, по 10 элементов на страницу).
    Также добавляет на страницу поиск по доменному имени,
    возможность фильтрования по доменной зоне и статусу доступности,
    а также удаление конкретного элемента
    из таблицы и базы данных соответственно.
    """
    all_actions_logger.info(SHOW_ALL_SOURCES)
    clear = request.args.get('clear', '')
    domain = request.args.get('domain', '')
    domain_zone = request.args.get('domain_zone', '')
    is_available = request.args.get('is_available', '')
    page = request.args.get('page', 1, type=int)

    if clear:
        sources = Source.query.paginate(page=1, per_page=10)
        return render_template('all_sources.html', sources=sources)

    query = Source.query

    if domain:
        query = query.filter(Source.domain == domain)
    if domain_zone:
        query = query.filter(Source.domain_zone == domain_zone)
    if is_available:
        query = query.filter(Source.is_available == is_available)

    if page:
        query = query.paginate(page=page, per_page=10)
    sources = query
    return render_template('all_sources.html', sources=sources)


@app.route('/source/<string:source_id>/delete')
@login_required
def delete_source_view(source_id):
    """
    Функция удаления ресурса по id.
    """
    all_actions_logger.info(DELETE_SOURCE)
    source = Source.query.get_or_404(source_id)
    db.session.delete(source)
    db.session.commit()
    all_actions_logger.info(SOURCE_DELETED.format(source_id))
    status_check_logger.info(SOURCE_DELETED.format(source_id))
    return redirect(url_for('get_sources_view'))


@app.route('/logs', methods=['GET'])
@login_required
def get_logs_view():
    """
    Функция для отображаения строк из лог-файла.
    Отображение динамическое (при обновлении файла -
    обновляется и содержимое веб-страницы).
    По клику на кнопку "скачать логи" скачивается файл
    с отображаемыми строчками лога в формате pdf.
    """
    all_actions_logger.info(SHOW_LOGS)
    log_file = 'logs/all_actions.log'

    page = request.args.get('page', 1, type=int)

    with open(log_file, 'r') as file:
        logs = file.readlines()[::-1]

    page_start = (page-1) * logs_per_page
    page_end = page_start + logs_per_page
    logs_with_pagination = logs[page_start:page_end]
    total = math.ceil(len(logs)/logs_per_page)

    return render_template(
        'logs.html',
        logs=logs_with_pagination,
        current_page=page,
        total=total)


@app.route('/download_logs')
@login_required
def download_logs():
    all_actions_logger.info(DOWNLOAD_LOGS_PDF)
    log_file = 'logs/all_actions.log'
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'font/DejaVuSerifCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', size=10)
    pdf.cell(200, 10, txt='Журнал добавления ресурсов', ln=1, align='C')

    with open(log_file, 'r') as file:
        logs = file.read()
        logs = logs.split('\n')[::-1]
        for elem in logs:
            pdf.cell(200, 10, txt=elem, ln=1, align='L')

    pdf.output('test_task_app/logs.pdf')
    return send_file('logs.pdf', as_attachment=True)


@app.route('/news', methods=['GET'])
@login_required
def news_view():
    """
    Функция для отображения ленты новостей.
    На эту страницу выводится информация об изменениях:
    - изменился код ответа сайта
    - ресурс был добавлен в базу
    - ресурс был удален из базы
    """
    all_actions_logger.info(SHOW_NEWS)

    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    clear = request.args.get('clear')
    page = request.args.get('page', 1, type=int)
    log_file = 'logs/status_check.log'
    per_page = news_per_page

    with open(log_file, 'r') as file:
        news = file.readlines()[::-1]

    page_start = (page-1) * per_page
    page_end = page_start + per_page
    news_with_pagination = news[page_start:page_end]
    total = math.ceil(len(news)/per_page)

    if clear:
        flash(DATE_CLEARED)
        session.pop('date_from', None)
        session.pop('date_to', None)

        return render_template(
            'news.html',
            news=news_with_pagination,
            current_page=page, total=total)

    datetime_pattern = re.compile(DATETIME_PATTERN)

    # Проверяем, что обе даты указаны
    if date_from and not date_to:
        flash(DATE_TO_REQUIRED)
        return render_template(
            'news.html',
            news=news_with_pagination,
            current_page=page, total=total)
    if date_to and not date_from:
        flash(DATE_FROM_REQUIRED)
        return render_template(
            'news.html',
            news=news_with_pagination,
            current_page=page, total=total)

    # Проверяем, что дата указана в корректном формате
    if date_from and date_to:
        if (not datetime_pattern.match(
                date_to) or not datetime_pattern.match(date_from)):
            flash(INVALID_DATE_FORMAT)
            return render_template(
                'news.html',
                news=news_with_pagination,
                current_page=page, total=total)

        # Если даты указаны сохраняем их в сессии, чтобы был доступ к ним
        # При переключении между страницами
        session['date_from'] = date_from
        session['date_to'] = date_to

        date_news = []
        for element in news:
            if date_from <= element.split(']')[0][1:20] <= date_to:
                date_news.append(element)

        page_start = (page-1) * per_page
        page_end = page_start + per_page
        news_with_pagination = date_news[page_start:page_end]
        total = math.ceil(len(date_news)/per_page)
        return render_template(
            'news.html',
            news=news_with_pagination,
            current_page=page,
            total=total)

    # Если даты есть в сессии
    if session.get('date_from') and session.get('date_to'):
        date_from = session['date_from']
        date_to = session['date_to']
        date_news = []
        for element in news:
            if date_from <= element.split(']')[0][1:20] <= date_to:
                date_news.append(element)

        page_start = (page-1) * per_page
        page_end = page_start + per_page
        news_with_pagination = date_news[page_start:page_end]
        total = math.ceil(len(date_news)/per_page)
        return render_template(
            'news.html',
            news=news_with_pagination,
            current_page=page,
            total=total)

    return render_template(
        'news.html',
        news=news_with_pagination,
        current_page=page, total=total)


@app.route('/source/<string:source_id>', methods=['GET'])
@login_required
def source_view(source_id):
    """
    Функция для отображения страницы ресурса.
    Выводятся все данные по ресурсу из БД, картинка (если есть),
    лента с новостями по ресурсу.
    """
    all_actions_logger.info(SHOW_SOURCE_PAGE.format(source_id))
    source = Source.query.get_or_404(source_id)
    screenshot = source.screenshot

    log_file = 'logs/status_check.log'
    source_news = []

    with open(log_file, 'r') as file:
        news = file.read()
        news = news.split('\n')[::-1]
        for elem in news:
            if source_id in elem:
                source_news.append(elem)

    if screenshot:
        filename = f'{source.id}.jpg'
        downloads = f'test_task_app/static/img/{filename}'
        file_new = f'/static/img/{filename}'
        with open(downloads, 'wb') as file:
            file.write(screenshot)
    else:
        file_new = None

    return render_template(
        'source.html',
        news=source_news,
        source=source,
        screenshot=file_new)

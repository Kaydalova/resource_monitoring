from flask import flash, redirect, render_template, request, url_for

from . import app, db
from .models import Source
from .services import add_resources_from_zip, add_single_resource
from .logging_config import all_actions_logger
from .constants import (INVALID_FILE_EXTENTION, INVALID_URL, INVALID_UUID,
                        NEW_SOURCE_CREATED, SCREENSHOT_REQUIRED,
                        SCREENSHOT_SAVED, UNABLE_TO_GET_LOGS, URL_REQUIRED,
                        UUID_NOT_FOUND, UUID_PATTERN, UUID_REQUIRED, ZIP_EMPTY,
                        ZIP_REQUIRED, STARTED_SAVING_PROCESS)
from .services import (add_resources_from_list, check_file_extension,
                       check_source_with_pattern, check_urls_in_csv,
                       create_new_source, unzip_the_zip_and_save)
from multiprocessing import Process


@app.route('/add_source', methods=['GET', 'POST'])
def create_source_view():
    """
    Функция для добавления  в приложение новых веб-ресурсов.
    Формы добавляют веб-ресурсы как поштучно, так и загрузкой файла.
    """
    if request.method == 'POST' and request.files:

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
        saving_urls_process = Process(
            target=add_resources_from_list, args=(urls_for_saving,))
        saving_urls_process.start()
        all_actions_logger.info(STARTED_SAVING_PROCESS)
        flash(f'Добавлено {len(urls_for_saving)} ресурса(ов).')


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
                all_actions_logger.info(NEW_SOURCE_CREATED)
                flash(NEW_SOURCE_CREATED)
    return render_template('create_source.html')



@app.route('/sources', methods=['GET'])
def get_sources_view():
    page = request.args.get('page', 1, type=int)
    sources = Source.query.paginate(page=page, per_page=10)
    return render_template('all_sources.html', sources=sources)


@app.route('/source/<string:source_id>/delete')
def delete_source_view(source_id):
    source = Source.query.get_or_404(source_id)
    db.session.delete(source)
    db.session.commit()
    return redirect(url_for('get_sources_view'))

import csv
import os
import re
from zipfile import ZipFile

import requests
from flask import flash

from . import db
from .models import Source


def check_file_extension(filename, extention):
    """
    Функция проверяет соответствует ли файл указанному расширению.
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1] == extention


def unzip_the_zip_and_save(zip_file):
    """
    Функция сохраняет, разархивирует zip и возвращает
    его содержимое в виде списка названий файлов.
    """
    zip_file.save(f'uploads/{zip_file.filename}')
    filename = zip_file.filename.rsplit('.', 1)[0]

    with ZipFile(f'uploads/{zip_file.filename}', 'r') as file:
        file.extractall(f'uploads/{filename}')
    
    content = os.listdir(f'uploads/{filename}')
    return content


def check_source_with_pattern(data):
    """
    Функция проверяет соответствие ссылки заданному паттерну.
    """
    pattern = '(?P<protocol>https|http):\/\/(?P<domain>[\.\-\w]+)\.(?P<zone>\w+)\/?(?P<path>[\w\._\-%\/]+)?\??(?P<params>[&=\-\w]+)?'
    pattern_match = re.search(pattern, data)
    if not pattern_match:
        return None
    return pattern_match


def check_urls_in_csv(zip_filename, csv_file):
    """
    Функция проверяет ссылки с csv на соответствие паттерну.
    Возвращает:
    - общее количество ссылок в файле
    - количество ссылок с ошибками
    - словарь(ссылка:pattern_match) со ссылками, которые нужно сохранить в БД
    """
    all_urls = 0
    urls_for_saving = {}
    with open(f'uploads/{zip_filename}/{csv_file}') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            all_urls += 1
            pattern_match = check_source_with_pattern(row[0])
            if pattern_match:
                urls_for_saving[row[0]] = pattern_match
    return (all_urls, urls_for_saving)


def add_resources_from_list(urls_for_saving):
    """
    Функция разбивает ссылку на составляющие
    (протокол, домен, доменная зона, путь, параментры)
    и сохраняет новый объект в БД.
    """

    print('начало обработки списка')
    for link in urls_for_saving.items():
        protocol, domain, zone, path, params = link[-1].groups()
        try:
            status = requests.get(link[0], timeout=5).status_code
        except requests.exceptions.ReadTimeout:
            print(f'таумаут для {link[0]}')
            # логгер
            continue
        if status == 200:
            is_awailable = True
        else:
            is_awailable = False

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
            full_link=link[0],
            status_code=status,
            is_awailable=is_awailable)
        db.session.add(new_source)
        db.session.commit()
    print('конец обработки списка')








def add_resources_from_zip(request):
    """
    Функция проверяет, что передан архив в формате zip,
    который содержит файл в формате csv
    и сохраняет ссылки из документа в базу.
    Возвращает количество добавленных в базу ссылок.
    """
    zip_file = request.files['file']
    zip_file_name = zip_file.filename

    if not check_file_extension(zip_file_name, 'zip'):
        flash('Поддерживается только формат zip', 'error')
        return None
    
    zip_file.save(f'uploads/{zip_file.filename}')

    filename = zip_file.filename.rsplit('.', 1)[0]

    with ZipFile(f'uploads/{zip_file.filename}', 'r') as file:
        file.extractall(f'uploads/{filename}')

    content = os.listdir(f'uploads/{filename}')
    new_source_count = 0
    for file in content:
        if not check_file_extension(file, 'csv'):
            flash(f'Неверный формат файла {file}', 'error')
            continue

        with open(f'uploads/{filename}/{file}') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                pattern_match = check_source_with_pattern(row[0])
                create_new_source(pattern_match, row[0])
                new_source_count += 1
    return new_source_count


def add_single_resource(source):
    """
    Функция проверяет ссылку на соответствие паттерну
    и загружает валидные данные в базу.
    """
    pattern_match = check_source_with_pattern(source)
    if not pattern_match:
        return None
    new_source = create_new_source(pattern_match, source)
    return new_source


def create_new_source(pattern_match, source):
    """
    Функция создает новый объект ресурса из переданного pattern match ссылки.
    """
    protocol, domain, zone, path, params = pattern_match.groups()
    try:
        status = requests.get(source).status_code
    except Exception:
        status = None
    if status == 200:
        is_awailable = True
    else:
        is_awailable = False

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
        full_link=source,
        status_code=status,
        is_awailable=is_awailable)
    db.session.add(new_source)
    db.session.commit()
    db.session.refresh(new_source)

    return new_source

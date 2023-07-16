import csv
import os
import re
from zipfile import ZipFile

import requests

from . import db
from .constants import URL_PATTERN
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
    pattern = URL_PATTERN
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

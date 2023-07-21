import os
import yaml


def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


config = load_config('config.yaml')
port = config['database']['port']
username = config['database']['username']
password = config['database']['password']
name = config['database']['dbname']

logs_limit_config = config['api_views']['logs_limit_config']

news_per_page = config['views']['news_per_page']
logs_per_page= config['views']['logs_per_page']

# проверять каждые N секунд
check_period = config['monitoring']['check_period']
# удалять, если ресурс недоступен N проверок
keep_unavailable = config['monitoring']['keep_unavailable']


class Config(object):
    SQLALCHEMY_DATABASE_URI = f'postgresql://{username}:{password}@db:{port}/{name}'
    #SQLALCHEMY_DATABASE_URI = f'postgresql://{username}:{password}@localhost:{port}/{name}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = config['SECRET_KEY']
    UPLOAD_FOLDER = 'test_task/uploads'
    FLASK_APP = config['FLASK_APP']
    FLASK_DEBUG = config['FLASK_DEBUG']

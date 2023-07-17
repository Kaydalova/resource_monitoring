import os
import yaml


def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


config = load_config('config.yaml')
host = config['database']['host']
port = config['database']['port']
username = config['database']['username']
password = config['database']['password']
name = config['database']['dbname']

# проверять каждые N секунд
check_period = config['monitoring']['check_period']
# удалять, если ресурс недоступен N проверок
keep_unavailable = config['monitoring']['keep_unavailable'] 


class Config(object):
    SQLALCHEMY_DATABASE_URI = f'postgresql://{username}:{password}@{host}:{port}/{name}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    UPLOAD_FOLDER = 'test_task/uploads'

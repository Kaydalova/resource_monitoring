import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        default='postgresql://alexandra:alex55@localhost:5432/flask_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    UPLOAD_FOLDER = 'test_task/uploads'

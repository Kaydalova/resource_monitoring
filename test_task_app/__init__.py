from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import Config, config
from flask_jwt_extended import JWTManager
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)
app.config["JWT_SECRET_KEY"] = config['SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
jwt = JWTManager(app)
login_manager = LoginManager(app)


db = SQLAlchemy(app)

migrate = Migrate(app, db)

from . import  (api_views, views, # noqa
                auth_api_views, logging_config, # noqa
                cli_commands, auth_views, # noqa
                error_handlers) # noqa
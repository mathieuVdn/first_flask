from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'


def custom_round(value, decimals=0):
    return round(value, decimals)


app.jinja_env.globals.update(custom_round=custom_round)

from app import routes, models


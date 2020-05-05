# app/__init__.py

# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# local imports
from config import app_config
from flask_migrate import Migrate
# db variable initialization
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)

    migrate = Migrate(app, db)
    
    from app import models
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')
    
    return app
    

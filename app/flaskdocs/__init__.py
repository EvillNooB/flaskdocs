import os
import psycopg2
from oauthlib.oauth2 import WebApplicationClient
from flask import Flask
from flask_mail import Mail
from flask_twilio import Twilio
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flaskdocs.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
twilio = Twilio()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.login_message = "Войдите для доступа к этой странице"

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.client = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    twilio.init_app(app)
    app.scheduler = BackgroundScheduler(daemon=True, timezone='Asia/Tashkent')
    from flaskdocs.users.routes import users
    from flaskdocs.staff.routes import staff
    from flaskdocs.main.routes import main
    from flaskdocs.groups.routes import groups
    from flaskdocs.experiment.routes import experiment
    app.register_blueprint(experiment)
    app.register_blueprint(users)
    app.register_blueprint(staff)
    app.register_blueprint(main)
    app.register_blueprint(groups)
    app.scheduler.start()

    return app
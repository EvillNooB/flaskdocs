import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

class Config(object):
    SCHEDULER_API_ENABLED = True
    
scheduler = APScheduler()



app = Flask(__name__)
app.config['SECRET_KEY'] = 'f6d45845a43d83a48902fc182906cbd8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = "Войдите для доступа к этой странице"
db = SQLAlchemy(app)

scheduler.init_app(app)
#scheduler.start()

from flaskdocs import routes

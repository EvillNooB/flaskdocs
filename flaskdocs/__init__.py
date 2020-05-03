import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flaskdocs.config import Config
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.login_message = "Войдите для доступа к этой странице"





def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    app.scheduler = BackgroundScheduler(daemon=True)

    from flaskdocs.users.routes import users
    from flaskdocs.staff.routes import staff
    from flaskdocs.main.routes import main
    from flaskdocs.groups.routes import groups
    app.register_blueprint(users)
    app.register_blueprint(staff)
    app.register_blueprint(main)
    app.register_blueprint(groups)
    app.scheduler.start()


    
    return app
import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f6d45845a43d83a48902fc182906cbd8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.login_message = "Войдите для доступа к этой странице"

db = SQLAlchemy(app)

from flaskdocs.users.routes import users
app.register_blueprint(users)

from flaskdocs.staff.routes import staff
app.register_blueprint(staff)

from flaskdocs.main.routes import main
app.register_blueprint(main)

from flaskdocs.groups.routes import groups
app.register_blueprint(groups)
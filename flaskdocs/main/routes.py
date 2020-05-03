from flask import Blueprint, render_template, url_for, flash, redirect
from flask_login import current_user, login_required
from flaskdocs.models import Settings
from flaskdocs import  db
from flaskdocs.main.forms import NotificationSettingsForm

main = Blueprint("main", __name__)

@main.route("/", methods=['GET'])
@main.route("/landing", methods=['GET'])
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    return render_template("landing.html", title="Тест")

@main.route("/main", methods=['GET', 'POST'])
@login_required
def main_menu():
    return render_template("main.html", title="Главная страница")

@main.route("/settings/notifications", methods=['POST', 'GET'])
@login_required
def notification_settings():
    form = NotificationSettingsForm()
    db_settings = Settings.query.first()
    if not db_settings:
        defaults = Settings()
        db.session.add(defaults)
        db.session.commit()
        db_settings = Settings.query.first()
    if form.validate_on_submit():
        array = [form.first.data, form.second.data, form.third.data]
        array.sort(reverse=True)
        db_settings.first = array[0]
        db_settings.second = array[1]
        db_settings.third = array[2]
        db.session.commit()
        flash(f"Сохранено", "success")
        return redirect(url_for("notification_settings"))
    form.first.data = db_settings.first
    form.second.data = db_settings.second
    form.third.data = db_settings.third
    return render_template("notification_settings.html", title="Уведомления", form=form)

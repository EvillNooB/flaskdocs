import arrow
from flask import Blueprint, render_template, url_for, flash, redirect, current_app, Flask
from flask_login import current_user, login_required
from flaskdocs import  db
from flaskdocs.main.forms import NotificationSettingsForm
from flaskdocs.models import User, Documents, Settings
from flaskdocs.main.utils import  send_email_to_group, send_email_to_staff

main = Blueprint("main", __name__)

@main.route("/", methods=['GET'])
@main.route("/landing", methods=['GET'])
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("main.main_menu"))
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
        return redirect(url_for("main.notification_settings"))
    form.first.data = db_settings.first
    form.second.data = db_settings.second
    form.third.data = db_settings.third
    return render_template("notification_settings.html", title="Уведомления", form=form)

def checkDocuments(app: Flask):
    with app.app_context():
        print("Checking all documents")
        now = arrow.utcnow()
        settings = Settings.query.first()
        first = settings.first
        second = settings.second
        third = settings.third
        documents = Documents.query.all()
        for document in documents:
            daysleft = (document.expiration_date - now).days
            if daysleft < first and not document.first:
                staff = document.owner
                group = staff.group
                send_email_to_staff(staff=staff, document=document, daysleft=daysleft)
                send_email_to_group(staff=staff, document=document, daysleft=daysleft, group=group)
                document.first = True
                db.session.commit()
            elif daysleft < second and not document.second:
                staff = document.owner
                group = staff.group
                send_email_to_staff(staff=staff, document=document, daysleft=daysleft)
                send_email_to_group(staff=staff, document=document, daysleft=daysleft, group=group)
                document.second = True
                db.session.commit()
            elif daysleft < third and not document.third:
                staff = document.owner
                group = staff.group
                send_email_to_staff(staff=staff, document=document, daysleft=daysleft)
                send_email_to_group(staff=staff, document=document, daysleft=daysleft, group=group)
                document.third = True
                db.session.commit()
       
@main.record
def record(state):
    state.app.scheduler.add_job(checkDocuments, trigger='interval', seconds=30, misfire_grace_time=900, max_instances=1, args=[state.app])
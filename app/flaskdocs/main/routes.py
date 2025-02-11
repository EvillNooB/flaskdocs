import arrow
from flask import Blueprint, render_template, url_for, flash, redirect, current_app, make_response, Flask
from flask_login import current_user, login_required
from flaskdocs import  db
from flaskdocs.main.forms import NotificationSettingsForm
from flaskdocs.models import User, Documents, Settings
from flaskdocs.main.utils import  (
                                  send_email_to_group,
                                  send_email_to_staff,
                                  send_sms_to_staff,
                                  send_sms_to_group,
                                  )

main = Blueprint("main", __name__)


@main.record
def record(state):
    state.app.scheduler.add_job(checkDocuments, trigger='cron', hour=9, misfire_grace_time=900, max_instances=1, args=[state.app])

@main.route('/sw.js', methods=['GET'])
def sw():
    res = make_response(current_app.send_static_file('pwabuilder-sw.js'), 200)
    res.headers["Content-Type"] = "application/javascript"
    return res

@main.route('/offline.html', methods=['GET'])
def offlibe():
    return "You're woffline"

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
        # db.session.close()
    if form.validate_on_submit():
        array = [form.first.data, form.second.data, form.third.data]
        array.sort(reverse=True)
        db_settings.first = array[0]
        db_settings.second = array[1]
        db_settings.third = array[2]
        db.session.commit()
        # db.session.close()
        flash(f"Сохранено", "success")
        return redirect(url_for("main.notification_settings"))
    form.first.data = db_settings.first
    form.second.data = db_settings.second
    form.third.data = db_settings.third
    return render_template("notification_settings.html", title="Уведомления", form=form)

def checkDocuments(app: Flask):
    def commence_spam():
        staff = document.owner
        group = staff.group
        if staff.use_email:
            send_email_to_staff(staff=staff, document=document, daysleft=daysleft)
        if staff.use_phone:
            send_sms_to_staff(staff=staff, document=document, daysleft=daysleft)
        send_email_to_group(staff=staff, document=document, daysleft=daysleft, group=group)
        send_sms_to_group(staff=staff, document=document, daysleft=daysleft, group=group)
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
                commence_spam()
                document.first = True
                db.session.commit()
            elif daysleft < second and not document.second:
                commence_spam()
                document.second = True
                db.session.commit()
            elif daysleft < third and not document.third:
                commence_spam()
                document.third = True
                db.session.commit()
        # db.session.close()
    

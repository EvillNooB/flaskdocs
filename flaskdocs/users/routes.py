import phonenumbers
from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskdocs.models import User, Groups
from flaskdocs.users.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskdocs import db

users = Blueprint("users", __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, phone=form.phone.data, password=form.password.data)

        default_group = Groups.query.first()
        if default_group:
            user.group_id = default_group.id
            flash(f"Assigned to a default group - {default_group.name}", "info")

        db.session.add(user)
        db.session.commit()
        flash(f"Учетная запись создана", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Регистрация", sidebar=False, form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            input_number = phonenumbers.parse(form.login.data)
            if phonenumbers.is_valid_number(input_number):
                user = User.query.filter_by(phone=form.login.data).first()
                if user and user.password==form.password.data:
                    login_user(user,remember=form.remember.data)
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for("main"))
                else:
                    flash("Неправильный логин или пароль", "danger")
        except:
            user = User.query.filter_by(email=form.login.data).first()
            if user and user.password==form.password.data:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for("main"))
            else:
                flash("Неправильный логин или пароль", "danger")
    return render_template("login.html", title="Войти", form=form)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing"))

@users.route('/settings/account', methods=['GET', 'POST'], )
def account_settings():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # current_user.username = form.username.data
        # current_user.email = form.email.data
        # db.session.commit()
        # flash("Account info updated", "success")
        # return redirect(url_for("users.account"))
        current_user.group_id = form.group.data
        db.session.commit()
        flash("Информация обновлена", "success")
        return redirect(url_for("account_settings"))
    elif request.method == "GET":
        form.group.default = current_user.group_id
        form.process()
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone.e164
    return render_template("account_settings.html", title="Информация об аккаунте", form=form, readonly=True)

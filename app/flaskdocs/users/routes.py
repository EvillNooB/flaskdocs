import phonenumbers
import requests
import json
from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from flaskdocs.models import User, Groups
from flaskdocs.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, GoogleRegistrationForm
from flaskdocs import db

users = Blueprint("users", __name__)

def get_google_provider_cfg():
    return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()

#NOTE Google register

@users.route("/register/google", methods=['GET', 'POST'])
def register_with_google():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = current_app.client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@users.route("/register/google/callback", methods=['GET', 'POST'])
def register_with_google_callback():
    form = GoogleRegistrationForm()
    if request.method == 'GET':
        code = request.args.get("code")
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]
        token_url, headers, body = current_app.client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
        )
        token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
        )
        current_app.client.parse_request_body_response(json.dumps(token_response.json()))
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = current_app.client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        if userinfo_response.json().get("email_verified"):
            form.username.data = userinfo_response.json()["given_name"]
            form.email.data = userinfo_response.json()["email"]
            form.use_email.data = True
            form.use_phone.data = False
            return render_template("register_google.html", title="Регистрация", sidebar=False, form=form)
        else:
            return "User email not available or not verified by Google.", 400
    elif request.method == 'POST':
        if form.validate_on_submit():
            if not form.use_email.data and not form.use_phone.data:
                flash(f"Вы не выбрали способ доставки уведомлении, рекомендуется выбрать как минимум 1", "danger")
            user = User(username=form.username.data,
                        email=form.email.data,
                        phone=form.phone.data,
                        password=current_app.config['SECRET_KEY'],
                        use_phone=form.use_phone.data,
                        use_email=form.use_email.data
                        )
            default_group = Groups.query.first()
            if not default_group:
                group = Groups(name="Workgroup 1")
                db.session.add(group)
                db.session.commit()
                default_group = Groups.query.first()
            user.group_id = default_group.id
            flash(f"Assigned to a default group - {default_group.name}", "info")
            db.session.add(user)
            db.session.commit()
            # db.session.close()
            flash(f"Учетная запись создана", "success")
            return redirect(url_for("users.login"))
        return render_template("register_google.html", title="Регистрация", sidebar=False, form=form)
#NOTE Google register


#NOTE Google login
@users.route("/login/google", methods=['GET', 'POST'])
def login_with_google():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = current_app.client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@users.route("/login/google/callback", methods=['GET', 'POST'])
def login_with_google_callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = current_app.client.prepare_token_request(
    token_endpoint,
    authorization_response=request.url,
    redirect_url=request.base_url,
    code=code
    )
    token_response = requests.post(
    token_url,
    headers=headers,
    data=body,
    auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
    )
    current_app.client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = current_app.client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get("email_verified"):
        email = userinfo_response.json()["email"]
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Аккаунт не найден", "danger")
            return redirect(url_for("users.login"))
        login_user(user, remember=True)
        return redirect(url_for("main.main_menu"))
    else:
        return "User email not available or not verified by Google.", 400

#NOTE Google login



@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.main_menu"))
    form = RegistrationForm()
    if form.validate_on_submit():
        if not form.use_email.data and not form.use_phone.data:
            flash(f"Вы не выбрали способ доставки уведомлении, рекомендуется выбрать как минимум 1", "danger")
        user = User(username=form.username.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    password=form.password.data,
                    use_phone=form.use_phone.data,
                    use_email=form.use_email.data
                    )
        default_group = Groups.query.first()
        if not default_group:
            group = Groups(name="Workgroup 1")
            db.session.add(group)
            db.session.commit()
            default_group = Groups.query.first()
        user.group_id = default_group.id
        flash(f"Assigned to a default group - {default_group.name}", "info")
        db.session.add(user)
        db.session.commit()
        # db.session.close()
        flash(f"Учетная запись создана", "success")
        return redirect(url_for("users.login"))
    form.use_email.data = True
    form.use_phone.data = False
    return render_template("register.html", title="Регистрация", sidebar=False, form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.main_menu"))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            input_number = phonenumbers.parse(form.login.data)
            if phonenumbers.is_valid_number(input_number):
                user = User.query.filter_by(phone=form.login.data).first()
                if user and user.password == form.password.data:
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for("main.main_menu"))
                else:
                    flash("Неправильный логин или пароль", "danger")
        except:
            user = User.query.filter_by(email=form.login.data).first()
            if user and user.password == form.password.data:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for("main.main_menu"))
            else:
                flash("Неправильный логин или пароль", "danger")
    return render_template("login.html", title="Войти", form=form)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.landing"))

@users.route('/settings/account', methods=['GET', 'POST'], )
def account_settings():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if not form.use_email.data and not form.use_phone.data:
            flash(f"Выберите как минимум 1 способ доставки уведомлении", "danger")
            return redirect(request.referrer)
        # current_user.username = form.username.data
        # current_user.email = form.email.data
        # db.session.commit()
        # flash("Account info updated", "success")
        # return redirect(url_for("users.account"))
        current_user.group_id = form.group.data
        current_user.use_email = form.use_email.data    
        current_user.use_phone = form.use_phone.data
        db.session.commit()
        # db.session.close()
        flash("Информация обновлена", "success")
        return redirect(url_for("users.account_settings"))
    elif request.method == "GET":
        form.group.default = current_user.group_id
        form.process()
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone.e164
        form.use_email.data = current_user.use_email
        form.use_phone.data = current_user.use_phone
    return render_template("account_settings.html", title="Информация об аккаунте", form=form, readonly=True)


from flask import render_template, url_for, flash, redirect, request, abort
from flaskdocs import app, db, scheduler
from flask_login import login_user, current_user, logout_user, login_required
from flaskdocs.models import User, Staff, Documents, Settings, Groups

from flaskdocs.forms import RegistrationForm, LoginForm, UpdateAccountForm, AddDocsForm, AddStaffForm, NotificationSettingsForm, AddGroupForm, EditStaffForm
import phonenumbers, arrow


@scheduler.task('interval', id='do_job_1', seconds=30, misfire_grace_time=900)
def job1():
    print(User.query.get(1))

@app.route("/", methods=['GET'])
@app.route("/landing", methods=['GET'])
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    return render_template("landing.html", title="Тест")



@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main"))
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("landing"))

@app.route('/settings/account', methods=['GET', 'POST'], )
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

@app.route("/main", methods=['GET', 'POST'])
@login_required
def main():
    return render_template("main.html", title="Главная страница")


@app.route("/database/staff", methods=['GET'])
@login_required
def show_staff():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    dbase = Staff.query.order_by(Staff.second_name.desc()).paginate(per_page=per_page, page=page)
    return render_template("show_staff.html", dbase=dbase, title="Работники", per_page=per_page)

@app.route("/database/docs", methods=['GET'])
@login_required
def show_docs():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    dbase = Documents.query.order_by(Documents.expiration_date.asc()).paginate(per_page=per_page, page=page)
    return render_template("show_docs.html", dbase=dbase, title="Документы", per_page=per_page)

@app.route("/database/groups", methods=['POST', 'GET'])
@login_required
def view_groups():
    groups_list = Groups.query.all()
    return render_template("show_groups.html", title="Группы", dbase=groups_list)


@app.route("/database/staff/<int:member>", methods=['GET'])
@login_required
def view_staff(member):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    user_to_look = Staff.query.get(member)
    if user_to_look:
        docs = Documents.query\
            .filter_by(owner=user_to_look)\
                .order_by(Documents.expiration_date.asc())\
                    .paginate(per_page=per_page, page=page)
    else:
        abort(404)
    return render_template("specific_docs.html", per_page=per_page, page=page, staff=user_to_look, dbase=docs)

@app.route("/database/staff/<int:member>/edit", methods=['GET','POST'])
@login_required
def edit_staff(member):
    staff_member = Staff.query.get(member)
    if not staff_member:
        abort(404)
    form = EditStaffForm()
    if form.validate_on_submit():
        if form.email.data != staff_member.email:
            user = Staff.query.filter_by(email=form.email.data).first()
            if user:
                flash("Работник с такой почтой уже зарегистрирован", "danger")
                return redirect(request.referrer)
        if form.phone.data != staff_member.phone.e164:
            try:
                input_number = phonenumbers.parse(form.phone.data)
                if not (phonenumbers.is_valid_number(input_number)):
                    flash('ErrorAfterParsing: Неправильный формат номера, убедитесь что он имеет вид +71234567890 (Без пробелов между цифрами)', "danger")
                    return redirect(request.referrer)
                user = Staff.query.filter_by(phone=form.phone.data).first()
                if user:
                    flash('Работник с таким номером уже зарегистрирован', "danger")
                    return redirect(request.referrer)
            except Exception as error:
                 flash(error)
                 return redirect(request.referrer)
        staff_member.group_id = form.group.data
        staff_member.first_name = form.first_name.data 
        staff_member.second_name = form.second_name.data  
        staff_member.email = form.email.data 
        staff_member.phone = form.phone.data 
        db.session.commit()
        flash("Информация обновлена", "success")
        return redirect(url_for("view_staff", member=member))
    elif request.method == "GET":
        form.group.default = staff_member.group_id
        form.process()
        form.first_name.data = staff_member.first_name
        form.second_name.data = staff_member.second_name
        form.email.data = staff_member.email
        form.phone.data = staff_member.phone.e164
    return render_template("edit_staff.html", form=form)

@app.route("/database/groups/<int:group>", methods=['GET'])
@login_required
def specific_group(group):
    target_group = Groups.query.get(group)
    if not target_group:
        abort(404)
    return render_template("specific_group.html", group=target_group)










@app.route("/settings/notifications", methods=['POST', 'GET'])
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

        # if a < b and a < c:
        #     db_settings.third = a
        #     if b < c:
        #         db_settings.second = b
        #         db_settings.first = c
        #     else:
        #         db_settings.second = c
        #         db_settings.first = b
        # elif a < b or a < c:
        #     db_settings.second = a
        #     if b < c:
        #         db_settings.third = b
        #         db_settings.first = c
        #     else:
        #         db_settings.third = c
        #         db_settings.first = b
        # else:
        #     db_settings.first = a
        #     if b < c:
        #         db_settings.third = b
        #         db_settings.second = c
        #     else:
        #         db_settings.third = c
        #         db_settings.second = b
        
        
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

# -------------------------------  ADD DATA ------------------------------
@app.route("/register", methods=['GET', 'POST'])
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

@app.route("/database/groups/add", methods=['POST', 'GET'])
@login_required
def add_group():
    form=AddGroupForm()
    if form.validate_on_submit():
        group = Groups(name=form.name.data)
        db.session.add(group)
        db.session.commit()
        flash(f"Успешно", "success")
        return redirect(url_for("view_groups"))
    return render_template("add_group.html", form=form)


@app.route("/database/staff/add", methods=['POST', 'GET'])
@login_required
def add_staffmember():
    form=AddStaffForm()
    if form.validate_on_submit():
        staff = Staff(first_name=form.first_name.data, second_name=form.second_name.data, email=form.email.data, phone=form.phone.data, group_id=form.group.data)
        db.session.add(staff)
        db.session.commit()
        flash(f"Успешно", "success")
        return redirect(url_for("view_staff", member=staff.id))
    return render_template("add_staff.html", form=form)

@app.route("/database/docs/<int:member>/add", methods=['GET', 'POST'])
@login_required
def add_doc(member):
    form = AddDocsForm()
    if form.validate_on_submit():
        new_doc = Documents(name=form.name.data, expiration_date=arrow.get(form.date.data,'DD.MM.YYYY'), owner_id=member)
        db.session.add(new_doc)
        db.session.commit()
        flash(f"Документ успешно добавлен", "success")
        return redirect(url_for("view_staff", member=member))
    user_to_look = Staff.query.get(member)
    if not user_to_look:
        abort(404)
    return render_template("add_doc.html", staff=user_to_look, form=form)


# -------------------------------  ADD DATA ------------------------------




#------------------------- DELETE DATA -----------------------------------------

@app.route("/delete/staff/<int:staff_id>", methods=['POST'])
@login_required
def delete_staff(staff_id):
    staff = Staff.query.get(staff_id)
    if not staff:
        abort(404)
    elif staff.documents:
        flash(f"Для начала удалите документы", "danger")
        return redirect(url_for("view_staff", member=staff.id))
    else:
        db.session.delete(staff)
        db.session.commit()
        flash(f"Успешно удалено", "info")
        return redirect(url_for('show_staff'))

@app.route("/delete/doc/<int:doc_id>", methods=['POST'])
@login_required
def delete_document(doc_id):
    document = Documents.query.get(doc_id)
    if document:
        db.session.delete(document)
        db.session.commit()
        flash(f"Документ успешно удалён", "info")
    else:
        abort(404)
    return redirect(request.referrer)
  
@app.route("/delete/group/<int:group_id>", methods=['POST'])
@login_required
def delete_group(group_id):
    group = Groups.query.get(group_id)
    if group:
        if group.staff_count or group.user_count:
            flash(f"Для удаления группа должна быть пуста", "danger")
            return redirect(request.referrer)
        db.session.delete(group)
        db.session.commit()
        flash(f"Группа успешно удалена", "info")
    else:
        abort(404)
    return redirect(request.referrer)

#------------------------- DELETE DATA  -----------------------------------------
# master branch

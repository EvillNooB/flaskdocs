import phonenumbers
import arrow
from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_required
from flaskdocs.models import Staff, Documents
from flaskdocs.staff.forms import AddDocsForm, AddStaffForm, EditStaffForm
from flaskdocs import db

staff = Blueprint("staff", __name__)

# NOTE Add data --------------------------

@staff.route("/database/staff/add", methods=['POST', 'GET'])
@login_required
def add_staffmember():
    form = AddStaffForm()
    if form.validate_on_submit():
        staff_member = Staff(first_name=form.first_name.data, 
                             second_name=form.second_name.data,
                             email=form.email.data,
                             phone=form.phone.data,
                             group_id=form.group.data,
                             use_phone=form.use_phone.data,
                             use_email=form.use_email.data
                             )
        db.session.add(staff_member)
        db.session.commit()
        db.session.close()
        flash(f"Успешно", "success")
        return redirect(url_for("staff.lookup_staff", member=staff_member.id))
    return render_template("add_staff.html", form=form)

@staff.route("/database/docs/<int:member>/add", methods=['GET', 'POST'])
@login_required
def add_doc(member):
    form = AddDocsForm()
    if form.validate_on_submit():
        new_doc = Documents(name=form.name.data, expiration_date=arrow.get(form.date.data, 'DD.MM.YYYY'), owner_id=member)
        db.session.add(new_doc)
        db.session.commit()
        db.session.close()
        flash(f"Документ успешно добавлен", "success")
        return redirect(url_for("staff.lookup_staff", member=member))
    staff_member = Staff.query.get(member)
    if not staff_member:
        abort(404)
    return render_template("add_doc.html", staff=staff_member, form=form)


# NOTE Delete data --------------------------

@staff.route("/delete/staff/<int:staff_id>", methods=['POST'])
@login_required
def delete_staff(staff_id):
    staff_member = Staff.query.get(staff_id)
    if not staff_member:
        abort(404)
    elif staff_member.documents:
        flash(f"Для начала удалите документы", "danger")
        return redirect(url_for("staff.lookup_staff", member=staff_member.id))
    else:
        db.session.delete(staff_member)
        db.session.commit()
        db.session.close()
        flash(f"Успешно удалено", "info")
        return redirect(url_for('staff.show_staff'))

@staff.route("/delete/doc/<int:doc_id>", methods=['POST'])
@login_required
def delete_document(doc_id):
    document = Documents.query.get(doc_id)
    if document:
        db.session.delete(document)
        db.session.commit()
        db.session.close()
        flash(f"Документ успешно удалён", "info")
    else:
        abort(404)
    return redirect(request.referrer)


# NOTE Edit data

@staff.route("/database/staff/<int:member>/edit", methods=['GET','POST'])
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
        staff_member.use_email = form.use_email.data
        staff_member.use_phone = form.use_phone.data
        db.session.commit()
        db.session.close()
        flash("Информация обновлена", "success")
        return redirect(url_for("staff.lookup_staff", member=member))
    elif request.method == "GET":
        form.group.default = staff_member.group_id
        form.process()
        form.first_name.data = staff_member.first_name
        form.second_name.data = staff_member.second_name
        form.email.data = staff_member.email
        form.phone.data = staff_member.phone.e164
        form.use_email.data = staff_member.use_email
        form.use_phone.data = staff_member.use_phone
    return render_template("edit_staff.html", form=form)

@staff.route("/database/staff/<int:member>", methods=['GET'])
@login_required
def lookup_staff(member):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    staff_member = Staff.query.get(member)
    if staff_member:
        docs = Documents.query\
            .filter_by(owner=staff_member)\
                .order_by(Documents.expiration_date.asc())\
                    .paginate(per_page=per_page, page=page)
    else:
        abort(404)
    return render_template("lookup_staff.html", per_page=per_page, page=page, staff=staff_member, dbase=docs)

@staff.route("/database/staff", methods=['GET'])
@login_required
def show_staff():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    dbase = Staff.query.order_by(Staff.second_name.desc()).paginate(per_page=per_page, page=page)
    return render_template("show_staff.html", dbase=dbase, title="Работники", per_page=per_page)

@staff.route("/database/docs", methods=['GET'])
@login_required
def show_docs():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    dbase = Documents.query.order_by(Documents.expiration_date.asc()).paginate(per_page=per_page, page=page)
    return render_template("show_docs.html", dbase=dbase, title="Документы", per_page=per_page)

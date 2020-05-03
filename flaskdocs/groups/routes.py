from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_required
from flaskdocs.models import Groups
from flaskdocs.groups.forms import AddGroupForm
from flaskdocs import db

groups = Blueprint("groups", __name__)

@groups.route("/database/groups/add", methods=['POST', 'GET'])
@login_required
def add_group():
    form = AddGroupForm()
    if form.validate_on_submit():
        group = Groups(name=form.name.data)
        db.session.add(group)
        db.session.commit()
        flash(f"Успешно", "success")
        return redirect(url_for("groups.view_groups"))
    return render_template("add_group.html", form=form)

@groups.route("/delete/group/<int:group_id>", methods=['POST'])
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

@groups.route("/database/groups/<int:group>", methods=['GET'])
@login_required
def lookup_group(group):
    target_group = Groups.query.get(group)
    if not target_group:
        abort(404)
    return render_template("lookup_group.html", group=target_group)

@groups.route("/database/groups", methods=['POST', 'GET'])
@login_required
def view_groups():
    groups_list = Groups.query.all()
    return render_template("show_groups.html", title="Группы", dbase=groups_list)

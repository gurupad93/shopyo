"""
.. module:: AdminViews
   :synopsis: All endpoints of the admin views are defined here.

"""
import os
import json

from flask import Blueprint, render_template, request, redirect

from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from shopyoapi.init import db

from shopyoapi.enhance import base_context
from sqlalchemy import exists
from modules.admin.admin import admin_required
from modules.admin.models import Users

dirpath = os.path.dirname(os.path.abspath(__file__))
module_info = {}

with open(dirpath + "/info.json") as f:
    module_info = json.load(f)

admin_blueprint = Blueprint(
    "admin",
    __name__,
    template_folder="templates",
    url_prefix=module_info["url_prefix"],
)


class AdminForm(FlaskForm):
    id = StringField('id')
    name = StringField('name')
    password = PasswordField('password')
    admin_user = BooleanField('admin_user')


@admin_blueprint.route("/")
@login_required
@admin_required
def user_list():
    """
           **Get The List of Users**

            Lists all users in the database.

    """
    context = base_context()
    context["users"] = Users.query.all()
    return render_template("admin/index.html", **context)


@admin_blueprint.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def user_add():
    """
               **Adds a User**

            adds a user to database.

    """
    context = base_context()
    admin_form = AdminForm()
    if admin_form.validate_on_submit():
        id = admin_form.id.data
        name = admin_form.name.data
        password = admin_form.password.data
        admin_user = admin_form.admin_user.data
        has_user = db.session.query(exists().where(Users.id == id)).scalar()

        if has_user is False:
            new_user = Users(id=id, name=name, admin_user=admin_user)
            new_user.set_hash(password)
            db.session.add(new_user)
            db.session.commit()
            return render_template("admin/add.html", **context)
    return render_template("admin/add.html", **context)


@admin_blueprint.route("/delete/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def admin_delete(id):
    """
                   **Delete a User**

        :param id: id of the user
        :type id: int

    """
    Users.query.filter(Users.id == id).delete()
    db.session.commit()
    return redirect("/admin")


@admin_blueprint.route("/edit/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def appointment_edit(id):
    """
                   **Update information for a User**

        :param id: id of the user
        :type id: int

    """
    context = base_context()
    u = Users.query.get(id)
    context["id"] = u.id
    context["name"] = u.name
    context["password"] = u.password
    context["admin_user"] = u.admin_user
    return render_template("admin/edit.html", **context)


@admin_blueprint.route("/update", methods=["GET", "POST"])
@login_required
@admin_required
def admin_update():
    """
                   **Update a User record**

    """
    admin_form = AdminForm()
    id = admin_form.id.data
    name = admin_form.name.data
    password = admin_form.password.data
    admin_user = admin_form.admin_user.data
    u = Users.query.get(id)
    u.name = name
    u.set_hash(password)
    u.admin_user = admin_user
    db.session.add(u)
    db.session.commit()
    return redirect("/admin")

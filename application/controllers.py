from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from flask import current_app as app

from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from application.database import db
from application.models import User


@app.route("/")
def home():
    if current_user.is_authenticated:

        if current_user.role == "Admin":
            return redirect(url_for("admin_dashboard"))

        if current_user.role == "Trek Staff":
            return redirect(url_for("staff_dashboard"))

        return redirect(url_for("user_dashboard"))

    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    role = request.form["role"]

    user = User.query.filter_by(email=email).first()

    if user:
        return "User already exists."

    approved = False

    if role == "User":
        approved = True

    new_user = User(
        name=name,
        email=email,
        password=password,
        role=role,
        is_approved=approved
    )

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(
        email=email,
        password=password
    ).first()

    if user is None:
        return "Invalid Email or Password."

    if user.is_blacklisted:
        return "Your account has been blacklisted."

    if user.role == "Trek Staff" and user.is_approved is False:
        return "Waiting for Admin approval."

    login_user(user)

    if user.role == "Admin":
        return redirect(url_for("admin_dashboard"))

    if user.role == "Trek Staff":
        return redirect(url_for("staff_dashboard"))

    return redirect(url_for("user_dashboard"))


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "Admin":
        return "Access Denied."

    return render_template("admin/dashboard.html")


@app.route("/staff/dashboard")
@login_required
def staff_dashboard():

    if current_user.role != "Trek Staff":
        return "Access Denied."

    return render_template("staff/dashboard.html")


@app.route("/user/dashboard")
@login_required
def user_dashboard():

    if current_user.role != "User":
        return "Access Denied."

    return render_template("user/dashboard.html")
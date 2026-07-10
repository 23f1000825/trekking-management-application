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
from application.models import User,Trek,Booking


@app.route("/")
def home():
    if current_user.is_authenticated:

        if current_user.role == "Admin":
            return redirect(url_for("admin_dashboard"))

        if current_user.role == "Trek Staff":
            return redirect(url_for("staff_dashboard"))

        return redirect(url_for("user_dashboard"))

    return redirect(url_for("login"))

#register user
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

#login
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

#logout
@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))

#ADMIN DASHBOARD
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "Admin":
        return "Access Denied."

    total_treks = Trek.query.count()

    total_users = User.query.filter_by(role="User").count()

    total_staff = User.query.filter_by(role="Trek Staff").count()

    total_bookings = Booking.query.count()

    return render_template(
        "admin/dashboard.html",
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings
    )

#STAFF DASHBOARD
@app.route("/staff/dashboard")
@login_required
def staff_dashboard():

    if current_user.role != "Trek Staff":
        return "Access Denied."

    return render_template("staff/dashboard.html")

#no access without login
@app.route("/user/dashboard")
@login_required
def user_dashboard():

    if current_user.role != "User":
        return "Access Denied."

    return render_template("user/dashboard.html")

#ADMIN CRUD OPS
@app.route("/admin/treks")
@login_required
def view_treks():

    if current_user.role != "Admin":
        return "Access Denied."

    treks = Trek.query.all()

    return render_template(
        "admin/view_treks.html",
        treks=treks
    )


@app.route("/admin/treks/add", methods=["GET", "POST"])
@login_required
def add_trek():

    if current_user.role != "Admin":
        return "Access Denied."

    staff_members = User.query.filter_by(
        role="Trek Staff",
        is_approved=True,
        is_blacklisted=False
    ).all()

    if request.method == "GET":
        return render_template(
            "admin/add_trek.html",
            staff_members=staff_members
        )

    assigned_staff = request.form["assigned_staff"]

    if assigned_staff == "":
        assigned_staff = None
    else:
        assigned_staff = int(assigned_staff)

    trek = Trek(
        trek_name=request.form["trek_name"],
        location=request.form["location"],
        difficulty=request.form["difficulty"],
        duration=int(request.form["duration"]),
        available_slots=int(request.form["available_slots"]),
        assigned_staff_id=assigned_staff,
        status=request.form["status"]
    )

    db.session.add(trek)
    db.session.commit()

    return redirect(url_for("view_treks"))

@app.route("/admin/treks/edit/<int:trek_id>", methods=["GET", "POST"])
@login_required
def edit_trek(trek_id):

    if current_user.role != "Admin":
        return "Access Denied."

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "GET":
        return render_template(
            "admin/edit_trek.html",
            trek=trek
        )

    trek.trek_name = request.form["trek_name"]
    trek.location = request.form["location"]
    trek.difficulty = request.form["difficulty"]
    trek.duration = int(request.form["duration"])
    trek.available_slots = int(request.form["available_slots"])
    trek.status = request.form["status"]

    db.session.commit()

    return redirect(url_for("view_treks"))

@app.route("/admin/treks/delete/<int:trek_id>")
@login_required
def delete_trek(trek_id):

    if current_user.role != "Admin":
        return "Access Denied."

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)
    db.session.commit()

    return redirect(url_for("view_treks"))

#ADMIN APPROVE TREK STAFF
@app.route("/admin/staff")
@login_required
def view_staff():

    if current_user.role != "Admin":
        return "Access Denied."

    staff = User.query.filter_by(role="Trek Staff").all()

    return render_template(
        "admin/view_staff.html",
        staff=staff
    )

#ADMIN APPROVAL TO TREK
@app.route("/admin/staff/approve/<int:user_id>")
@login_required
def approve_staff(user_id):

    if current_user.role != "Admin":
        return "Access Denied."

    staff = User.query.get_or_404(user_id)

    staff.is_approved = True

    db.session.commit()

    return redirect(url_for("view_staff"))

#ADMIN BLACKLISTS STAFF
@app.route("/admin/staff/blacklist/<int:user_id>")
@login_required
def blacklist_staff(user_id):

    if current_user.role != "Admin":
        return "Access Denied."

    staff = User.query.get_or_404(user_id)

    staff.is_blacklisted = True

    db.session.commit()

    return redirect(url_for("view_staff"))

#ACTIVATES/REMOVE STAFF FROM BLACKLIST
@app.route("/admin/staff/activate/<int:user_id>")
@login_required
def activate_staff(user_id):

    if current_user.role != "Admin":
        return "Access Denied."

    staff = User.query.get_or_404(user_id)

    staff.is_blacklisted = False

    db.session.commit()

    return redirect(url_for("view_staff"))

#
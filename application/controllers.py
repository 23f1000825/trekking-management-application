from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import jsonify
from flask import session
from flask import make_response

from flask import current_app as app

from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from application.database import db
from application.models import User,Trek,Booking, StaffProfile
from werkzeug.security import generate_password_hash, check_password_hash
from application.auth_jwt import generate_jwt, decode_jwt, get_jwt_from_request

from datetime import date,datetime, timedelta
from sqlalchemy import or_

@app.before_request
def sync_jwt_auth():
    if not current_user.is_authenticated:
        token = get_jwt_from_request()
        if token:
            payload = decode_jwt(token)
            if payload and "user_id" in payload:
                user = User.query.get(payload["user_id"])
                if user and not user.is_blacklisted:
                    login_user(user, remember=False)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "application": "TrekALine", "version": "1.0.0"}), 200


@app.route("/")
def home():
    if current_user.is_authenticated:

        if current_user.role == "Admin":
            return redirect(url_for("admin_dashboard"))

        if current_user.role == "Trek Staff":
            return redirect(url_for("staff_dashboard"))

        return redirect(url_for("user_dashboard"))

    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    role = request.form.get("role", "User")

    if not name or not email or not password:
        flash("Please fill in all required fields.", "danger")
        return render_template("register.html")

    if confirm_password and password != confirm_password:
        flash("Passwords do not match. Please verify your password.", "danger")
        return render_template("register.html")

    if len(password) < 4:
        flash("Password must be at least 4 characters long.", "danger")
        return render_template("register.html")

    user = User.query.filter(db.func.lower(User.email) == email).first()

    if user:
        flash("An account with this email address already exists.", "danger")
        return render_template("register.html")

    approved = False

    if role == "User":
        approved = True

    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        role=role,
        is_approved=approved
    )

    db.session.add(new_user)
    db.session.commit()

    if role == "Trek Staff":
        profile = StaffProfile(
            user_id=new_user.user_id
        )

        db.session.add(profile)
        db.session.commit()
        flash("Staff account created successfully! Please wait for Admin approval.", "info")
    else:
        flash("Account created successfully! Please log in.", "success")

    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = User.query.filter(
        db.func.lower(User.email) == email
    ).first()

    if user is None:
        flash("Invalid Email or Password.", "danger")
        return render_template("login.html")

    password_matches = False
    try:
        password_matches = check_password_hash(user.password, password)
    except Exception:
        pass

    if not password_matches and user.password == password:
        password_matches = True

    if not password_matches:
        flash("Invalid Email or Password.", "danger")
        return render_template("login.html")

    if user.is_blacklisted:
        flash("Your account has been blacklisted.", "danger")
        return render_template("login.html")

    if user.role == "Trek Staff" and user.is_approved is False:
        flash("Waiting for Admin approval.", "warning")
        return render_template("login.html")

    session.permanent = True
    login_user(user, remember=False)
    token = generate_jwt(user)

    user_info = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

    if user.role == "Admin":
        target_url = url_for("admin_dashboard")
    elif user.role == "Trek Staff":
        target_url = url_for("staff_dashboard")
    else:
        target_url = url_for("user_dashboard")

    flash(f"Welcome back, {user.name}!", "success")
    response = make_response(redirect(target_url))
    response.set_cookie("jwt_token", token, max_age=86400 * 7, httponly=False, samesite="Lax")
    response.headers["X-Auth-Token"] = token
    return response

@app.route("/logout")
def logout():
    logout_user()
    session.clear()

    response = make_response(redirect(url_for("login")))

    response.delete_cookie("jwt_token", path="/")
    response.delete_cookie("remember_token", path="/")
    response.delete_cookie("session", path="/")

    return response

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "Admin":
        return "Access Denied."

    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role="User").count()
    total_staff = User.query.filter_by(role="Trek Staff").count()
    total_bookings = Booking.query.count()


    open_treks = Trek.query.filter_by(status="Open").count()
    closed_treks = Trek.query.filter_by(status="Closed").count()
    ongoing_treks = Trek.query.filter_by(status="Ongoing").count()
    completed_treks = Trek.query.filter_by(status="Completed").count()


    booked = Booking.query.filter_by(booking_status="Booked").count()
    cancelled = Booking.query.filter_by(booking_status="Cancelled").count()
    completed_booking = Booking.query.filter_by(
        booking_status="Completed"
    ).count()

    return render_template(
        "admin/dashboard.html",

        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings,

        trek_chart=[
            open_treks,
            closed_treks,
            ongoing_treks,
            completed_treks
        ],

        booking_chart=[
            booked,
            cancelled,
            completed_booking
        ],

        user_chart=[
            total_users,
            total_staff,
            1
        ]
    )

@app.route("/staff/dashboard")
@login_required
def staff_dashboard():

    if current_user.role != "Trek Staff":
        return "Access Denied."

    treks = Trek.query.filter_by(
        assigned_staff_id=current_user.user_id
    ).all()

    trek_data = []

    total_participants = 0
    open_treks = 0

    trek_labels = []
    participant_counts = []

    for trek in treks:

        participant_count = Booking.query.filter_by(
            trek_id=trek.trek_id,
            booking_status="Booked"
        ).count()

        total_participants += participant_count

        if trek.status == "Open":
            open_treks += 1

        trek_data.append({
            "trek": trek,
            "participant_count": participant_count
        })

        trek_labels.append(trek.trek_name)
        participant_counts.append(participant_count)

    return render_template(
        "staff/dashboard.html",
        trek_data=trek_data,
        total_treks=len(treks),
        total_participants=total_participants,
        open_treks=open_treks,
        trek_labels=trek_labels,
        participant_counts=participant_counts
    )


from sqlalchemy import or_    

@app.route("/user/dashboard")
@login_required
def user_dashboard():

    if current_user.role != "User":
        return "Access Denied."

    difficulty = request.args.get("difficulty", "")
    keyword = request.args.get("keyword", "")

    treks = Trek.query.filter_by(status="Open")

    if difficulty:
        treks = treks.filter(Trek.difficulty == difficulty)

    if keyword:
        treks = treks.filter(
            or_(
                Trek.trek_name.ilike(f"%{keyword}%"),
                Trek.location.ilike(f"%{keyword}%")
            )
        )

    treks = treks.all()
    bookings = Booking.query.filter_by(
        user_id=current_user.user_id,
        booking_status="Booked"
    ).all()
    booked_trek_ids = [b.trek_id for b in bookings]

    return render_template(
        "user/dashboard.html",
        treks=treks,
        my_bookings=bookings,
        booked_trek_ids=booked_trek_ids,
        difficulty=difficulty,
        keyword=keyword
    )

@app.route("/admin/treks")
@login_required
def view_treks():

    if current_user.role != "Admin":
        return "Access Denied."

    search = request.args.get("search", "").strip()

    if search:
        treks = Trek.query.filter(
            Trek.trek_name.ilike(f"%{search}%")
        ).all()
    else:
        treks = Trek.query.all()

    return render_template(
        "admin/view_treks.html",
        treks=treks,
        search=search
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
            staff_members=staff_members,
            today=date.today().isoformat()
        )

    assigned_staff = request.form["assigned_staff"]


    if assigned_staff == "":
        assigned_staff = None
    else:
        assigned_staff = int(assigned_staff)

    existing_trek = Trek.query.filter(
        db.func.lower(Trek.trek_name) ==
        request.form["trek_name"].strip().lower()
    ).first()

    if existing_trek:
        flash("A trek with the same name already exists", "danger")
        return render_template(
                "admin/add_trek.html",
                staff_members=staff_members,
                today=date.today().isoformat()
    )

    start_date = datetime.strptime(
        request.form["start_date"],
        "%Y-%m-%d"
    ).date()

    if start_date < date.today():
            flash("Start date cannot be in the past.", "danger")
            return render_template(
                "admin/add_trek.html",
                staff_members=staff_members,
                today=date.today().isoformat()
    )

    duration = int(request.form["duration"])

    end_date = start_date + timedelta(days=duration)

    trek = Trek(
        trek_name=request.form["trek_name"],
        location=request.form["location"],
        difficulty=request.form["difficulty"],
        duration=duration,
        available_slots=int(request.form["available_slots"]),
        assigned_staff_id=assigned_staff,
        status=request.form["status"],
        start_date=start_date,
        end_date=end_date
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

    staff_members = User.query.filter_by(
        role="Trek Staff",
        is_approved=True,
        is_blacklisted=False
    ).all()

    if request.method == "GET":
        return render_template(
            "admin/edit_trek.html",
            trek=trek,
            staff_members=staff_members,
            today=date.today().isoformat()
        )

    existing_trek = Trek.query.filter(
        db.func.lower(Trek.trek_name) ==
        request.form["trek_name"].strip().lower(),
        Trek.trek_id != trek.trek_id
    ).first()

    if existing_trek:
        flash("Another trek with this name already exists.", "danger")
        return render_template(
            "admin/edit_trek.html",
            trek=trek,
            staff_members=staff_members
        )

    start_date = datetime.strptime(
        request.form["start_date"],
        "%Y-%m-%d"
    ).date()

    if start_date < date.today():
        flash("Start date cannot be in the past.", "danger")
        return render_template(
            "admin/edit_trek.html",
            trek=trek,
            staff_members=staff_members,
            today=date.today().isoformat()
        )

    assigned_staff = request.form["assigned_staff"]

    if assigned_staff == "":
        trek.assigned_staff_id = None
    else:
        trek.assigned_staff_id = int(assigned_staff)

    trek.trek_name = request.form["trek_name"]
    trek.location = request.form["location"]
    trek.difficulty = request.form["difficulty"]
    trek.duration = int(request.form["duration"])
    trek.available_slots = int(request.form["available_slots"])
    trek.status = request.form["status"]

    trek.start_date = start_date
    trek.end_date = start_date + timedelta(days=trek.duration)

    db.session.commit()

    flash("Trek updated successfully.", "success")

    return redirect(url_for("view_treks"))

@app.route("/admin/treks/delete/<int:trek_id>")
@login_required
def delete_trek(trek_id):

    if current_user.role != "Admin":
        return "Access Denied."

    trek = Trek.query.get_or_404(trek_id)

    if trek.bookings:
        flash(
            "Cannot delete a trek that has bookings.","danger"
        )
        return redirect(url_for("view_treks"))

    db.session.delete(trek)
    db.session.commit()

    flash(
        "Trek deleted successfully.",
        "success"
    )

    return redirect(url_for("view_treks"))

@app.route("/admin/staff")
@login_required
def view_staff():

    if current_user.role != "Admin":
        return "Access Denied."

    staff = User.query.filter_by(
        role="Trek Staff"
    ).outerjoin(StaffProfile).all()

    return render_template(
        "admin/view_staff.html",
        staff=staff
    )

@app.route("/admin/staff/approve/<int:user_id>")
@login_required
def approve_staff(user_id):

    if current_user.role != "Admin":
        return "Access Denied."

    staff = User.query.get_or_404(user_id)

    staff.is_approved = True

    db.session.commit()

    return redirect(url_for("view_staff"))

@app.route("/admin/staff/delete/<int:user_id>")
@login_required
def delete_staff(user_id):

    if current_user.role != "Admin":
        return "Access Denied."

    staff = User.query.get_or_404(user_id)

    if staff.role != "Trek Staff":
        return "Invalid Staff."

    profile = StaffProfile.query.filter_by(
    user_id=staff.user_id
    ).first()

    if profile:
        db.session.delete(profile)

    db.session.delete(staff)
    db.session.commit()

    return redirect(url_for("view_staff"))

@app.route("/admin/staff/blacklist/<int:user_id>")
@login_required
def blacklist_staff(user_id):

    if current_user.role != "Admin":
        return "Access Denied."

    staff = User.query.get_or_404(user_id)

    if staff.role == "Admin":
        return "Cannot blacklist Admin."

    staff.is_blacklisted = True

    db.session.commit()

    return redirect(url_for("view_staff"))

@app.route("/admin/staff/activate/<int:user_id>")
@login_required
def activate_staff(user_id):

    if current_user.role != "Admin":
        return "Access Denied."

    staff = User.query.get_or_404(user_id)

    if staff.role == "Admin":
        return "Cannot modify Admin."

    staff.is_blacklisted = False

    db.session.commit()

    return redirect(url_for("view_staff"))

@app.route("/admin/users")
@login_required
def view_users():

    if current_user.role != "Admin":
        return "Access Denied."

    search = request.args.get("search", "")

    users = User.query.filter_by(role="User")

    if search:
        users = users.filter(
            User.name.ilike(f"%{search}%")
        )

    users = users.all()

    return render_template(
        "admin/view_users.html",
        users=users,
        search=search
    )

@app.route("/admin/users/blacklist/<int:user_id>")
@login_required
def blacklist_user(user_id):

    if current_user.role != "Admin":
        return "Access Denied."

    user = User.query.get_or_404(user_id)

    user.is_blacklisted = True

    db.session.commit()

    return redirect(url_for("view_users"))

@app.route("/admin/users/activate/<int:user_id>")
@login_required
def activate_user(user_id):

    if current_user.role != "Admin":
        return "Access Denied."

    user = User.query.get_or_404(user_id)

    user.is_blacklisted = False

    db.session.commit()

    return redirect(url_for("view_users"))

@app.route("/admin/search", methods=["GET", "POST"])
@login_required
def admin_search():

    if current_user.role != "Admin":
        return "Access Denied."

    users = []
    staff = []
    treks = []

    if request.method == "POST":

        keyword = request.form["keyword"]

        users = User.query.filter(
            User.role == "User",
            or_(
                User.name.ilike(f"%{keyword}%"),
                db.cast(User.user_id, db.String).ilike(f"%{keyword}%")
            )
        ).all()

        staff = User.query.filter(
            User.role == "Trek Staff",
            or_(
                User.name.ilike(f"%{keyword}%"),
                db.cast(User.user_id, db.String).ilike(f"%{keyword}%")
            )
        ).all()

        treks = Trek.query.filter(
            or_(
                Trek.trek_name.ilike(f"%{keyword}%"),
                db.cast(Trek.trek_id, db.String).ilike(f"%{keyword}%")
            )
        ).all()

    return render_template(
        "admin/search.html",
        users=users,
        staff=staff,
        treks=treks,
        keyword=request.form.get("keyword", "")
    )

@app.route("/staff/trek/<int:trek_id>", methods=["GET", "POST"])
@login_required
def staff_trek(trek_id):

    if current_user.role != "Trek Staff":
        return "Access Denied."

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != current_user.user_id:
        return "Access Denied."

    bookings = Booking.query.filter_by(
        trek_id=trek.trek_id
    ).all()

    if request.method == "POST":

        action = request.form.get("action")
        booking_id = request.form.get("booking_id")

        if action == "cancel_booking" and booking_id:
            target_booking = Booking.query.get(int(booking_id))
            if target_booking and target_booking.trek_id == trek.trek_id:
                if target_booking.booking_status == "Booked":
                    target_booking.booking_status = "Cancelled"
                    target_booking.payment_status = "Refunded"
                    trek.available_slots += 1
                    flash(f"Booking for {target_booking.user.name} cancelled.", "info")
        elif action == "complete_booking" and booking_id:
            target_booking = Booking.query.get(int(booking_id))
            if target_booking and target_booking.trek_id == trek.trek_id:
                target_booking.booking_status = "Completed"
                flash(f"Booking for {target_booking.user.name} marked as completed.", "success")
        else:
            if "available_slots" in request.form:
                try:
                    slots_val = int(request.form.get("available_slots"))
                    if slots_val >= 0:
                        trek.available_slots = slots_val
                except (ValueError, TypeError):
                    pass

            if action == "started":
                trek.status = "Started"
                flash("Trek status updated to Started.", "success")
            elif action == "completed":
                trek.status = "Completed"
                for booking in bookings:
                    if booking.booking_status == "Booked":
                        booking.booking_status = "Completed"
                flash("Trek status updated to Completed.", "success")
            elif action == "update":
                flash("Trek details updated successfully.", "success")

        db.session.commit()
        return redirect(url_for("staff_trek", trek_id=trek.trek_id))

    total_slots = trek.available_slots + len([
        b for b in bookings
        if b.booking_status == "Booked"
    ])

    return render_template(
        "staff/trek.html",
        trek=trek,
        bookings=bookings,
        total_slots=total_slots
    )

@app.route("/staff/profile", methods=["GET", "POST"])
@login_required
def staff_profile():

    if current_user.role != "Trek Staff":
        return "Access Denied."

    profile = StaffProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    if profile is None:
        profile = StaffProfile(
            user_id=current_user.user_id
        )
        db.session.add(profile)
        db.session.commit()

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        contact_number = request.form.get("contact_number", "").strip()
        experience_raw = request.form.get("experience", "").strip()

        if not name or not email:
            flash("Name and email fields cannot be empty.", "danger")
            return render_template("staff/profile.html", profile=profile, user=current_user)

        existing_user = User.query.filter(
            db.func.lower(User.email) == email,
            User.user_id != current_user.user_id
        ).first()

        if existing_user:
            flash("This email address is already in use by another account.", "danger")
            return render_template("staff/profile.html", profile=profile, user=current_user)

        current_user.name = name
        current_user.email = email
        profile.contact_number = contact_number
        if experience_raw.isdigit():
            profile.experience = int(experience_raw)

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("staff_profile"))

    return render_template(
        "staff/profile.html",
        profile=profile,
        user=current_user
    )

@app.route("/staff/participants/<int:trek_id>")
@login_required
def participant_list(trek_id):

    if current_user.role != "Trek Staff":
        return "Access Denied."

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != current_user.user_id:
        return "Access Denied."

    bookings = Booking.query.filter_by(
        trek_id=trek_id
    ).all()

    return render_template(
        "staff/participants.html",
        trek=trek,
        bookings=bookings
    )

@app.route("/user/profile", methods=["GET", "POST"])
@login_required
def user_profile():

    if current_user.role != "User":
        return "Access Denied."

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not name or not email:
            flash("Name and email fields cannot be empty.", "danger")
            return render_template("user/profile.html", user=current_user)

        existing_user = User.query.filter(
            db.func.lower(User.email) == email,
            User.user_id != current_user.user_id
        ).first()

        if existing_user:
            flash("This email address is already in use by another account.", "danger")
            return render_template("user/profile.html", user=current_user)

        current_user.name = name
        current_user.email = email

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("user_profile"))

    return render_template(
        "user/profile.html",
        user=current_user
    )

@app.route("/user/trek/<int:trek_id>")
@login_required
def trek_details(trek_id):

    if current_user.role != "User":
        return "Access Denied."

    trek = Trek.query.get_or_404(trek_id)

    is_booked = Booking.query.filter_by(
        user_id=current_user.user_id,
        trek_id=trek.trek_id,
        booking_status="Booked"
    ).first() is not None

    return render_template(
        "user/trek_details.html",
        trek=trek,
        is_booked=is_booked
    )

@app.route("/user/book/<int:trek_id>")
@login_required
def book_trek(trek_id):

    if current_user.role != "User":
        return "Access Denied."

    trek = Trek.query.get_or_404(trek_id)

    existing_booking = Booking.query.filter_by(
        user_id=current_user.user_id,
        trek_id=trek.trek_id,
        booking_status="Booked"
    ).first()

    if existing_booking:
        flash("You have already booked this trek.", "info")
        return redirect(url_for("user_bookings"))

    if trek.status != "Open":
        flash("This trek is not open for booking.", "warning")
        return redirect(url_for("user_dashboard"))

    if trek.available_slots <= 0:
        flash("No slots available for this trek.", "danger")
        return redirect(url_for("user_dashboard"))

    booking = Booking(
        user_id=current_user.user_id,
        trek_id=trek.trek_id,
        booking_date=datetime.now(),
        booking_status="Booked"
    )

    trek.available_slots -= 1

    db.session.add(booking)
    db.session.commit()

    flash(f"Successfully booked '{trek.trek_name}'!", "success")
    return redirect(url_for("user_bookings"))

@app.route("/user/bookings")
@login_required
def user_bookings():

    if current_user.role != "User":
        return "Access Denied."

    bookings = Booking.query.filter(
        Booking.user_id == current_user.user_id,
        Booking.booking_status != "Completed",
        Booking.booking_status != "Cancelled"
    ).all()

    return render_template(
        "user/bookings.html",
        bookings=bookings
    )

@app.route("/user/history")
@login_required
def user_history():

    if current_user.role != "User":
        return "Access Denied."

    history = Booking.query.filter(
        Booking.user_id == current_user.user_id,
        Booking.booking_status.in_(["Completed", "Cancelled"])
    ).all()

    completed = Booking.query.filter_by(
        user_id=current_user.user_id,
        booking_status="Completed"
    ).count()

    cancelled = Booking.query.filter_by(
        user_id=current_user.user_id,
        booking_status="Cancelled"
    ).count()

    history_chart = [
        completed,
        cancelled
    ]

    return render_template(
        "user/history.html",
        history=history,
        history_chart=history_chart
    )

@app.route("/user/cancel/<int:booking_id>")
@login_required
def cancel_booking(booking_id):

    if current_user.role != "User":
        return "Access Denied."

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.user_id:
        return "Access Denied."

    if booking.booking_status != "Booked":
        return redirect(url_for("user_bookings"))

    booking.booking_status = "Cancelled"

    booking.trek.available_slots += 1

    db.session.commit()

    return redirect(url_for("user_bookings"))

@app.route("/admin/bookings")
@login_required
def admin_bookings():

    if current_user.role != "Admin":
        return "Access Denied."

    search = request.args.get("search", "")

    bookings = Booking.query

    if search:

        bookings = bookings.filter(
            db.or_(
                Booking.booking_status.ilike(f"%{search}%"),
                Booking.user.has(
                    User.name.ilike(f"%{search}%")
                ),
                Booking.trek.has(
                    Trek.trek_name.ilike(f"%{search}%")
                )
            )
        )

    bookings = bookings.all()

    return render_template(
        "admin/bookings.html",
        bookings=bookings,
        search=search
    )
# 🥾 Trek Management System

A role-based Trek Management System developed using **Flask**, **SQLAlchemy**, **SQLite**, **Bootstrap 5**, and **Chart.js**. The application allows administrators to manage treks and staff, trekkers to book and manage treks, and trek staff to oversee assigned treks.

---

## Features

### Administrator
- Dashboard with statistics and charts
- Manage treks (Create, Update, Delete)
- Manage trek staff
- Approve or reject staff registrations
- View and manage users
- View all bookings
- Search users, treks, and bookings
- Data visualization using Chart.js

### Trekker
- Register and login
- Browse available treks
- Filter treks by difficulty
- Search treks by name or location
- Book available treks
- View active bookings
- Cancel bookings
- View completed and cancelled trekking history
- Manage personal profile
- Booking trend visualization

### Trek Staff
- View assigned treks
- Manage trek status
- View participant count per trek
- Dashboard with participant statistics
- Manage personal profile

---

## Technology Stack

| Category | Technology |
|----------|------------|
| Backend | Flask |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | Flask-Login |
| Frontend | HTML5, CSS3, Bootstrap 5 |
| Charts | Chart.js |
| Template Engine | Jinja2 |

---

## Project Structure

```text
Trekking-Management-Application/
│
├── application/
│   ├── __init__.py
│   ├── config.py
│   ├── controllers.py
│   ├── database.py
│   └── models.py
│
├── templates/
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── add_trek.html
│   │   ├── edit_trek.html
│   │   ├── view_treks.html
│   │   ├── view_staff.html
│   │   ├── view_users.html
│   │   ├── admin_bookings.html
│   │   ├── admin_search.html
│   │   └── ...
│   │
│   ├── staff/
│   │   ├── dashboard.html
│   │   ├── assigned_treks.html
│   │   ├── participants.html
│   │   ├── profile.html
│   │   └── ...
│   │
│   ├── user/
│   │   ├── dashboard.html
│   │   ├── available_treks.html
│   │   ├── booking_history.html
│   │   ├── profile.html
│   │   └── ...
│   │
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── staff_register.html
│   │
│   └── base_dashboard.html
│
├── static/
│   ├── css/
│   
├── db_directory/
│   └── trekking.sqlite3
│
├── main.py
├── initial_data.py
├── requirements.txt
├── README.md
├── Project_Report.pdf
└── .gitignore
```
---

## Database Schema

```text
                   +----------------------+
                   |        USER          |
                   +----------------------+
                   | PK user_id           |
                   | name                 |
                   | email                |
                   | password             |
                   | role                 |
                   | is_approved          |
                   | is_blacklisted       |
                   | is_active            |
                   +----------------------+
                      |             |
             1:1      |             |1:N
                      |             |
        +-------------+             +----------------+
        |                                        |
+---------------------+                 +----------------------+
|   STAFF_PROFILE     |                 |      BOOKING         |
+---------------------+                 +----------------------+
| PK staff_profile_id |                 | PK booking_id        |
| FK user_id          |                 | FK user_id           |
| contact_number      |                 | FK trek_id           |
| experience          |                 | booking_date         |
| status              |                 | booking_status       |
+---------------------+                 | payment_status       |
                                        +----------+-----------+
                                                   |
                                                   | N:1
                                                   |
                                          +----------------------+
                                          |        TREK          |
                                          +----------------------+
                                          | PK trek_id           |
                                          | trek_name            |
                                          | location             |
                                          | difficulty           |
                                          | duration             |
                                          | available_slots      |
                                          | FK assigned_staff_id |
                                          | status               |
                                          | start_date           |
                                          | end_date             |
                                          +----------------------+
```

---

## User Roles

### Admin

- Full access to the system
- Manage treks and staff
- View analytics
- Monitor bookings
- Search across the platform

### Trekker

- Book treks
- Manage bookings
- View trekking history
- Update profile

### Trek Staff

- Manage assigned treks
- Monitor participants
- Update trek status
- View participant statistics

---

## Dashboard Visualizations

### Admin Dashboard

- Treks by Status
- Booking Status Distribution
- Users by Role

### Trek Staff Dashboard

- Participants per Trek

### Trekker Dashboard

- Booking Trends
- Trekking History

---


# Installation & Setup

## 1. Clone the repository

```bash
git clone <repository-url>
cd trekking-management-application
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

## 3. Activate the virtual environment

### Windows (Command Prompt)

```bash
.venv\Scripts\activate
```

### Windows (Git Bash)

```bash
source .venv/Scripts/activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Initialize the database

Run the following command to create the SQLite database and automatically create the predefined Admin account.

```bash
python initial_data.py
```

## 6. Start the application

```bash
python main.py
```

The application will be available at:

```
http://127.0.0.1:8080
```

---

## Default Admin Credentials

| Email | Password |
|--------|----------|
| admin@trek.com | admin123 |

---

## Notes

- The database is created programmatically using SQLAlchemy.
- No manual database creation is required.
- The Admin account is automatically created when `initial_data.py` is executed.
- If starting with a fresh database, delete `db_directory/trekking.sqlite3` and rerun `initial_data.py`.

## Author

**Dua Saeed(23f1000825)**

Trek Management System using Flask, SQLAlchemy, Bootstrap, SQLite, and Chart.js.
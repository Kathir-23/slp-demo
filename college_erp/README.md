# Minimal College ERP System

A minimal, fully working College ERP System built with Python + Flask, Jinja2 templates, and plain JSON files as a database.

## Project Overview

This ERP system supports three user roles:

- **Admin** – Full access: manage students, staff, courses, reports, and announcements.
- **Staff** – Mark attendance, enter grades, view class roster, read announcements.
- **Student** – View own grades, attendance, enrolled courses, and announcements.

## Requirements

- Python 3.8 or higher

## Tech Stack

| Layer        | Technology              |
|--------------|-------------------------|
| Backend      | Python + Flask          |
| Templates    | Jinja2 (server-rendered)|
| Styling      | Plain CSS               |
| Database     | JSON files (`/data`)    |
| Auth         | Flask sessions          |
| Passwords    | werkzeug hash functions |

## Installation

```bash
pip install -r requirements.txt
```

## Seed Data

Populate all JSON files with test data:

```bash
python seed_data.py
```

This creates:
- 1 admin account
- 2 staff members (with login accounts)
- 5 students (with login accounts)
- 3 courses with enrollments
- Sample attendance and grade records
- 3 sample announcements

## Run the Application

```bash
python app.py
```

Open your browser and navigate to:

```
http://127.0.0.1:5000
```

## Default Login Credentials

> ⚠️ These are test credentials for development only. Change passwords before deploying to production.

| Role    | Username  | Password    |
|---------|-----------|-------------|
| Admin   | admin     | admin123    |
| Staff   | staff1    | staff123    |
| Student | student1  | student123  |

## Folder Structure

```
college_erp/
│
├── app.py                        # Main Flask application
├── requirements.txt              # Python dependencies
├── seed_data.py                  # Script to populate test data
├── README.md                     # This file
│
├── data/                         # JSON "database" files
│   ├── users.json
│   ├── students.json
│   ├── staff.json
│   ├── courses.json
│   ├── attendance.json
│   ├── grades.json
│   └── announcements.json
│
├── templates/                    # Jinja2 HTML templates
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── admin_students.html
│   ├── admin_student_form.html
│   ├── admin_staff.html
│   ├── admin_staff_form.html
│   ├── admin_courses.html
│   ├── admin_course_form.html
│   ├── admin_reports.html
│   ├── admin_announcements.html
│   ├── staff_dashboard.html
│   ├── staff_attendance.html
│   ├── staff_grades.html
│   ├── staff_roster.html
│   ├── staff_announcements.html
│   ├── student_dashboard.html
│   ├── student_grades.html
│   ├── student_attendance.html
│   ├── student_courses.html
│   └── student_announcements.html
│
└── static/
    └── style.css                 # Plain CSS stylesheet
```

## Features Summary

### Admin
- Dashboard with live statistics (students, staff, courses, today's attendance)
- Add / Edit / Delete students (auto-creates login account)
- Add / Edit / Delete staff (auto-creates login account)
- Add / Edit / Delete courses, assign staff, enrol students
- Attendance and grade reports with department/course filters
- Create and view college announcements

### Staff
- Dashboard showing assigned courses
- Mark attendance per course per date (present/absent checkboxes)
- Enter / update grades per course per exam type
- View class roster for assigned courses
- Read-only announcements

### Student
- Dashboard with profile and summary statistics
- View grades grouped by course
- View attendance summary with percentage bar per course
- View enrolled courses with instructor info
- Read-only announcements

## Security Notes

- Passwords are stored as hashed values using `werkzeug.security.generate_password_hash`.
- Role-based access control prevents cross-role access.
- Staff members can only access courses assigned to them.
- Students can only view their own data.

import os
import json
from datetime import date, datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "college_erp_secret_key_2024"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ─────────────────────────────────────────────
#  JSON helpers
# ─────────────────────────────────────────────

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ─────────────────────────────────────────────
#  Auth decorators
# ─────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if session.get("role") != role:
                flash("Unauthorized access.", "error")
                role_dashboards = {
                    "admin": "admin_dashboard",
                    "staff": "staff_dashboard",
                    "student": "student_dashboard",
                }
                return redirect(url_for(role_dashboards.get(session.get("role"), "login")))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ─────────────────────────────────────────────
#  Auth routes
# ─────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        role = session.get("role")
        if role == "admin":
            return redirect(url_for("admin_dashboard"))
        elif role == "staff":
            return redirect(url_for("staff_dashboard"))
        elif role == "student":
            return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        users = load_json("users.json")
        user = next((u for u in users if u["username"] == username), None)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["name"] = user["name"]
            session["linked_id"] = user.get("linked_id")
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user["role"] == "staff":
                return redirect(url_for("staff_dashboard"))
            elif user["role"] == "student":
                return redirect(url_for("student_dashboard"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ─────────────────────────────────────────────
#  ADMIN routes
# ─────────────────────────────────────────────

@app.route("/admin/dashboard")
@role_required("admin")
def admin_dashboard():
    students = load_json("students.json")
    staff = load_json("staff.json")
    courses = load_json("courses.json")
    attendance = load_json("attendance.json")
    today = date.today().isoformat()
    today_records = [r for r in attendance if r.get("date") == today]
    if today_records:
        present_count = sum(1 for r in today_records if r.get("status") == "present")
        attendance_pct = round((present_count / len(today_records)) * 100)
    else:
        attendance_pct = None
    return render_template(
        "admin_dashboard.html",
        total_students=len(students),
        total_staff=len(staff),
        total_courses=len(courses),
        attendance_pct=attendance_pct,
    )


# ── Students ──────────────────────────────────

@app.route("/admin/students")
@role_required("admin")
def admin_students():
    students = load_json("students.json")
    return render_template("admin_students.html", students=students)


@app.route("/admin/students/add", methods=["GET", "POST"])
@role_required("admin")
def admin_student_add():
    if request.method == "POST":
        roll_no = request.form.get("roll_no", "").strip()
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not all([roll_no, name, department, year, email, phone, username, password]):
            flash("All fields are required.", "error")
            return render_template("admin_student_form.html", student=None, action="Add")

        students = load_json("students.json")
        users = load_json("users.json")

        # check duplicate roll_no or username
        if any(s["roll_no"] == roll_no for s in students):
            flash("Roll number already exists.", "error")
            return render_template("admin_student_form.html", student=None, action="Add")
        if any(u["username"] == username for u in users):
            flash("Username already taken.", "error")
            return render_template("admin_student_form.html", student=None, action="Add")

        new_id = max((s["id"] for s in students), default=0) + 1
        student = {
            "id": new_id,
            "roll_no": roll_no,
            "name": name,
            "department": department,
            "year": int(year),
            "email": email,
            "phone": phone,
        }
        students.append(student)
        save_json("students.json", students)

        new_user_id = max((u["id"] for u in users), default=0) + 1
        user = {
            "id": new_user_id,
            "username": username,
            "password_hash": generate_password_hash(password),
            "role": "student",
            "name": name,
            "linked_id": new_id,
        }
        users.append(user)
        save_json("users.json", users)

        flash(f"Student '{name}' added successfully.", "success")
        return redirect(url_for("admin_students"))

    return render_template("admin_student_form.html", student=None, action="Add")


@app.route("/admin/students/edit/<int:student_id>", methods=["GET", "POST"])
@role_required("admin")
def admin_student_edit(student_id):
    students = load_json("students.json")
    users = load_json("users.json")
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("admin_students"))

    linked_user = next((u for u in users if u.get("linked_id") == student_id and u["role"] == "student"), None)

    if request.method == "POST":
        student["roll_no"] = request.form.get("roll_no", student["roll_no"]).strip()
        student["name"] = request.form.get("name", student["name"]).strip()
        student["department"] = request.form.get("department", student["department"]).strip()
        student["year"] = int(request.form.get("year", student["year"]))
        student["email"] = request.form.get("email", student["email"]).strip()
        student["phone"] = request.form.get("phone", student["phone"]).strip()

        new_password = request.form.get("password", "").strip()
        if linked_user:
            linked_user["name"] = student["name"]
            if new_password:
                linked_user["password_hash"] = generate_password_hash(new_password)

        save_json("students.json", students)
        save_json("users.json", users)
        flash(f"Student '{student['name']}' updated successfully.", "success")
        return redirect(url_for("admin_students"))

    return render_template("admin_student_form.html", student=student, action="Edit", linked_user=linked_user)


@app.route("/admin/students/delete/<int:student_id>", methods=["POST"])
@role_required("admin")
def admin_student_delete(student_id):
    students = load_json("students.json")
    users = load_json("users.json")
    courses = load_json("courses.json")

    students = [s for s in students if s["id"] != student_id]
    users = [u for u in users if not (u.get("linked_id") == student_id and u["role"] == "student")]

    for course in courses:
        if student_id in course.get("student_ids", []):
            course["student_ids"].remove(student_id)

    save_json("students.json", students)
    save_json("users.json", users)
    save_json("courses.json", courses)
    flash("Student deleted successfully.", "success")
    return redirect(url_for("admin_students"))


# ── Staff ─────────────────────────────────────

@app.route("/admin/staff")
@role_required("admin")
def admin_staff():
    staff_list = load_json("staff.json")
    return render_template("admin_staff.html", staff_list=staff_list)


@app.route("/admin/staff/add", methods=["GET", "POST"])
@role_required("admin")
def admin_staff_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not all([name, department, email, username, password]):
            flash("All fields are required.", "error")
            return render_template("admin_staff_form.html", staff=None, action="Add")

        staff_list = load_json("staff.json")
        users = load_json("users.json")

        if any(u["username"] == username for u in users):
            flash("Username already taken.", "error")
            return render_template("admin_staff_form.html", staff=None, action="Add")

        new_id = max((s["id"] for s in staff_list), default=0) + 1
        staff_member = {
            "id": new_id,
            "name": name,
            "department": department,
            "email": email,
            "subjects": [],
        }
        staff_list.append(staff_member)
        save_json("staff.json", staff_list)

        new_user_id = max((u["id"] for u in users), default=0) + 1
        user = {
            "id": new_user_id,
            "username": username,
            "password_hash": generate_password_hash(password),
            "role": "staff",
            "name": name,
            "linked_id": new_id,
        }
        users.append(user)
        save_json("users.json", users)

        flash(f"Staff member '{name}' added successfully.", "success")
        return redirect(url_for("admin_staff"))

    return render_template("admin_staff_form.html", staff=None, action="Add")


@app.route("/admin/staff/edit/<int:staff_id>", methods=["GET", "POST"])
@role_required("admin")
def admin_staff_edit(staff_id):
    staff_list = load_json("staff.json")
    users = load_json("users.json")
    staff = next((s for s in staff_list if s["id"] == staff_id), None)
    if not staff:
        flash("Staff member not found.", "error")
        return redirect(url_for("admin_staff"))

    linked_user = next((u for u in users if u.get("linked_id") == staff_id and u["role"] == "staff"), None)

    if request.method == "POST":
        staff["name"] = request.form.get("name", staff["name"]).strip()
        staff["department"] = request.form.get("department", staff["department"]).strip()
        staff["email"] = request.form.get("email", staff["email"]).strip()

        new_password = request.form.get("password", "").strip()
        if linked_user:
            linked_user["name"] = staff["name"]
            if new_password:
                linked_user["password_hash"] = generate_password_hash(new_password)

        save_json("staff.json", staff_list)
        save_json("users.json", users)
        flash(f"Staff member '{staff['name']}' updated successfully.", "success")
        return redirect(url_for("admin_staff"))

    return render_template("admin_staff_form.html", staff=staff, action="Edit", linked_user=linked_user)


@app.route("/admin/staff/delete/<int:staff_id>", methods=["POST"])
@role_required("admin")
def admin_staff_delete(staff_id):
    staff_list = load_json("staff.json")
    users = load_json("users.json")
    courses = load_json("courses.json")

    staff_list = [s for s in staff_list if s["id"] != staff_id]
    users = [u for u in users if not (u.get("linked_id") == staff_id and u["role"] == "staff")]

    for course in courses:
        if course.get("staff_id") == staff_id:
            course["staff_id"] = None

    save_json("staff.json", staff_list)
    save_json("users.json", users)
    save_json("courses.json", courses)
    flash("Staff member deleted successfully.", "success")
    return redirect(url_for("admin_staff"))


# ── Courses ───────────────────────────────────

@app.route("/admin/courses")
@role_required("admin")
def admin_courses():
    courses = load_json("courses.json")
    staff_list = load_json("staff.json")
    staff_map = {s["id"]: s["name"] for s in staff_list}
    return render_template("admin_courses.html", courses=courses, staff_map=staff_map)


@app.route("/admin/courses/add", methods=["GET", "POST"])
@role_required("admin")
def admin_course_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip()
        department = request.form.get("department", "").strip()

        if not all([name, code, department]):
            flash("All fields are required.", "error")
            return render_template("admin_course_form.html", course=None, action="Add",
                                   staff_list=[], students=[])

        courses = load_json("courses.json")
        if any(c["code"] == code for c in courses):
            flash("Course code already exists.", "error")
            return render_template("admin_course_form.html", course=None, action="Add",
                                   staff_list=load_json("staff.json"), students=load_json("students.json"))

        new_id = max((c["id"] for c in courses), default=0) + 1
        course = {
            "id": new_id,
            "name": name,
            "code": code,
            "department": department,
            "staff_id": None,
            "student_ids": [],
        }
        courses.append(course)
        save_json("courses.json", courses)
        flash(f"Course '{name}' added successfully.", "success")
        return redirect(url_for("admin_courses"))

    staff_list = load_json("staff.json")
    students = load_json("students.json")
    return render_template("admin_course_form.html", course=None, action="Add",
                           staff_list=staff_list, students=students)


@app.route("/admin/courses/edit/<int:course_id>", methods=["GET", "POST"])
@role_required("admin")
def admin_course_edit(course_id):
    courses = load_json("courses.json")
    staff_list = load_json("staff.json")
    students = load_json("students.json")
    course = next((c for c in courses if c["id"] == course_id), None)
    if not course:
        flash("Course not found.", "error")
        return redirect(url_for("admin_courses"))

    if request.method == "POST":
        course["name"] = request.form.get("name", course["name"]).strip()
        course["code"] = request.form.get("code", course["code"]).strip()
        course["department"] = request.form.get("department", course["department"]).strip()

        staff_id_str = request.form.get("staff_id", "")
        course["staff_id"] = int(staff_id_str) if staff_id_str else None

        selected_ids = request.form.getlist("student_ids")
        course["student_ids"] = [int(i) for i in selected_ids]

        save_json("courses.json", courses)
        flash(f"Course '{course['name']}' updated successfully.", "success")
        return redirect(url_for("admin_courses"))

    return render_template("admin_course_form.html", course=course, action="Edit",
                           staff_list=staff_list, students=students)


@app.route("/admin/courses/delete/<int:course_id>", methods=["POST"])
@role_required("admin")
def admin_course_delete(course_id):
    courses = load_json("courses.json")
    courses = [c for c in courses if c["id"] != course_id]
    save_json("courses.json", courses)
    flash("Course deleted successfully.", "success")
    return redirect(url_for("admin_courses"))


# ── Reports ───────────────────────────────────

@app.route("/admin/reports")
@role_required("admin")
def admin_reports():
    students = load_json("students.json")
    courses = load_json("courses.json")
    attendance = load_json("attendance.json")
    grades = load_json("grades.json")

    dept_filter = request.args.get("department", "")
    course_filter = request.args.get("course_id", "")

    student_map = {s["id"]: s for s in students}
    course_map = {c["id"]: c for c in courses}

    departments = sorted(set(s["department"] for s in students))

    # Filter courses
    filtered_courses = courses
    if dept_filter:
        filtered_courses = [c for c in courses if c["department"] == dept_filter]
    course_ids = set(c["id"] for c in filtered_courses)
    if course_filter:
        try:
            course_ids = {int(course_filter)}
        except ValueError:
            pass

    # Attendance report
    att_report = []
    for r in attendance:
        if r["course_id"] not in course_ids:
            continue
        s = student_map.get(r["student_id"])
        c = course_map.get(r["course_id"])
        if s and c:
            if dept_filter and s["department"] != dept_filter:
                continue
            att_report.append({
                "student": s["name"],
                "roll_no": s["roll_no"],
                "department": s["department"],
                "course": c["name"],
                "date": r["date"],
                "status": r["status"],
            })

    # Grade report
    grade_report = []
    for g in grades:
        if g["course_id"] not in course_ids:
            continue
        s = student_map.get(g["student_id"])
        c = course_map.get(g["course_id"])
        if s and c:
            if dept_filter and s["department"] != dept_filter:
                continue
            pct = round((g["score"] / g["max_score"]) * 100) if g["max_score"] else 0
            grade_report.append({
                "student": s["name"],
                "roll_no": s["roll_no"],
                "course": c["name"],
                "exam": g["exam"],
                "score": g["score"],
                "max_score": g["max_score"],
                "percentage": pct,
            })

    return render_template(
        "admin_reports.html",
        att_report=att_report,
        grade_report=grade_report,
        departments=departments,
        courses=filtered_courses,
        all_courses=courses,
        dept_filter=dept_filter,
        course_filter=course_filter,
    )


# ── Announcements ─────────────────────────────

@app.route("/admin/announcements", methods=["GET", "POST"])
@role_required("admin")
def admin_announcements():
    announcements = load_json("announcements.json")

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        message = request.form.get("message", "").strip()
        if not title or not message:
            flash("Title and message are required.", "error")
        else:
            new_id = max((a["id"] for a in announcements), default=0) + 1
            announcements.append({
                "id": new_id,
                "title": title,
                "message": message,
                "date": date.today().isoformat(),
                "posted_by": session.get("name", "Administrator"),
            })
            save_json("announcements.json", announcements)
            flash("Announcement posted successfully.", "success")
            return redirect(url_for("admin_announcements"))

    announcements_sorted = sorted(announcements, key=lambda x: x.get("date", ""), reverse=True)
    return render_template("admin_announcements.html", announcements=announcements_sorted)


# ─────────────────────────────────────────────
#  STAFF routes
# ─────────────────────────────────────────────

def get_staff_courses(staff_id):
    courses = load_json("courses.json")
    return [c for c in courses if c.get("staff_id") == staff_id]


def verify_staff_course(staff_id, course_id):
    """Return course if it belongs to this staff, else None."""
    courses = load_json("courses.json")
    return next((c for c in courses if c["id"] == course_id and c.get("staff_id") == staff_id), None)


@app.route("/staff/dashboard")
@role_required("staff")
def staff_dashboard():
    staff_id = session.get("linked_id")
    staff_list = load_json("staff.json")
    staff = next((s for s in staff_list if s["id"] == staff_id), None)
    my_courses = get_staff_courses(staff_id)
    return render_template("staff_dashboard.html", staff=staff, courses=my_courses)


@app.route("/staff/attendance/<int:course_id>", methods=["GET", "POST"])
@role_required("staff")
def staff_attendance(course_id):
    staff_id = session.get("linked_id")
    course = verify_staff_course(staff_id, course_id)
    if not course:
        flash("Unauthorized: you do not teach this course.", "error")
        return redirect(url_for("staff_dashboard"))

    students = load_json("students.json")
    enrolled = [s for s in students if s["id"] in course.get("student_ids", [])]
    attendance = load_json("attendance.json")

    selected_date = request.args.get("date", date.today().isoformat())

    if request.method == "POST":
        selected_date = request.form.get("date", date.today().isoformat())
        present_ids = set(int(x) for x in request.form.getlist("present_ids"))

        # Remove existing records for this course+date
        attendance = [
            r for r in attendance
            if not (r["course_id"] == course_id and r["date"] == selected_date)
        ]

        for s in enrolled:
            attendance.append({
                "student_id": s["id"],
                "course_id": course_id,
                "date": selected_date,
                "status": "present" if s["id"] in present_ids else "absent",
            })

        save_json("attendance.json", attendance)
        flash("Attendance saved successfully.", "success")
        return redirect(url_for("staff_attendance", course_id=course_id, date=selected_date))

    # Load existing records for the selected date
    existing = {
        r["student_id"]: r["status"]
        for r in attendance
        if r["course_id"] == course_id and r["date"] == selected_date
    }

    return render_template(
        "staff_attendance.html",
        course=course,
        enrolled=enrolled,
        selected_date=selected_date,
        existing=existing,
    )


@app.route("/staff/grades/<int:course_id>", methods=["GET", "POST"])
@role_required("staff")
def staff_grades(course_id):
    staff_id = session.get("linked_id")
    course = verify_staff_course(staff_id, course_id)
    if not course:
        flash("Unauthorized: you do not teach this course.", "error")
        return redirect(url_for("staff_dashboard"))

    students = load_json("students.json")
    enrolled = [s for s in students if s["id"] in course.get("student_ids", [])]
    grades = load_json("grades.json")

    exam_choices = ["Internal 1", "Internal 2", "Model Exam", "Semester"]
    selected_exam = request.args.get("exam", exam_choices[0])

    if request.method == "POST":
        selected_exam = request.form.get("exam", exam_choices[0])
        max_score = int(request.form.get("max_score", 100))

        for s in enrolled:
            score_str = request.form.get(f"score_{s['id']}", "").strip()
            if score_str == "":
                continue
            try:
                score = int(score_str)
            except ValueError:
                continue

            # Update or insert
            existing = next(
                (g for g in grades
                 if g["student_id"] == s["id"]
                 and g["course_id"] == course_id
                 and g["exam"] == selected_exam),
                None,
            )
            if existing:
                existing["score"] = score
                existing["max_score"] = max_score
            else:
                grades.append({
                    "student_id": s["id"],
                    "course_id": course_id,
                    "exam": selected_exam,
                    "score": score,
                    "max_score": max_score,
                })

        save_json("grades.json", grades)
        flash("Grades saved successfully.", "success")
        return redirect(url_for("staff_grades", course_id=course_id, exam=selected_exam))

    # Pre-load existing grades for selected exam
    existing_grades = {
        g["student_id"]: g
        for g in grades
        if g["course_id"] == course_id and g["exam"] == selected_exam
    }

    return render_template(
        "staff_grades.html",
        course=course,
        enrolled=enrolled,
        exam_choices=exam_choices,
        selected_exam=selected_exam,
        existing_grades=existing_grades,
    )


@app.route("/staff/roster/<int:course_id>")
@role_required("staff")
def staff_roster(course_id):
    staff_id = session.get("linked_id")
    course = verify_staff_course(staff_id, course_id)
    if not course:
        flash("Unauthorized: you do not teach this course.", "error")
        return redirect(url_for("staff_dashboard"))

    students = load_json("students.json")
    enrolled = [s for s in students if s["id"] in course.get("student_ids", [])]
    return render_template("staff_roster.html", course=course, enrolled=enrolled)


@app.route("/staff/announcements")
@role_required("staff")
def staff_announcements():
    announcements = load_json("announcements.json")
    announcements_sorted = sorted(announcements, key=lambda x: x.get("date", ""), reverse=True)
    return render_template("staff_announcements.html", announcements=announcements_sorted)


# ─────────────────────────────────────────────
#  STUDENT routes
# ─────────────────────────────────────────────

@app.route("/student/dashboard")
@role_required("student")
def student_dashboard():
    student_id = session.get("linked_id")
    students = load_json("students.json")
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        flash("Student record not found.", "error")
        return redirect(url_for("logout"))

    courses = load_json("courses.json")
    my_courses = [c for c in courses if student_id in c.get("student_ids", [])]

    attendance = load_json("attendance.json")
    my_att = [r for r in attendance if r["student_id"] == student_id]
    if my_att:
        present = sum(1 for r in my_att if r["status"] == "present")
        att_pct = round((present / len(my_att)) * 100)
    else:
        att_pct = None

    return render_template(
        "student_dashboard.html",
        student=student,
        num_courses=len(my_courses),
        att_pct=att_pct,
    )


@app.route("/student/grades")
@role_required("student")
def student_grades():
    student_id = session.get("linked_id")
    courses = load_json("courses.json")
    grades = load_json("grades.json")

    my_courses = [c for c in courses if student_id in c.get("student_ids", [])]
    my_grades = [g for g in grades if g["student_id"] == student_id]

    grade_by_course = {}
    for course in my_courses:
        cg = [g for g in my_grades if g["course_id"] == course["id"]]
        grade_by_course[course["id"]] = {
            "course": course,
            "grades": cg,
        }

    return render_template("student_grades.html", grade_by_course=grade_by_course)


@app.route("/student/attendance")
@role_required("student")
def student_attendance():
    student_id = session.get("linked_id")
    courses = load_json("courses.json")
    attendance = load_json("attendance.json")

    my_courses = [c for c in courses if student_id in c.get("student_ids", [])]
    my_att = [r for r in attendance if r["student_id"] == student_id]

    att_by_course = {}
    for course in my_courses:
        ca = [r for r in my_att if r["course_id"] == course["id"]]
        present = sum(1 for r in ca if r["status"] == "present")
        absent = sum(1 for r in ca if r["status"] == "absent")
        total = present + absent
        pct = round((present / total) * 100) if total > 0 else None
        att_by_course[course["id"]] = {
            "course": course,
            "present": present,
            "absent": absent,
            "percentage": pct,
        }

    return render_template("student_attendance.html", att_by_course=att_by_course)


@app.route("/student/courses")
@role_required("student")
def student_courses():
    student_id = session.get("linked_id")
    courses = load_json("courses.json")
    staff_list = load_json("staff.json")
    staff_map = {s["id"]: s["name"] for s in staff_list}

    my_courses = [c for c in courses if student_id in c.get("student_ids", [])]
    return render_template("student_courses.html", courses=my_courses, staff_map=staff_map)


@app.route("/student/announcements")
@role_required("student")
def student_announcements():
    announcements = load_json("announcements.json")
    announcements_sorted = sorted(announcements, key=lambda x: x.get("date", ""), reverse=True)
    return render_template("student_announcements.html", announcements=announcements_sorted)


# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)

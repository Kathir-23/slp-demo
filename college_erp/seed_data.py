"""
Seed script – populates all JSON data files with realistic test data.
Run once before starting the app:
    python seed_data.py
"""

import os
import json
from werkzeug.security import generate_password_hash

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def save(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"  [OK] {filename}")


# ─── Users ────────────────────────────────────────────────────────────────────
users = [
    {
        "id": 1,
        "username": "admin",
        "password_hash": generate_password_hash("admin123"),
        "role": "admin",
        "name": "Administrator",
        "linked_id": None,
    },
    {
        "id": 2,
        "username": "staff1",
        "password_hash": generate_password_hash("staff123"),
        "role": "staff",
        "name": "Dr. Robert Smith",
        "linked_id": 1,
    },
    {
        "id": 3,
        "username": "staff2",
        "password_hash": generate_password_hash("staff456"),
        "role": "staff",
        "name": "Prof. Ananya Iyer",
        "linked_id": 2,
    },
    {
        "id": 4,
        "username": "student1",
        "password_hash": generate_password_hash("student123"),
        "role": "student",
        "name": "John Doe",
        "linked_id": 1,
    },
    {
        "id": 5,
        "username": "student2",
        "password_hash": generate_password_hash("stu2pass"),
        "role": "student",
        "name": "Jane Smith",
        "linked_id": 2,
    },
    {
        "id": 6,
        "username": "student3",
        "password_hash": generate_password_hash("stu3pass"),
        "role": "student",
        "name": "Arun Kumar",
        "linked_id": 3,
    },
    {
        "id": 7,
        "username": "student4",
        "password_hash": generate_password_hash("stu4pass"),
        "role": "student",
        "name": "Priya Nair",
        "linked_id": 4,
    },
    {
        "id": 8,
        "username": "student5",
        "password_hash": generate_password_hash("stu5pass"),
        "role": "student",
        "name": "Mohammed Ali",
        "linked_id": 5,
    },
]
save("users.json", users)

# ─── Staff ────────────────────────────────────────────────────────────────────
staff = [
    {
        "id": 1,
        "name": "Dr. Robert Smith",
        "department": "Computer Science",
        "email": "robert.smith@college.edu",
        "subjects": ["Data Structures", "Algorithms"],
    },
    {
        "id": 2,
        "name": "Prof. Ananya Iyer",
        "department": "Computer Science",
        "email": "ananya.iyer@college.edu",
        "subjects": ["Database Systems", "Web Technologies"],
    },
]
save("staff.json", staff)

# ─── Students ─────────────────────────────────────────────────────────────────
students = [
    {
        "id": 1,
        "roll_no": "CS001",
        "name": "John Doe",
        "department": "Computer Science",
        "year": 2,
        "email": "john.doe@student.edu",
        "phone": "9876543210",
    },
    {
        "id": 2,
        "roll_no": "CS002",
        "name": "Jane Smith",
        "department": "Computer Science",
        "year": 2,
        "email": "jane.smith@student.edu",
        "phone": "9876543211",
    },
    {
        "id": 3,
        "roll_no": "CS003",
        "name": "Arun Kumar",
        "department": "Computer Science",
        "year": 3,
        "email": "arun.kumar@student.edu",
        "phone": "9876543212",
    },
    {
        "id": 4,
        "roll_no": "CS004",
        "name": "Priya Nair",
        "department": "Computer Science",
        "year": 3,
        "email": "priya.nair@student.edu",
        "phone": "9876543213",
    },
    {
        "id": 5,
        "roll_no": "CS005",
        "name": "Mohammed Ali",
        "department": "Computer Science",
        "year": 2,
        "email": "mohammed.ali@student.edu",
        "phone": "9876543214",
    },
]
save("students.json", students)

# ─── Courses ──────────────────────────────────────────────────────────────────
courses = [
    {
        "id": 1,
        "name": "Data Structures",
        "code": "CS201",
        "department": "Computer Science",
        "staff_id": 1,
        "student_ids": [1, 2, 3, 4, 5],
    },
    {
        "id": 2,
        "name": "Database Systems",
        "code": "CS202",
        "department": "Computer Science",
        "staff_id": 2,
        "student_ids": [1, 2, 3],
    },
    {
        "id": 3,
        "name": "Web Technologies",
        "code": "CS203",
        "department": "Computer Science",
        "staff_id": 2,
        "student_ids": [3, 4, 5],
    },
]
save("courses.json", courses)

# ─── Attendance ───────────────────────────────────────────────────────────────
attendance = []

# CS201 – last 5 days attendance for all enrolled students
from datetime import date, timedelta

base = date(2026, 9, 23)
att_data = {
    # course_id: {student_id: [P/A for day 0..4]}
    1: {
        1: ["present", "present", "present", "absent",  "present"],
        2: ["present", "absent",  "present", "present", "present"],
        3: ["absent",  "present", "present", "present", "present"],
        4: ["present", "present", "absent",  "present", "present"],
        5: ["present", "present", "present", "present", "absent"],
    },
    2: {
        1: ["present", "present", "absent",  "present", "present"],
        2: ["present", "present", "present", "present", "absent"],
        3: ["absent",  "present", "present", "absent",  "present"],
    },
    3: {
        3: ["present", "present", "present", "present", "present"],
        4: ["present", "absent",  "present", "present", "present"],
        5: ["absent",  "present", "present", "present", "present"],
    },
}

for course_id, student_map in att_data.items():
    for day_offset in range(5):
        rec_date = (base + timedelta(days=day_offset)).isoformat()
        for student_id, statuses in student_map.items():
            attendance.append({
                "student_id": student_id,
                "course_id": course_id,
                "date": rec_date,
                "status": statuses[day_offset],
            })

save("attendance.json", attendance)

# ─── Grades ───────────────────────────────────────────────────────────────────
grades = [
    # CS201
    {"student_id": 1, "course_id": 1, "exam": "Internal 1", "score": 85, "max_score": 100},
    {"student_id": 1, "course_id": 1, "exam": "Internal 2", "score": 90, "max_score": 100},
    {"student_id": 2, "course_id": 1, "exam": "Internal 1", "score": 78, "max_score": 100},
    {"student_id": 2, "course_id": 1, "exam": "Internal 2", "score": 82, "max_score": 100},
    {"student_id": 3, "course_id": 1, "exam": "Internal 1", "score": 91, "max_score": 100},
    {"student_id": 3, "course_id": 1, "exam": "Internal 2", "score": 88, "max_score": 100},
    {"student_id": 4, "course_id": 1, "exam": "Internal 1", "score": 74, "max_score": 100},
    {"student_id": 4, "course_id": 1, "exam": "Internal 2", "score": 79, "max_score": 100},
    {"student_id": 5, "course_id": 1, "exam": "Internal 1", "score": 88, "max_score": 100},
    {"student_id": 5, "course_id": 1, "exam": "Internal 2", "score": 92, "max_score": 100},
    # CS202
    {"student_id": 1, "course_id": 2, "exam": "Internal 1", "score": 80, "max_score": 100},
    {"student_id": 2, "course_id": 2, "exam": "Internal 1", "score": 75, "max_score": 100},
    {"student_id": 3, "course_id": 2, "exam": "Internal 1", "score": 93, "max_score": 100},
    # CS203
    {"student_id": 3, "course_id": 3, "exam": "Internal 1", "score": 87, "max_score": 100},
    {"student_id": 4, "course_id": 3, "exam": "Internal 1", "score": 70, "max_score": 100},
    {"student_id": 5, "course_id": 3, "exam": "Internal 1", "score": 95, "max_score": 100},
]
save("grades.json", grades)

# ─── Announcements ────────────────────────────────────────────────────────────
announcements = [
    {
        "id": 1,
        "title": "Semester Examination Schedule",
        "message": "The semester examinations will begin from October 15, 2026. Kindly check the hall tickets issued by the exam cell.",
        "date": "2026-09-20",
        "posted_by": "Administrator",
    },
    {
        "id": 2,
        "title": "College Holiday – Gandhi Jayanti",
        "message": "The college will remain closed on October 2, 2026 on account of Gandhi Jayanti. Regular classes resume on October 3.",
        "date": "2026-09-22",
        "posted_by": "Administrator",
    },
    {
        "id": 3,
        "title": "Internal Assessment Marks Submission",
        "message": "All staff members are requested to submit Internal Assessment marks by September 30, 2026. Use the Staff portal to enter grades.",
        "date": "2026-09-25",
        "posted_by": "Administrator",
    },
]
save("announcements.json", announcements)

print("\nSeed data populated successfully!")
print("\nDefault Login Credentials:")
print("  Admin   -> username: admin    / password: admin123")
print("  Staff   -> username: staff1   / password: staff123")
print("  Student -> username: student1 / password: student123")

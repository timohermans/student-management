from datetime import datetime, timezone
from flask import abort, redirect, render_template, request, url_for
import json

from student import canvas_api
from student.database import db_session
from student.models import Student, Semester
from student.cache import cache
from student.canvas_api import User as CanvasUser


def user_get_general_overview():
    students = db_session.query(Student).all()
    semesters = db_session.query(Semester).all()
    return render_template("index.html", students=students, semesters=semesters)


def students_search():
    query = request.args.get("query") or ""
    result = db_session.query(Student).where(Student.name.like(f"%{query}%")).all()
    return render_template("students/search.html", students=result)


def student_show_overview(id: int):
    student = db_session.query(Student).where(Student.id.is_(id)).one()
    return render_template("student/index.html", student=student)


@cache.cached(timeout=86400)  # a day
def canvas_show_available_courses():
    courses = canvas_api.get_available_courses()
    courses.sort(
        key=lambda c: c.term.endAt
        if c.term.endAt is not None
        else datetime(1990, 1, 1, tzinfo=timezone.utc),
        reverse=True,
    )
    return render_template("canvas/courses.html", courses=courses)


@cache.cached(timeout=86400)  # a day
def canvas_course_details(id: str):
    course = canvas_api.get_course_details(id)

    if course is None:
        abort(404)

    sections = course.sections

    for section in sections:
        section.students = []
        for enrollment in course.enrollments:
            if section._id == enrollment.section._id:
                section.students.append(enrollment.user)
        section.student_json = json.dumps([s.__dict__ for s in section.students])

    course.sections = sections

    return render_template("canvas/course.html", course=course)


def canvas_students_import(id):
    form = request.form
    course_id = id
    course_name = form.get("course_name")
    term_name = form.get("course_term_name")
    term_start_at = form.get("course_term_start_at")
    term_end_at = form.get("course_term_end_at")
    section_id = form.get("section_id")
    section_name = form.get("section_name")
    students_json = form.get("students")
    students = [CanvasUser(**s) for s in json.loads(students_json)]

    canvas_id = int(course_id + section_id)

    semester = (
        db_session.query(Semester)
        .join(Semester.students)
        .where(Semester.canvas_id.is_(canvas_id))
        .first()
    )

    if semester is None:
        semester = Semester(
            name=course_name,
            section=section_name,
            term=term_name,
            start_at=datetime.fromisoformat(term_start_at),
            end_at=datetime.fromisoformat(term_end_at),
            canvas_id=canvas_id,
        )
        db_session.add(semester)

    student_ids = [s._id for s in students]
    existing_students = (
        db_session.query(Student).where(Student.canvas_id.in_(student_ids)).all()
    )

    for student in students:
        existing_student = next(
            (s for s in existing_students if s.canvas_id == int(student._id)), None
        )

        if existing_student is not None:
            semester.students.append(existing_student)
        else:
            new_student = Student(
                name=student.name, canvas_id=student._id, avatar_url=student.avatarUrl
            )
            db_session.add(new_student)
            semester.students.append(new_student)

    db_session.commit()

    return redirect(url_for("user_get_general_overview"))

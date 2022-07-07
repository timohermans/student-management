from datetime import datetime, timezone
import os
from typing import List, Tuple
from flask import (
    abort,
    current_app as app,
)
from werkzeug.utils import secure_filename
import json
import urllib

from . import canvas_api
from .database import db_session
from .models import Note, Student, Semester
from .canvas_api import User as CanvasUser


def user_get_general_overview() -> Tuple[List[Student], List[Semester]]:
    students = db_session.query(Student).all()
    semesters = db_session.query(Semester).all()
    return students, semesters


def students_search(query: str):
    return db_session.query(Student).where(Student.name.like(f"%{query}%")).all()


def student_show_overview(id: int):
    return db_session.query(Student).where(Student.id == id).one()


def student_add_note(id: int, text: str, file):
    student = db_session.query(Student).where(Student.id == id).one()
    file_name = None

    if file is not None:
        file_name = secure_filename(file.filename)
        student_dir = secure_filename(f"{student.id}_{student.name}")
        dir = os.path.join(app.config['MEDIA_FOLDER'], student_dir)
        if not os.path.exists(dir):
            os.makedirs(dir)
        file_path = os.path.join(dir, file_name)
        file.save(file_path)

    note = Note(text=text, attachment=f'{student_dir}/{file_name}')
    student.notes.append(note)

    db_session.commit()


def semester_show_overview(id: int):
    return db_session.query(Semester).where(Semester.id == id).one()


def canvas_show_available_courses():
    courses = canvas_api.get_available_courses()
    courses.sort(
        key=lambda c: c.term.endAt
        if c.term.endAt is not None
        else datetime(1990, 1, 1, tzinfo=timezone.utc),
        reverse=True,
    )
    return courses


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
    return course


def canvas_students_import(id, form):
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

    semester = db_session.query(Semester).where(Semester.canvas_id == canvas_id).first()

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

        student_new = None

        if existing_student is not None:
            student_new = existing_student
            semester.students.append(student_new)
        else:
            file_name = f"{student.name}.jpg" if student.avatarUrl is not None else None
            student_new = Student(
                name=student.name, canvas_id=student._id, avatar_url=file_name
            )
            db_session.add(student_new)
            semester.students.append(student_new)

        download_image_of(student_new, student.avatarUrl)
    db_session.commit()


def download_image_of(student: Student, avatar_url: str) -> str:
    if student.avatar_url is None or avatar_url is None:
        return

    dir = app.config["MEDIA_FOLDER"]
    if not os.path.exists(dir):
        os.makedirs(dir)
    file_name = os.path.join(dir, student.avatar_url)

    if os.path.exists(file_name):
        return

    urllib.request.urlretrieve(avatar_url, file_name)

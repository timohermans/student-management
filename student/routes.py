from flask import (
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
    current_app as app,
)

from . import usecases
from .cache import cache


def user_get_general_overview():
    students, semesters = usecases.user_get_general_overview()
    return render_template("index.html", students=students, semesters=semesters)


def students_search():
    query = request.args.get("query") or ""
    students = usecases.students_search(query)
    return render_template("students/search.html", students=students)


def student_show_overview(id: int):
    student = usecases.student_show_overview(id)
    return render_template("student/index.html", student=student)

def semester_show_overview(id: int):
    semester = usecases.semester_show_overview(id)
    return render_template("semester/index.html", semester=semester)


def student_add_note(id: int):
    file_key = 'attachment'
    file = None
    if file_key in request.files and request.files[file_key].filename != '':
        file = request.files[file_key]
    # TODO: when calling from an API, this is NOT safe. We should escape it then
    text = request.form.get('text')
    usecases.student_add_note(id, text, file)
    return redirect(url_for('student_show_overview', id=id))


@cache.cached(timeout=86400)  # a day
def canvas_show_available_courses():
    courses = usecases.canvas_show_available_courses()
    return render_template("canvas/courses.html", courses=courses)


@cache.cached(timeout=86400)  # a day
def canvas_course_details(id: str):
    course = usecases.canvas_course_details(id)
    return render_template("canvas/course.html", course=course)


def canvas_students_import(id):
    # TODO: don't pass form
    usecases.canvas_students_import(id, request.form)
    return redirect(url_for("user_get_general_overview"))


def get_media_file(filename: str):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename, as_attachment=True)

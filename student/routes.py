from flask import (
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
    current_app as app,
)

from student import cache, usecases


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


@cache.cached(timeout=86400)  # a day
def canvas_show_available_courses():
    courses = usecases.canvas_show_available_courses()
    return render_template("canvas/courses.html", courses=courses)


@cache.cached(timeout=86400)  # a day
def canvas_course_details(id: str):
    course = usecases.canvas_course_details(id)
    return render_template("canvas/course.html", course=course)


def canvas_students_import(id):
    usecases.canvas_students_import(id, request.form)
    return redirect(url_for("user_get_general_overview"))


def get_media_file(filename: str):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename, as_attachment=True)

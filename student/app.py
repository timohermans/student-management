from flask import Flask

from student import usecases, errors
from .cache import cache
from .database import db_session


app = Flask(__name__)
cache.init_app(app)
app.register_blueprint(errors.blueprint)

app.add_url_rule("/", methods=["GET"], view_func=usecases.user_get_general_overview)
app.add_url_rule("/search", view_func=usecases.students_search)
app.add_url_rule("/student/<int:id>", view_func=usecases.student_show_overview)
app.add_url_rule("/canvas", view_func=usecases.canvas_show_available_courses)
app.add_url_rule("/canvas/course/<string:id>", view_func=usecases.canvas_course_details)
app.add_url_rule("/canvas/course/<string:id>", methods=["POST"], view_func=usecases.canvas_students_import)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

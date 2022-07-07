import os
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from student import routes, errors
from .cache import cache
from .database import db_session


app = Flask(__name__)
app.config.from_mapping(
    MEDIA_FOLDER=os.path.join(app.instance_path, "media"),
    DATABASE=os.environ.get("DATABASE"),
    CANVAS_API_TOKEN=os.environ.get("CANVAS_API_TOKEN"),
    SECRET_KEY= os.environ.get("SECRET_KEY")
)
toolbar = DebugToolbarExtension(app)
cache.init_app(app)
app.register_blueprint(errors.blueprint)

app.add_url_rule("/", methods=["GET"], view_func=routes.user_get_general_overview)
app.add_url_rule("/search", view_func=routes.students_search)
app.add_url_rule("/student/<int:id>", view_func=routes.student_show_overview)
app.add_url_rule("/student/<int:id>", methods=["POST"], view_func=routes.student_add_note)
app.add_url_rule("/semester/<int:id>", view_func=routes.semester_show_overview)
app.add_url_rule("/canvas", view_func=routes.canvas_show_available_courses)
app.add_url_rule("/canvas/course/<string:id>", view_func=routes.canvas_course_details)
app.add_url_rule(
    "/canvas/course/<string:id>",
    methods=["POST"],
    view_func=routes.canvas_students_import,
)
app.add_url_rule("/media/<path:filename>", view_func=routes.get_media_file)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

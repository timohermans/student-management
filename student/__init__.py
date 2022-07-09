import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from . import errors, filters, routes
from .cache import cache
from .database import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        MEDIA_FOLDER=os.path.join(app.instance_path, "media"),
        CANVAS_API_URL=os.environ.get("CANVAS_API_URL"),
        CANVAS_API_TOKEN=os.environ.get("CANVAS_API_TOKEN"),
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI= "sqlite:///" + os.path.join(app.instance_path, "student.sqlite"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is not None:
        app.config.from_mapping(test_config)
        
    # debug tools
    toolbar = DebugToolbarExtension(app)

    # storage
    db.init_app(app)
    cache.init_app(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # logic
    app.register_blueprint(errors.blueprint)
    app.register_blueprint(filters.blueprint)

    app.add_url_rule("/", methods=["GET"], view_func=routes.user_get_general_overview)
    app.add_url_rule("/search", view_func=routes.students_search)
    app.add_url_rule("/student/<int:id>", view_func=routes.student_show_overview)
    app.add_url_rule(
        "/student/<int:id>", methods=["POST"], view_func=routes.student_add_note
    )
    app.add_url_rule("/semester/<int:id>", view_func=routes.semester_show_overview)
    app.add_url_rule("/canvas", view_func=routes.canvas_show_available_courses)
    app.add_url_rule(
        "/canvas/course/<string:id>", view_func=routes.canvas_course_details
    )
    app.add_url_rule(
        "/canvas/course/<string:id>",
        methods=["POST"],
        view_func=routes.canvas_students_import,
    )
    app.add_url_rule("/media/<path:filename>", view_func=routes.get_media_file)

    return app

from typing import List
from flask import Blueprint
from datetime import datetime
from markupsafe import Markup

from student.models import Note, Student

blueprint = Blueprint("template_filters", __name__)


@blueprint.app_template_filter("datetimeformat")
def datetime_format(value: datetime, format="%d-%m-%y %H:%M"):
    return value.strftime(format)


@blueprint.app_template_filter("unescape")
def unescape_string(value: str):
    return Markup(value).unescape()


@blueprint.app_template_filter("all_students_notes_dates")
def all_students_notes_dates(value: List[Student]):
    print(value)

    notes_per_student = [s.notes for s in value]

    notes = [
        notes for notes_of_student in notes_per_student for notes in notes_of_student
    ]

    return [note.date_created for note in notes]

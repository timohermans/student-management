from flask import Blueprint
from datetime import datetime
from markupsafe import Markup

blueprint = Blueprint("template_filters", __name__)

@blueprint.app_template_filter("datetimeformat")
def datetime_format(value: datetime, format="%d-%m-%y %H:%M"):
    return value.strftime(format)


@blueprint.app_template_filter("unescape")
def unescape_string(value: str):
    return Markup(value).unescape()
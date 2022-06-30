from flask import Blueprint, abort, redirect, render_template
from sqlalchemy.exc import NoResultFound

blueprint = Blueprint("error_handlers", __name__)


@blueprint.app_errorhandler(404)
def not_found(error):
    return render_template("not_found.html"), 404


@blueprint.app_errorhandler(NoResultFound)
def db_entity_not_found(error):
    return not_found(error)

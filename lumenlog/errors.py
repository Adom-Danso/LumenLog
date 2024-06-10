from flask import Blueprint, render_template

errors = Blueprint("errors", __name__)

@errors.app_errorhandler(404)
def page_not_found(error):
    return render_template("error/404.html"), 404
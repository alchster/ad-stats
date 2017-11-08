from flask import Blueprint, render_template, redirect, request
from jinja2 import TemplateNotFound

from .util.reader import Reader

bp = Blueprint("ad-stats", __name__,
               static_folder="../web/static",
               static_url_path="",
               template_folder="../web/templates")


@bp.route("/", defaults={'page': 'index'})
@bp.route("/<page>")
def index(page):
    try:
        return render_template("%s.html" % page)
    except TemplateNotFound:
        return render_template("404.html")


@bp.route("/config", methods=["POST"])
def config_post():
    try:
        bp.reader = Reader(request.files["file"].read())
        return redirect("prepare")
    except:
        return render_template("error.html")
    return render_template("404.html")


@bp.route("/prepare")
def prepare():
    # TODO: make separate lists with new, updated and disabled (removed?) urls
    with bp.reader as reader:
        return render_template("prepare.html", urls=reader)


@bp.route("/update")
def update():
    if bp.reader is None:
        return render_template("error.html")
    with bp.reader as reader:
        print(reader)
        return render_template("success.html")

import logging
from datetime import datetime, date, MINYEAR

from flask import Blueprint, render_template, redirect, request, current_app
from jinja2 import TemplateNotFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy import extract

from .util.reader import Reader
from .util.tablename import tablename
from .models.urls import URLs
from .models.data import Data

from .fetcher import Fetcher

bp = Blueprint("ad-stats", __name__,
               static_folder="../web/static",
               static_url_path="",
               template_folder="../web/templates")


@bp.route("/", defaults={"page": "index"})
@bp.route("/<page>")
def main(page):
    urls = current_app.db.session.query(URLs).all()
    try:
        return render_template("%s.html" % page, urls=urls)
    except TemplateNotFound:
        return render_template("404.html")


@bp.route("/stat/<name>")
@bp.route("/stat/<name>/<int:year>")
@bp.route("/stat/<name>/<int:year>/<int:month>")
def stat(name, year=None, month=None):
    logging.debug("GET: stat: %s , year: %s, month: %s",
                  name, str(year), str(month))
    session = current_app.db.session
    model = Data.model(name)

    data = session.query(model)
    if year is not None:
        data = data.filter(extract("year", model.date) == year)
    if month is not None:
        data = data.filter(extract("month", model.date) == month)
    return render_template("stat.html", data=data.all())


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
    with bp.reader as reader:
        bp.separator = URLs.separate(current_app.db.session, reader)
    bp.reader = None
    return render_template("prepare.html", urls=bp.separator)


@bp.route("/update")
def update():
    if bp.separator is None:
        return render_template("error.html")
    session = current_app.db.session

    for url in bp.separator.removed:
        u = session.query(URLs).filter_by(url=url["url"]).first()
        Data.drop(session, u.table)
        session.delete(u)

    for url in bp.separator.modified:
        u = session.query(URLs).filter_by(url=url["url"]).first()
        u.modify(url)

    for url in bp.separator.added:
        tn = tablename(url["name"])
        u = URLs(name=url["name"],
                 table=tn,
                 url=url["url"],
                 username=url["username"],
                 password=url["password"])
        retries = 0
        # TODO?: move this to config
        max_tries = 5
        while retries < max_tries:
            try:
                session.add(u)
                Data.create(session, u.table)
                break
            except IntegrityError:
                logging.debug("Table '%s' is already exists", tn)
                retries += 1
                tn = "%s_%d" % (tablename(url["name"]), retries)
                u.table = tn
        if retries >= max_tries:
            return render_template("error.html")

    session.commit()
    return render_template("success.html")


@bp.route("/getdata")
def getdata():
    def get_parser(session, table_name):
        # TODO: create table if not exists
        DataTable = Data.model(table_name)

        def parser(row):
            row[0] = datetime.strptime(row[0], "%Y-%m-%d").date()
            data = session.query(DataTable).filter_by(date=row[0]).first()
            row = dict(zip(["date", "shows", "starts", "clicks"], row))
            if data is None:
                session.add(DataTable(**row))
            else:
                data.shows = row["shows"]
                data.starts = row["starts"]
                data.clicks = row["clicks"]
            session.commit()

        return parser

    session = current_app.db.session
    for url in session.query(URLs).all():
        for _ in Fetcher(url.url,
                         username=url.username,
                         password=url.password,
                         row_handler=get_parser(session, url.table)):
            pass
    session.commit()

    return render_template("success.html")

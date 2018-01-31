import logging
from datetime import datetime, MINYEAR

from flask import Blueprint, render_template, redirect, request, current_app, \
    Response, stream_with_context, jsonify, abort
from jinja2 import TemplateNotFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy import extract, func

from .util.reader import Reader
from .util.tablename import tablename
from .models.urls import URLs
from .models.data import Data
from .fetcher import Fetcher
from .auth import Auth as auth

bp = Blueprint("ad-stats", __name__,
               static_folder="../web/static",
               static_url_path="",
               template_folder="../web/templates")


@bp.route("/", defaults={"page": "index"})
@bp.route("/<page>")
@auth.require
def main(page):
    urls = current_app.db.session.query(URLs).all()
    try:
        return render_template("%s.html" % page, urls=urls)
    except TemplateNotFound:
        return render_template("404.html")


@bp.route("/months")
@auth.require
def months():
    session = current_app.db.session
    urls = session.query(URLs).all()
    return render_template("months.html", urls=urls)


@bp.route("/stat/<name>")
@bp.route("/stat/<name>/<int:year>")
@bp.route("/stat/<name>/<int:year>/<int:month>")
@auth.require
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
@auth.require
def config_post():
    try:
        bp.reader = Reader(request.files["file"].read())
        return redirect("prepare")
    except Exception:
        return render_template("error.html")
    return render_template("404.html")


@bp.route("/prepare")
@auth.require
def prepare():
    with bp.reader as reader:
        bp.separator = URLs.separate(current_app.db.session, reader)
    bp.reader = None
    return render_template("prepare.html", separator=bp.separator)


@bp.route("/update")
@auth.require
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


@bp.route("/service/fetchdata")
def service_fetchdata():
    def get_parser(session, table_name):
        # TODO: create table if not exists
        DataTable = Data.model(table_name)
        old_data = session.query(DataTable).all()

        def find(elem):
            dt = elem["date"]
            filtered = list(filter(lambda x: x.date == dt, old_data))
            return filtered[0] if len(filtered) > 0 else None

        def same(elem, row):
            if elem.shows == row["shows"] \
                    and elem.starts == row["starts"] \
                    and elem.clicks == row["clicks"]:
                return True
            return False

        def parser(row):
            row[0] = datetime.strptime(row[0], "%Y-%m-%d").date()
            for i in range(1, 4):
                try:
                    row[i] = int(row[i])
                except ValueError:
                    row[i] = 0

            row = dict(zip(["date", "shows", "starts", "clicks"], row))
            data = find(row)
            if data is None:
                session.add(DataTable(**row))
            else:
                if same(data, row):
                    return
                data.shows = row["shows"]
                data.starts = row["starts"]
                data.clicks = row["clicks"]
            return row

        return parser

    def process():
        session = current_app.db.session
        urls = session.query(URLs).all()
        current = 0
        total = len(urls)
        for url in urls:
            try:
                for row in Fetcher(url.url,
                                   username=url.username,
                                   password=url.password,
                                   row_handler=get_parser(session,
                                                          url.table)):
                    if row is not None:
                        logging.debug(row)
            except Exception as error:
                yield "data: Error while updating '%s': %s\n\n" % (url.name,
                                                                   error)
            current += 1
            yield "data:{:d}/{:d}|{:.0f}\n\n".format(current, total,
                                                     (current / total) * 100)
        session.commit()

    return Response(stream_with_context(process()),
                    mimetype="text/event-stream")


@bp.route("/fetchdata")
@auth.require
def fetchdata():
    return service_fetchdata()


@bp.route("/<name>/months")
# @auth.require
def months_data(name):
    session = current_app.db.session
    months = {}
    try:
        model = Data.model(
            session.query(URLs).filter_by(name=name).first().table)
    except AttributeError:
        return abort(404)
    for (date, ) in session.query(model.date).order_by(model.date).all():
        year = date.year
        if year not in months:
            months[year] = []
        month = date.month
        if month not in months[year]:
            months[year].append(month)
    return jsonify(months)

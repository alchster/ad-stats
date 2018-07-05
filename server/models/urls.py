import datetime

from sqlalchemy import Column, String, Unicode, DateTime, Boolean

from .base import Base
from ..util.separator import Separator


class URLs(Base):
    __tablename__ = "urls"
    name = Column(Unicode(100), nullable=False)
    table = Column(String(100), unique=True, nullable=False)
    url = Column(String(180), primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    created = Column(DateTime(timezone=True), default=datetime.datetime.now)
    modified = Column(DateTime(timezone=True), nullable=True,
                      onupdate=datetime.datetime.now)
    data_updated = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean(), default=True)

    def modify(self, url_info):
        self.name = url_info["name"]
        self.username = url_info["username"]
        self.password = url_info["password"]

    def __repr__(self):
        return "%s <URL: %s user: %s password: %s>" \
            % (self.name, self.url, self.username, self.password)

    @staticmethod
    def separate(session, urls):
        separator = Separator()
        new = set()
        for url in urls:
            l = separator.added
            if session.query(URLs).filter_by(url=url["url"]).count() > 0:
                l = separator.unchanged \
                    if session.query(URLs).\
                    filter_by(name=url["name"],
                              url=url["url"],
                              username=url["username"],
                              password=url["password"]).count() > 0 \
                    else separator.modified
            l.append(url)
            new.add(url["url"])

        for url in session.query(URLs).all():
            if url.url not in new:
                separator.removed.append(url.__dict__)

        return separator

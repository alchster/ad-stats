import logging

from sqlalchemy import Column, Integer, Date

from .base import Base


class Data(object):
    __tablename__ = None
    __table_args__ = {'extend_existing': True}
    date = Column(Date, primary_key=True)
    starts = Column(Integer, nullable=False, default=0)
    shows = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    viewability = Column(Integer, nullable=False, default=0)

    @staticmethod
    def model(name):
        return type(name.title(), (Data, Base), {'__tablename__': name})

    @staticmethod
    def create(session, name):
        logging.debug("Creating table %s", name)
        Data.model(name).__table__.create(session.get_bind())

    @staticmethod
    def drop(session, name):
        logging.debug("Dropping table %s", name)
        session.drop(Data.model(name))

    def __repr__(self):
        return "%s (%s, starts: %d, shows: %d, clicks: %d)" % \
            (self.__tablename__, self.date.strftime("%Y-%m-%d"),
             self.starts, self.shows, self.clicks)

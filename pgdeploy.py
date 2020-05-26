import os

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date

# Declare the database in PostgreSQL
Base = declarative_base()

class SongsCleared(Base):
    __tablename__ = 'SongsCleared'
    id = Column(Integer, primary_key=True)
    song = Column(String)
    chatid = Column(Integer)
    level = Column(Integer)

    def __repr__(self):
        return "<SongsCleared(id='{}', song='{}', chatid='{}', level='{}')>".format(self.id, self.song, self.chatid, self.level)

class User(Base):
    __tablename__ = 'User'
    chatid = Column(Integer, primary_key=True)
    level = Column(Integer)

    def __repr__(self):
        return "<User(chatid='{}', level='{}')>".format(self.chatid, self.level)

class TitleCard(Base):
    __tablename__ = 'TitleCard'
    song = Column(String, primary_key=True)
    cut = Column(String, primary_key=True)
    image = Column(String)

    def __repr__(self):
        return "<TitleCard(song='{}', cut='{}', image='{}')>".format(self.song, self.cut, self.image)


# To ensure that each change to the database is in a separate session
@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Make the database, if it does not exist before
DATABASE_URI = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


# Database query functions
def add_user(chatid, level):
    with session_scope() as s:
        user_to_add = User(chatid=chatid, level=level)
        s.add(user_to_add)


def update_user(chatid, level):
    with session_scope() as s:
        user_in_query = s.query(User).filter(User.chatid==chatid).first()
        user_in_query.level = level


def get_user_level(chatid):
    with session_scope() as s:
        user_in_query = s.query(User).filter(User.chatid==chatid).first()
        return user_in_query.level if user_in_query else None


def add_item(song, chatid):
    with session_scope() as s:
        user_in_query = s.query(User).filter(User.chatid==chatid).first()
        level = user_in_query.level
        song_to_add = SongsCleared(song=song, chatid=chatid, level=level)
        s.add(song_to_add)


def delete_item(song, chatid):
    with session_scope() as s:
        song_to_delete = s.query(SongsCleared).filter(and_(SongsCleared.song==song, SongsCleared.chatid==chatid)).first()
        s.delete(song_to_delete)


def get_items(chatid):
    with session_scope() as s:
        user_in_query = s.query(User).filter(User.chatid==chatid).first()
        level = user_in_query.level
        list_of_tup = s.query(SongsCleared.song).filter(and_(SongsCleared.chatid==chatid, SongsCleared.level==level)).order_by(SongsCleared.id)
        return [tup[0] for tup in list_of_tup]

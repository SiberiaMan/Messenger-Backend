from sqlalchemy import (
    Integer, Column, ForeignKey, DateTime, String, Index, func, cast
)
import datetime

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False, unique=True) # два чата с одним именем существовать не могут


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    chat = Column(Integer, ForeignKey('chats.id'), nullable=False)
    login = Column(String, nullable=False) # при вставке пользователя в чат, смотрим состоит ли он уже в чате или нет
                                            # если да, то говорим что пользователь уже тут есть


class Login(Base):
    __tablename__ = 'logins'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user = Column(Integer, ForeignKey('users.id'), nullable=False)
    chat = Column(Integer, ForeignKey('chats.id'), nullable=False)
    msg = Column(String, nullable=False)
    time_created = Column(DateTime, default=datetime.datetime.now, nullable=False)


class TaskMessages(Base):
    __tablename__ = "search_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, nullable=False)
    msg = Column(String, nullable=False)
    time_created = Column(DateTime, default=datetime.datetime.now, nullable=False)


class UserConfig(Base):
    __tablename__ = "configs"

    id = Column(Integer, primary_key=True, nullable=False)
    timezone = Column(DateTime, nullable=False)

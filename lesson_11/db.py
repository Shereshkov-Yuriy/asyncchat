"""Storage"""
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

DB_URL = "sqlite:///db.sqlite3"
BASE = declarative_base()


class Storage(object):

    def __init__(self):
        self.db_engine = sa.create_engine(DB_URL, echo=False, pool_recycle=7200)
        BASE.metadata.create_all(self.db_engine)
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()

    class User(BASE):
        __tablename__ = "users"
        id = sa.Column(sa.Integer, primary_key=True)
        username = sa.Column(sa.String, unique=True)
        last_login = sa.Column(sa.DateTime)

        def __init__(self, username, last_login):
            self.username = username
            self.last_login = last_login

        def __repr__(self):
            return f"User <{self.username}>"

    class LoginHistory(BASE):
        __tablename__ = "login_history"
        id = sa.Column(sa.Integer, primary_key=True)
        user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
        login_time = sa.Column(sa.DateTime)
        ip = sa.Column(sa.String)
        port = sa.Column(sa.String)

        def __init__(self, user_id, login_time, ip, port):
            self.user_id = user_id
            self.login_time = login_time
            self.ip = ip
            self.port = port

    class Contacts(BASE):
        __tablename__ = "contacts"
        owner_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
        target_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))

        __table_args__ = (
            sa.PrimaryKeyConstraint("owner_id", "target_id"),
            sa.CheckConstraint("owner_id != target_id"),
        )

    def get_session(self):
        return self.session

    def create_users(self, name):
        user_request = self.session.query(self.User).filter_by(username=name).one_or_none()
        if user_request is not None:
            print(f"Пользователь с именем {name} уже существует")
            return None
        user = self.User(name, datetime.now())
        self.session.add(user)
        self.session.commit()

    def users_list(self):
        query = self.session.query(self.User)
        return query.all()


if __name__ == "__main__":
    db = Storage()
    db.create_users("Jeeves")
    db.create_users("Wooster")

    print(db.users_list())

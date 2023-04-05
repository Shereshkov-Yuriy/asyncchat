"""Server Storage"""
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
from constants import *

BASE = declarative_base()


class ServerStorage(object):

    def __init__(self):
        self.db_engine = sa.create_engine(DB_URL, echo=False, pool_recycle=7200)
        BASE.metadata.create_all(self.db_engine)
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        self.session.query(self.LoginUsers).delete()
        self.session.commit()

    class Users(BASE):
        __tablename__ = "users"
        id = sa.Column(sa.Integer, primary_key=True)
        username = sa.Column(sa.String, unique=True)
        last_login = sa.Column(sa.DateTime)

        history = relationship("LoginHistory", backref="users")

        def __init__(self, username):
            self.username = username
            self.last_login = datetime.now()

        def __repr__(self):
            return f"User <{self.username}> last login: <{self.last_login}>"

    class LoginUsers(BASE):
        __tablename__ = "login_users"
        id = sa.Column(sa.Integer, primary_key=True)
        user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
        ip = sa.Column(sa.String)
        port = sa.Column(sa.Integer)
        login_time = sa.Column(sa.DateTime)

        user = relationship("Users", backref="login_users", uselist=False)

        def __init__(self, user_id, ip, port, login_time):
            self.user_id = user_id
            self.ip = ip
            self.port = port
            self.login_time = login_time

        # def __repr__(self):
        #     return f"<{self.user.username}, {self.ip}, {self.port}, {self.login_time}>"

    class LoginHistory(BASE):
        __tablename__ = "login_history"
        id = sa.Column(sa.Integer, primary_key=True)
        user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
        ip = sa.Column(sa.String)
        port = sa.Column(sa.String)
        history_date = sa.Column(sa.DateTime)

        def __init__(self, user_id, ip, port, history_date):
            self.user_id = user_id
            self.ip = ip
            self.port = port
            self.history_date = history_date

    class Contacts(BASE):
        __tablename__ = "contacts"
        owner_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
        target_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))

        __table_args__ = (
            sa.PrimaryKeyConstraint("owner_id", "target_id"),
            sa.CheckConstraint("owner_id != target_id"),
        )

        def __init__(self, owner_id, target_id):
            self.owner_id = owner_id
            self.target_id = target_id

    def user_login(self, username, ip, port):
        print(username, ip, port)
        check_user = self.session.query(self.Users).filter_by(username=username).first()
        if check_user is None:
            user = self.Users(username)
            self.session.add(user)
            self.session.commit()
            print(f"create user: {user.username}")
        else:
            user = check_user
            user.last_login = datetime.now()
            print(f"login user: {user.username}")
        new_login_user = self.LoginUsers(user.id, ip, port, datetime.now())
        self.session.add(new_login_user)
        new_login_history = self.LoginHistory(user.id, ip, port, datetime.now())
        self.session.add(new_login_history)
        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.Users).filter_by(username=username).first()
        self.session.query(self.LoginUsers).filter_by(id=user.id).delete()
        self.session.commit()

    def users_list(self):
        query = self.session.query(self.Users)
        return query.all()

    def login_list(self):
        query = self.session.query(
            self.Users.username,
            self.LoginUsers.ip,
            self.LoginUsers.port,
            self.LoginUsers.login_time,
        ).join(self.Users)
        return query.all()

    def login_history(self, username=None):
        query = self.session.query(self.Users.username,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port,
                                   self.LoginHistory.history_date,
                                   ).join(self.Users)
        if username:
            query = query.filter(self.Users.username == username)
        return query.all()

    def add_contact(self, owner, target):
        owner = self.session.query(self.Users).filter_by(username=owner).first()
        target = self.session.query(self.Users).filter_by(username=target).first()
        if owner is None or target is None:
            return
        if self.session.query(self.Contacts).filter_by(owner_id=owner.id, target_id=target.id).count():
            return
        if owner.id != target.id:
            new_contact = self.Contacts(owner.id, target.id)
            self.session.add(new_contact)
            self.session.commit()

    def del_contact(self, owner, target):
        owner = self.session.query(self.Users).filter_by(username=owner).first()
        target = self.session.query(self.Users).filter_by(username=target).first()
        if not target:
            return
        self.session.query(self.Contacts).filter_by(owner_id=owner.id, target_id=target.id).delete()
        self.session.commit()

    def get_contacts(self, owner):
        owner = self.session.query(self.Users).filter_by(username=owner).one()
        query = self.session.query(self.Contacts, self.Users.username).filter_by(owner_id=owner.id).\
            join(self.Users, self.Contacts.target_id == self.Users.id)
        return print([contact[1] for contact in query.all()])


if __name__ == "__main__":
    db = ServerStorage()
    # Проверка работы БД
    db.user_login("Jeeves", "127.0.0.1", "7777")
    db.user_login("Wooster", "127.0.0.1", "7788")
    # print(db.login_list())
    # db.user_logout("Wooster")
    # print(db.login_list())
    # print(db.login_history("Wooster"))
    # print(db.users_list())
    # db.add_contact("Jeeves", "Wooster")
    # db.add_contact("Jeeves", "Georgy")
    # db.add_contact("Wooster", "Jeeves")
    # db.add_contact("Wooster", "Georgy")
    # db.del_contact("Wooster", "Jeeves")
    # db.del_contact("Jeeves", "Wooster")
    # db.get_contacts("Wooster")
    # db.add_contact("yu", "Wooster")
    # db.add_contact("yu", "Jeeves")
    print(db.login_list())

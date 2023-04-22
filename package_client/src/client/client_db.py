"""Client Storage"""
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker

from common.constants import CLIENT_DIR

BASE = declarative_base()


class ClientDatabase(object):
    """
    Основной класс для работы с БД пользователей.
    Использует SQLite базу данных, реализован с помощью
    SQLAlchemy ORM и используется декларативный подход.
    """

    def __init__(self, name):
        filename = f"db_{name}.sqlite3"
        self.db_engine = sa.create_engine(
            f"sqlite:///{CLIENT_DIR / filename}",
            echo=False,
            pool_recycle=7200,
            connect_args={"check_same_thread": False},
        )
        BASE.metadata.create_all(self.db_engine)
        current_session = sessionmaker(bind=self.db_engine)
        self.session = current_session()
        self.session.query(self.Contacts).delete()
        self.session.commit()

    class Knowns(BASE):
        """Класс, реализующий таблицу известных пользователей."""

        __tablename__ = "knowns"
        id = sa.Column(sa.Integer, primary_key=True)
        username = sa.Column(sa.String)

        def __init__(self, username):
            self.username = username

    class MessageHistory(BASE):
        """Класс, реализующий таблицу истории сообщений пользователей."""

        __tablename__ = "message_history"
        id = sa.Column(sa.Integer, primary_key=True)
        from_user = sa.Column(sa.String)
        to_user = sa.Column(sa.String)
        message = sa.Column(sa.Text)
        date = sa.Column(sa.DateTime)

        def __init__(self, from_user, to_user, message):
            self.from_user = from_user
            self.to_user = to_user
            self.message = message
            self.date = datetime.now()

    class Contacts(BASE):
        """Класс, реализующий таблицу контактов пользователей."""

        __tablename__ = "contacts"
        id = sa.Column(sa.Integer, primary_key=True)
        username = sa.Column(sa.String, unique=True)

        def __init__(self, username):
            self.username = username

    def add_contact(self, username):
        if (
            not self.session.query(self.Contacts)
            .filter_by(username=username)
            .count()
        ):
            new_contact = self.Contacts(username)
            self.session.add(new_contact)
            self.session.commit()

    def del_contact(self, username):
        self.session.query(self.Contacts).filter_by(username=username).delete()

    def get_contacts(self):
        return [
            contact[0]
            for contact in self.session.query(self.Contacts.username).all()
        ]

    def check_contact(self, username):
        if (
            self.session.query(self.Contacts)
            .filter_by(username=username)
            .count()
        ):
            return True
        return False

    def clear_contacts(self):
        self.session.query(self.Contacts).delete()

    def add_users(self, users_list):
        self.session.query(self.Knowns).delete()
        for user in users_list:
            user_row = self.Knowns(user)
            self.session.add(user_row)
        self.session.commit()

    def get_users(self):
        return [
            user[0] for user in self.session.query(self.Knowns.username).all()
        ]

    def check_user(self, username):
        if (
            self.session.query(self.Knowns)
            .filter_by(username=username)
            .count()
        ):
            return True
        return False

    def save_message(self, from_user, to_user, message):
        message_row = self.MessageHistory(from_user, to_user, message)
        self.session.add(message_row)
        self.session.commit()

    def get_history(self, from_user):
        query = self.session.query(self.MessageHistory).filter_by(
            from_user=from_user
        )
        return [
            (
                history_row.from_user,
                history_row.to_user,
                history_row.message,
                history_row.date,
            )
            for history_row in query.all()
        ]


if __name__ == "__main__":
    db = ClientDatabase("tester2")
    # проверка работы БД
    for i in ["tester1", "tester2", "tester3", "tester4"]:
        db.add_contact(i)
    # db.add_contact("tester4")
    # db.add_users(["tester1", "tester2", "tester3", "tester4", "tester5"])
    # db.save_message("tester1", "tester2", "Бегом в корабль.")
    # db.save_message("tester2", "tester1", "Залетай в гости.")
    # print(db.get_contacts())
    # print(db.get_users())
    # print(db.check_user("tester1"))
    # print(db.check_user("tester8"))
    # print(db.get_history("tester4"))
    # print(db.get_history(from_user="tester4"))
    # print(db.get_history("tester1"))
    # db.del_contact("tester4")
    # print(db.get_contacts())

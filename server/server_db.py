"""Server Storage"""
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from common.constants import DB_URL

BASE = declarative_base()


class ServerStorage(object):
    """
    Основной класс для работы с БД сервера.
    Использует SQLite базу данных, реализован с помощью
    SQLAlchemy ORM и используется декларативный подход.
    """

    def __init__(self):
        self.db_engine = sa.create_engine(
            DB_URL, echo=False, pool_recycle=7200
        )
        BASE.metadata.create_all(self.db_engine)
        current_session = sessionmaker(bind=self.db_engine)
        self.session = current_session()
        self.session.query(self.LoginUsers).delete()
        self.session.commit()

    class Users(BASE):
        """Класс, реализующий таблицу пользователей"""

        __tablename__ = "users"
        id = sa.Column(sa.Integer, primary_key=True)
        username = sa.Column(sa.String, unique=True)
        password_hash = sa.Column(sa.String)
        last_login = sa.Column(sa.DateTime)

        history = relationship("LoginHistory", backref="users")

        def __init__(self, username, password_hash):
            self.username = username
            self.password_hash = password_hash
            self.last_login = datetime.now()

    class LoginUsers(BASE):
        """Класс, реализующий таблицу подключенных пользователей"""

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

    class LoginHistory(BASE):
        """Класс, реализующий таблицу истории подключений пользователей"""

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
        """Класс, реализующий таблицу контактов пользователей"""

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

    def user_login(self, username, ip, port, password):
        """Обрабатывает подключение пользователя."""
        print(username, ip, port, password)
        check_user = (
            self.session.query(self.Users).filter_by(username=username).first()
        )
        if check_user is None:
            user = self.Users(username, password)
            self.session.add(user)
            self.session.commit()
            print(f"create user: {user.username}")
        else:
            user = check_user
            user.last_login = datetime.now()
            print(f"login user: {user.username}")
        new_login_user = self.LoginUsers(user.id, ip, port, datetime.now())
        self.session.add(new_login_user)
        new_login_history = self.LoginHistory(
            user.id, ip, port, datetime.now()
        )
        self.session.add(new_login_history)
        self.session.commit()

    def add_user(self, username, password_hash):
        """Регистрирует пользователя в БД."""
        user_row = self.Users(username, password_hash)
        self.session.add(user_row)
        self.session.commit()

    def del_user(self, username):
        """Удаляет пользователя из БД."""
        user = (
            self.session.query(self.Users).filter_by(username=username).first()
        )
        self.session.query(self.LoginUsers).filter_by(user_id=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(
            user_id=user.id
        ).delete()
        self.session.query(self.Contacts).filter_by(owner_id=user.id).delete()
        self.session.query(self.Contacts).filter_by(target_id=user.id).delete()
        self.session.query(self.Users).filter_by(username=username).delete()
        self.session.commit()

    def get_hash(self, username):
        """Получить хэш пароля пользователя."""
        user = (
            self.session.query(self.Users).filter_by(username=username).first()
        )
        return user.password_hash

    def check_user(self, username):
        """Проверяет существование пользователя."""
        if self.session.query(self.Users).filter_by(username=username).count():
            return True
        return False

    def user_logout(self, username):
        """Обрабатывает отключение пользователя."""
        user = (
            self.session.query(self.Users).filter_by(username=username).first()
        )
        self.session.query(self.LoginUsers).filter_by(user_id=user.id).delete()
        self.session.commit()

    def users_list(self):
        """Возвращает список известных пользователей."""
        query = self.session.query(self.Users.username, self.Users.last_login)
        return query.all()

    def login_list(self):
        """Возвращает список активных пользователей."""
        query = self.session.query(
            self.Users.username,
            self.LoginUsers.ip,
            self.LoginUsers.port,
            self.LoginUsers.login_time,
        ).join(self.Users)
        return query.all()

    def login_history(self, username=None):
        """Возвращает историю подключений."""
        query = self.session.query(
            self.Users.username,
            self.LoginHistory.ip,
            self.LoginHistory.port,
            self.LoginHistory.history_date,
        ).join(self.Users)
        if username:
            query = query.filter(self.Users.username == username)
        return query.all()

    def add_contact(self, owner, target):
        """Создает контакт пользователей."""
        owner = (
            self.session.query(self.Users).filter_by(username=owner).first()
        )
        target = (
            self.session.query(self.Users).filter_by(username=target).first()
        )
        if owner is None or target is None:
            return
        if (
            self.session.query(self.Contacts)
            .filter_by(owner_id=owner.id, target_id=target.id)
            .count()
        ):
            return
        if owner.id != target.id:
            new_contact = self.Contacts(owner.id, target.id)
            self.session.add(new_contact)
            self.session.commit()

    def del_contact(self, owner, target):
        """Удаляет контакт пользователей."""
        owner = (
            self.session.query(self.Users).filter_by(username=owner).first()
        )
        target = (
            self.session.query(self.Users).filter_by(username=target).first()
        )
        if not target:
            return
        self.session.query(self.Contacts).filter(
            self.Contacts.owner_id == owner.id,
            self.Contacts.target_id == target.id,
        ).delete()
        self.session.commit()

    def get_contacts(self, username):
        """Возвращает список контактов пользователя."""
        owner = (
            self.session.query(self.Users).filter_by(username=username).one()
        )
        query = (
            self.session.query(self.Contacts, self.Users.username)
            .filter_by(owner_id=owner.id)
            .join(self.Users, self.Contacts.target_id == self.Users.id)
        )
        return [contact[1] for contact in query.all()]


if __name__ == "__main__":
    # Проверка работы БД
    import binascii
    import hashlib

    from common.constants import ENCODING, HASH_NAME

    def pwd_hash(username, password):
        passwd_bytes = password.encode(ENCODING)
        salt = username.lower().encode(ENCODING)
        passwd_hash = hashlib.pbkdf2_hmac(HASH_NAME, passwd_bytes, salt, 10000)
        passwd_hash_string = binascii.hexlify(passwd_hash)

        return passwd_hash_string

    db = ServerStorage()
    # Проверка работы БД
    j = "Jeeves"
    w = "Wooster"
    t_1 = "tester1"
    t_2 = "tester2"
    db.user_login(t_1, "127.0.0.1", "7777", pwd_hash(t_1, "123456"))
    db.user_login(t_2, "127.0.0.1", "7788", pwd_hash(t_2, "123456"))
    print(db.login_list())
    db.user_logout(t_1)
    print(db.login_list())
    print(db.login_history(t_1))
    print(db.users_list())
    db.add_contact(t_2, t_1)
    db.add_contact(t_1, "Georgy")
    db.add_contact(t_1, t_2)
    db.add_contact(t_2, "Georgy")
    # db.del_contact("Wooster", "Jeeves")
    # db.del_contact("Jeeves", "Wooster")
    db.get_contacts("Wooster")
    # db.add_contact("yu", "Wooster")
    # db.add_contact("yu", "Jeeves")
    print(db.login_list())

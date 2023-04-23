import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QDialog, QLabel, QPushButton

logger = logging.getLogger("client")


class AddContactDialog(QDialog):
    """Диалог выбора контакта для добавления"""

    def __init__(self, sock, db):
        super().__init__()
        self.sock = sock
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(350, 120)
        self.setWindowTitle("Выберите контакт для добавления:")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel("Выберите контакт для добавления:", self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_refresh = QPushButton("Обновить список", self)
        self.btn_refresh.setFixedSize(100, 30)
        self.btn_refresh.move(60, 60)

        self.btn_ok = QPushButton("Добавить", self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton("Отмена", self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        # Заполняем список возможных контактов
        self.possible_contacts_update()
        # Назначаем действие на кнопку обновить
        self.btn_refresh.clicked.connect(self.update_possible_contacts)

    def possible_contacts_update(self):
        """Заполняет список возможных контактов"""
        self.selector.clear()
        # множества всех контактов и контактов клиента
        contacts_list = set(self.db.get_contacts())
        users_list = set(self.db.get_users())
        # Удалим сами себя из списка пользователей,
        # чтобы нельзя было добавить самого себя
        users_list.remove(self.sock.username)
        # Добавляем список возможных контактов
        self.selector.addItems(users_list - contacts_list)

    def update_possible_contacts(self):
        """Обновляет список возможных контактов"""
        try:
            self.sock.user_list_update()
        except OSError:
            pass
        else:
            logger.debug("Обновление списка пользователей с сервера выполнено")
            self.possible_contacts_update()

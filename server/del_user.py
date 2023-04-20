from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, qApp
from PyQt5.QtCore import Qt


class DelUserDialog(QDialog):
    """Класс - диалог выбора контакта для удаления."""

    def __init__(self, db, server):
        super().__init__()
        self.db = db
        self.server = server

        self.setFixedSize(350, 120)
        self.setWindowTitle('Удаление пользователя')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите пользователя для удаления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_ok = QPushButton('Удалить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)
        self.btn_ok.clicked.connect(self.del_user)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(qApp.quit)

        self.all_users_fill()

    def all_users_fill(self):
        """Метод заполняющий список пользователей."""
        self.selector.addItems([item[0] for item in self.db.users_list()])

    def del_user(self):
        """Метод - обработчик удаления пользователя."""
        self.db.del_user(self.selector.currentText())
        if self.selector.currentText() in self.server.names:
            sock = self.server.names[self.selector.currentText()]
            del self.server.names[self.selector.currentText()]
            self.server.del_client(sock)
        # Рассылаем клиентам сообщение о необходимости обновить справочники
        self.server.service_update_lists()
        self.close()

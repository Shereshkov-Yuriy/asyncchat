import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QDialog
from server.add_user import RegisterUser
from server.del_user import DelUserDialog


class MainWindow(QMainWindow):
    """Класс основного окна сервера."""

    def __init__(self, db, server):
        super().__init__()
        self.db = db
        self.server_thread = server

        # Задать параметры окна.
        self.setWindowTitle("Server app (Administration).")
        self.setGeometry(200, 200, 560, 480)
        # Задать элементы окна. Настроить элементы окна.
        self.exit_action = QAction("Выход", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(qApp.quit)
        self.btn_refresh = QAction('Обновить список', self)
        self.btn_register = QAction('Регистрация пользователя', self)
        self.btn_remove = QAction('Удаление пользователя', self)
        self.list_action = QAction("Список клиентов", self)
        self.stat_action = QAction("Статистика клиентов", self)
        self.conf_action = QAction("Конфигурация сервера", self)
        self.conf_action.setDisabled(True)  # В разработке
        self.statusBar()
        self.statusBar().showMessage("Server ready.")
        self.tool_bar = self.addToolBar("MainBar")
        self.tool_bar.addAction(self.exit_action)
        self.tool_bar.addAction(self.btn_refresh)
        self.tool_bar.addAction(self.btn_register)
        self.tool_bar.addAction(self.btn_remove)
        self.tool_bar.addAction(self.list_action)
        self.tool_bar.addAction(self.stat_action)
        self.tool_bar.addAction(self.conf_action)

        self.list_label = QtWidgets.QLabel("Список подключенных клиентов: ", self)
        self.list_label.setAlignment(QtCore.Qt.AlignCenter)
        self.list_label.setGeometry(0, 0, 560, 16)
        self.list_label.move(12, 24)

        self.list_table = QtWidgets.QTableView(self)
        self.list_table.setFixedSize(536, 360)
        self.list_table.setGeometry(0, 0, 536, 360)
        self.list_table.move(12, 48)

        # Окно со списком подключённых клиентов.
        self.active_clients_table = QtWidgets.QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)

        # Таймер, обновляющий список клиентов 1 раз в секунду
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.create_users_model)
        self.timer.start(1000)

        # Связываем кнопки с процедурами
        self.btn_refresh.triggered.connect(self.create_users_model)
        self.btn_register.triggered.connect(self.reg_user)
        self.btn_remove.triggered.connect(self.rem_user)

        # Последним параметром отображаем окно.
        self.show()

    def create_users_model(self):
        """Метод заполняющий таблицу активных пользователей."""
        list_users = self.db.login_list()
        sample_list = QtGui.QStandardItemModel()
        sample_list.setHorizontalHeaderLabels(["Клиент", "IPv4", "Порт", "Время логина"])
        for row in list_users:
            user, ip, port, time = row
            user = QtGui.QStandardItem(user)
            user.setEditable(False)
            ip = QtGui.QStandardItem(ip)
            ip.setEditable(False)
            port = QtGui.QStandardItem(str(port))
            port.setEditable(False)
            time = QtGui.QStandardItem(str(time.replace(microsecond=0)))
            time.setEditable(False)
            sample_list.appendRow([user, ip, port, time])
        self.active_clients_table.setModel(sample_list)
        self.active_clients_table.resizeColumnsToContents()
        self.active_clients_table.resizeRowsToContents()

    def reg_user(self):
        """Метод создающий окно регистрации пользователя."""
        global reg_window
        reg_window = RegisterUser(self.db, self.server_thread)
        reg_window.show()

    def rem_user(self):
        """Метод создающий окно удаления пользователя."""
        global rem_window
        rem_window = DelUserDialog(self.db, self.server_thread)
        rem_window.show()


# В разработке
class StatisticsWindow(QDialog):
    """Класс окна статистики клиента."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Статистика по клиентам")
        self.setFixedSize(536, 360)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.close_btn = QtWidgets.QPushButton("Закрыть", self)
        self.close_btn.move(10, 10)
        self.close_btn.clicked.connect(self.close)

        self.stat_table = QtWidgets.QTableView(self)
        self.stat_table.setFixedSize(512, 260)
        self.stat_table.move(12, 48)


if __name__ == "__main__":
    # Создать приложение.
    app = QApplication(sys.argv)
    # Создать окно. Может быть несколько.
    main_ = MainWindow(None, None)
    # stat_ = StatisticsWindow()
    # Показать окно.
    main_.show()
    # stat_.show()
    sys.exit(app.exec_())

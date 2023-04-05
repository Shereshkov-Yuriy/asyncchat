import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QDialog


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Задать параметры окна.
        self.setWindowTitle("Server app (Administration).")
        self.setGeometry(200, 200, 560, 480)
        # Задать элементы окна. Настроить элементы окна.
        self.exit_action = QAction("Выход", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(qApp.quit)
        self.list_action = QAction("Список клиентов", self)
        self.stat_action = QAction("Статистика клиентов", self)
        self.conf_action = QAction("Конфигурация сервера", self)
        self.conf_action.setDisabled(True)  # В разработке
        self.tool_bar = self.addToolBar("MainBar")
        self.tool_bar.addAction(self.exit_action)
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


class StatisticsWindow(QDialog):
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


def fill_list(db):
    list_users = db.login_list()
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
    return sample_list


def application():
    # Создать приложение.
    app = QApplication(sys.argv)
    # Создать окно. Может быть несколько.
    main_ = MainWindow()
    # stat_ = StatisticsWindow()
    # Показать окно.
    main_.show()
    # stat_.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    application()

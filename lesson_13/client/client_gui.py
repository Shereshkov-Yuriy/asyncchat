import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QDesktopWidget, QMainWindow, QTextEdit, QAction, QPushButton,
    QHBoxLayout, QVBoxLayout, QListView, QLabel, QMessageBox)
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, Qt

sys.path.append("../")
from .make_add import AddContactDialog
from .make_del import DelContactDialog

logger = logging.getLogger("client")


class MainWindow(QMainWindow):

    def __init__(self, sock, db):
        super().__init__()
        self.sock = sock
        self.db = db

        # Макет основного виджета
        window = QWidget()
        self.setCentralWidget(window)

        self.contacts_label = QLabel("Список контактов:")
        self.contacts = QListView()
        self.btn_add_con = QPushButton("&Добавить контакт")
        self.btn_del_con = QPushButton("&Удалить контакт")
        self.history_label = QLabel("История сообщений:")
        self.history = QListView()
        self.message_label = QLabel("Текст сообщения:")
        self.message = QTextEdit()
        self.btn_clear = QPushButton("&Очистить поле")
        self.btn_send = QPushButton("Отправить &сообщение")

        hbox = QHBoxLayout()

        vbox_left = QVBoxLayout()
        vbox_left.addWidget(self.contacts_label)
        vbox_left.addWidget(self.contacts)
        hbox_vl = QHBoxLayout()
        hbox_vl.addStretch(1)
        hbox_vl.addWidget(self.btn_add_con)
        hbox_vl.addWidget(self.btn_del_con)
        vbox_left.addLayout(hbox_vl)

        vbox_right = QVBoxLayout()
        vbox_right.addWidget(self.history_label)
        vbox_right.addWidget(self.history, 3)
        vbox_right.addWidget(self.message_label)
        vbox_right.addWidget(self.message, 1)
        hbox_vr = QHBoxLayout()
        hbox_vr.addStretch(1)
        hbox_vr.addWidget(self.btn_clear)
        hbox_vr.addWidget(self.btn_send)
        vbox_right.addLayout(hbox_vr)

        hbox.addLayout(vbox_left, 1)
        hbox.addLayout(vbox_right, 3)
        window.setLayout(hbox)

        self.exitAction = QAction(QIcon('exit.svg'), '&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.close)
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('&File')
        self.fileMenu.addAction(self.exitAction)
        self.statusBar().showMessage('Ready')
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(self.exitAction)

        self.setGeometry(400, 400, 400, 400)
        self.center_screen()
        self.setWindowTitle('Main window')

        self.btn_clear.clicked.connect(self.message.clear)
        self.btn_send.clicked.connect(self.send_message)
        self.btn_del_con.clicked.connect(self.del_contact_window)
        self.btn_add_con.clicked.connect(self.add_contact_window)

        # Дополнительные требующиеся атрибуты
        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None
        self.history.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.history.setWordWrap(True)

        self.contacts.doubleClicked.connect(self.select_active_user)

        self.clients_list_update()
        self.set_disabled_input()

        self.show()

    def center_screen(self):
        window_frame = self.frameGeometry()
        window_avail = QDesktopWidget().availableGeometry().center()
        window_frame.moveCenter(window_avail)
        self.move(window_frame.topLeft())

    def set_disabled_input(self):
        self.message_label.setText('Для выбора получателя дважды кликните на нем в окне контактов.')
        self.message.clear()
        if self.history_model:
            self.history_model.clear()
        self.btn_clear.setDisabled(True)
        self.btn_send.setDisabled(True)
        self.message.setDisabled(True)

    def clients_list_update(self):
        contacts_list = self.db.get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.contacts.setModel(self.contacts_model)

    # Заполняем историю сообщений.
    def history_list_update(self):
        # Получаем историю сортированную по дате
        list_sort = sorted(self.db.get_history(self.current_chat), key=lambda item: item[3])
        # Если модель не создана, создадим.
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.history.setModel(self.history_model)
        # Очистим от старых записей
        self.history_model.clear()
        # Берём не более 20 последних записей.
        length = len(list_sort)
        start_index = 0
        if length > 20:
            start_index = length - 20
        # Заполнение модели записями, так-же стоит разделить входящие и исходящие выравниванием и разным фоном.
        # Записи в обратном порядке, поэтому выбираем их с конца и не более 20
        for i in range(start_index, length):
            item = list_sort[i]
            if item[1] == 'in':
                mess = QStandardItem(f'Входящее от {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            else:
                mess = QStandardItem(f'Исходящее от {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setTextAlignment(Qt.AlignRight)
                mess.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(mess)
        self.history.scrollToBottom()

    # Функция обработчик даблклика по контакту
    def select_active_user(self):
        # Выбранный пользователем (даблклик) находится в выделеном элементе в QListView
        self.current_chat = self.contacts.currentIndex().data()
        # вызываем основную функцию
        self.set_active_user()

    # Функция устанавливающяя активного собеседника
    def set_active_user(self):
        # Ставим надпись и активируем кнопки
        self.message_label.setText(f'Введите сообщенние для {self.current_chat}:')
        self.btn_clear.setDisabled(False)
        self.btn_send.setDisabled(False)
        self.message.setDisabled(False)

        # Заполняем окно историю сообщений по требуемому пользователю.
        self.history_list_update()

    def send_message(self):
        message_text = self.message.toPlainText()
        self.message.clear()
        if not message_text:
            return
        try:
            self.sock.send_message(self.current_chat, message_text)
            pass
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
            self.close()
        else:
            self.db.save_message(self.current_chat, 'out', message_text)
            logger.debug(f'Отправлено сообщение для {self.current_chat}: {message_text}')
            self.history_list_update()

    # Функция удаления контакта
    def del_contact_window(self):
        global del_dialog
        del_dialog = DelContactDialog(self.db)
        del_dialog.btn_ok.clicked.connect(lambda: self.del_contact(del_dialog))
        del_dialog.show()

    def del_contact(self, item):
        selected = item.selector.currentText()
        try:
            self.sock.del_contact(selected)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.db.del_contact(selected)
            self.clients_list_update()
            logger.info(f'Успешно удалён контакт {selected}')
            self.messages.information(self, 'Успех', 'Контакт успешно удалён.')
            item.close()
            # Если удалён активный пользователь, то деактивируем поля ввода.
            if selected == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    # Функция добавления контакта
    def add_contact_window(self):
        global select_dialog
        select_dialog = AddContactDialog(self.sock, self.db)
        select_dialog.btn_ok.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    # Функция - обработчик добавления, сообщает серверу, обновляет таблицу и список контактов
    def add_contact_action(self, item):
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, new_contact):
        try:
            self.sock.add_contact(new_contact)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.db.add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            logger.info(f'Успешно добавлен контакт {new_contact}')
            self.messages.information(self, 'Успех', 'Контакт успешно добавлен.')

    # Слот приёма сообщений
    @pyqtSlot(str)
    def read_message(self, sender):
        if sender == self.current_chat:
            self.history_list_update()
        else:
            # Если пользователь в контактах:
            if self.db.check_contact(sender):
                # Запрос об открытии чата
                if self.messages.question(self,
                                          'Новое сообщение',
                                          f'Получено новое сообщение от {sender}, открыть чат с ним?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')
                # Раз нет,спрашиваем хотим ли добавить юзера в контакты.
                if self.messages.question(self,
                                          'Новое сообщение',
                                          f'Получено новое сообщение от {sender}.\n'
                                          f'Данного пользователя нет в вашем контакт-листе.\n'
                                          f'Добавить в контакты и открыть чат с ним?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.set_active_user()

    # Слот потери соединения
    # Выдаёт сообщение о ошибке и завершает работу приложения
    @pyqtSlot()
    def connection_lost(self):
        self.messages.warning(self, 'Сбой соединения', 'Потеряно соединение с сервером. ')
        self.close()

    def make_connection(self, trans_obj):
        trans_obj.signal_new_message.connect(self.read_message)
        trans_obj.signal_connection_lost.connect(self.connection_lost)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_ = MainWindow()
    sys.exit(app.exec_())

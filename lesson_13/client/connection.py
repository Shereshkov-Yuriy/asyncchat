import json
import sys
import time
import logging
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from PyQt5.QtCore import pyqtSignal, QObject

sys.path.append("../")
from lesson_13.constants import *
from lesson_13.utils import get_message, send_message

logger = logging.getLogger("client")
socket_lock = Lock()


class ClientConnection(Thread, QObject):
    signal_new_message = pyqtSignal(str)
    signal_connection_lost = pyqtSignal()

    def __init__(self, ip, port, username, db):
        Thread.__init__(self)
        QObject.__init__(self)

        self.ip = ip
        self.port = port
        self.username = username
        self.db = db
        self.connection = None
        self.connection_init()
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as e:
            if e.errno:
                logger.critical(f"Соединение с сервером разорвано.")
                sys.exit(1)
        except json.JSONDecodeError:
            logger.critical(f"Соединение с сервером разорвано.")
            sys.exit(1)
            # Флаг продолжения работы соединения.
        self.running = True

    def connection_init(self):
        self.connection = socket(AF_INET, SOCK_STREAM)
        self.connection.settimeout(5)

        # Соединяемся, 5 попыток соединения, флаг успеха ставим в True если удалось
        connected = False
        for i in range(5):
            logger.info(f'Попытка подключения №{i + 1}')
            try:
                self.connection.connect((self.ip, self.port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        # Если соединится не удалось - исключение
        if not connected:
            logger.critical('Не удалось установить соединение с сервером')
            sys.exit(1)

        logger.debug('Установлено соединение с сервером')

        try:
            with socket_lock:
                send_message(self.connection, self.create_presence())
                self.process_server_response(get_message(self.connection))
        except (OSError, ValueError, json.JSONDecodeError):
            logger.critical('Потеряно соединение с сервером!')
            sys.exit(1)

        logger.info('Соединение с сервером успешно установлено.')

    def create_presence(self):
        """Формирует presence-сообщение."""
        message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }
        logger.debug(f"Создано {PRESENCE}-сообщение для пользователя '{self.username}'.")
        return message

    def process_server_response(self, message):
        """Разбирает ответ сервера. Добавляет сообщение в БД."""
        logger.debug(f'Разбор сообщения от сервера: {message}')

        # Если это подтверждение чего-либо
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return "200: OK"
            elif message[RESPONSE] == 400:
                return f"400: {message[ERROR]}"
            else:
                logger.debug(f'Принят неизвестный код подтверждения {message[RESPONSE]}')

        # Если это сообщение от пользователя добавляем в базу, даём сигнал о новом сообщении
        elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message \
                and message[RECIPIENT] == self.username:
            logger.debug(f'Получено сообщение от пользователя {message[SENDER]}:{message[MESSAGE_TEXT]}')
            self.db.save_message(message[SENDER], "in", message[MESSAGE_TEXT])
            self.signal_new_message.emit(message[SENDER])

    def contacts_list_update(self):
        """Обновляет список контактов с сервера"""
        logger.debug(f'Запрос контакт листа для пользователся {self.username}')
        request = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        logger.debug(f'Сформирован запрос {request}')
        with socket_lock:
            send_message(self.connection, request)
            answer = get_message(self.connection)
        logger.debug(f'Получен ответ {answer}')
        if RESPONSE in answer and answer[RESPONSE] == 202:
            for contact in answer[DATA_AVAILABLE]:
                self.db.add_contact(contact)
        else:
            logger.error('Не удалось обновить список контактов.')

    def user_list_update(self):
        """Обновляет таюлицу известных пользователей"""
        logger.debug(f'Запрос списка известных пользователей {self.username}')
        request = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            send_message(self.connection, request)
            answer = get_message(self.connection)
        if RESPONSE in answer and answer[RESPONSE] == 202:
            self.db.add_users(answer[DATA_AVAILABLE])
        else:
            logger.error('Не удалось обновить список известных пользователей.')

    # Функция сообщающая на сервер о добавлении нового контакта
    def add_contact(self, contact):
        logger.debug(f'Создание контакта {contact}')
        request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.connection, request)
            self.process_server_response(get_message(self.connection))

    # Функция удаления клиента на сервере
    def del_contact(self, contact):
        logger.debug(f'Удаление контакта {contact}')
        request = {
            ACTION: DEL_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.connection, request)
            self.process_server_response(get_message(self.connection))

    def connection_shutdown(self):
        """Закрывает соедиение. Отправляет сообщение о выходе."""
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                send_message(self.connection, message)
            except OSError:
                pass
        logger.debug('Соединение завершает работу.')
        time.sleep(0.5)

    def send_message(self, to_user, message):
        """Отправляет сообщение через сервер"""
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            RECIPIENT: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')

        # Необходимо дождаться освобождения сокета для отправки сообщения
        with socket_lock:
            send_message(self.connection, message_dict)
            self.process_server_response(get_message(self.connection))
            logger.info(f'Отправлено сообщение для пользователя {to_user}')

    def run(self):
        logger.debug('Запущен процесс - приёмник собщений с сервера.')
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.connection.settimeout(0.5)
                    message = get_message(self.connection)
                except OSError as err:
                    if err.errno:
                        logger.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.signal_connection_lost.emit()
                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    logger.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.signal_connection_lost.emit()
                # Если сообщение получено, то вызываем функцию обработчик:
                else:
                    logger.debug(f'Принято сообщение с сервера: {message}')
                    self.process_server_response(message)
                finally:
                    self.connection.settimeout(5)

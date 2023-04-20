"""Основная программа сервера."""
import binascii
import hmac
import json
import logging
import os
import select
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

from common.constants import *
from common.decorators import login_required
from common.descriptors import Port
from common.utils import get_message, send_message

logger = logging.getLogger("server")


class ServerClass(Thread):
    """
    Основной класс сервера. Принимает содинения, словари - пакеты
    от клиентов, обрабатывает поступающие сообщения.
    Работает в качестве отдельного потока.
    """

    port = Port()

    def __init__(self, listening_host, listening_port, db):
        """Инициализирует класс сервера."""
        super().__init__()
        self.daemon = True
        self.host = listening_host
        self.port = listening_port
        self.db = db

        self.socket = None
        self.clients = []
        # {username: socket}
        self.names = {}
        self.listen_sockets = None
        # Флаг продолжения работы соединения.
        self.running = True

    def listen(self):
        """Создает и слушает сокет."""
        logger.info(
            f"Запуск сервера по адресу: {self.host}, " f"порт: {self.port}."
        )
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(0.4)
        self.socket.listen(MAX_CONNECTIONS)

    def run(self):
        """Основной цикл потока."""
        self.listen()

        while self.running:
            try:
                client, client_address = self.socket.accept()
            except OSError:
                pass  # Ошибка по таймауту
            else:
                logger.info(
                    f"Установлено соединение с клиентом: {client_address}"
                )
                client.settimeout(5)
                self.clients.append(client)

            wait = 8
            read_list = []
            # write_list = []
            # error_list = []
            try:
                read_list, self.listen_sockets, _ = select.select(
                    self.clients, self.clients, [], wait
                )
            except OSError:
                pass

            if read_list:
                for client in read_list:
                    try:
                        msg = get_message(client)
                        self.process_client_message(msg, client)
                    except (OSError, json.JSONDecodeError, TypeError) as error:
                        logger.debug(
                            "Возникло исключение клиента.", exc_info=error
                        )
                        self.remove_client(client)

    def remove_client(self, client):
        """Обрабатывает клиентов, с которыми прервана связь."""
        logger.info(f"Отключение клиента: '{client.getpeername()}'.")
        for name in self.names:
            if self.names[name] == client:
                self.db.user_logout(name)
                del self.names[name]
                break
        self.clients.remove(client)
        client.close()

    @login_required
    def process_client_message(self, message, client):
        """
        Разбирает сообщение клиента и проверяет на корректность.
        Отправляет ответ сервера, удаляет клиента или
        добавляет сообщение в очередь.
        """
        logger.debug(f"Разбор сообщения от клиента: {message}")
        # Если presence, то выполнить аутентификацию пользователя
        if (
            ACTION in message
            and message[ACTION] == PRESENCE
            and TIME in message
            and USER in message
        ):
            self.auth_user(message, client)
        # Если это сообщение, то отправить его получателю.
        elif (
            message[ACTION] == MESSAGE
            and RECIPIENT in message
            and SENDER in message
            and self.names[message[SENDER]] == client
        ):
            if message[RECIPIENT] in self.names:
                self.process_message(message)
                try:
                    send_message(client, RESPONSE_200)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = "Пользователь не зарегистрирован на сервере."
                try:
                    send_message(client, response)
                except OSError:
                    pass
            return
        # Удалить уходящего клиента из списка.
        elif (
            message[ACTION] == EXIT
            and ACCOUNT_NAME in message
            and self.names[message[ACCOUNT_NAME]] == client
        ):
            self.remove_client(client)
        # Запрос контактов пользователей
        elif (
            message[ACTION] == GET_CONTACTS
            and self.names[message[USER]] == client
        ):
            response = RESPONSE_202
            response[DATA_AVAILABLE] = self.db.get_contacts(message[USER])
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)
        # Запрос на добавление контакта
        elif (
            message[ACTION] == ADD_CONTACT
            and self.names[message[USER]] == client
        ):
            self.db.add_contact(message[USER], message[ACCOUNT_NAME])
            try:
                send_message(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)
        # Запрос на удаление контакта
        elif (
            message[ACTION] == DEL_CONTACT
            and self.names[message[USER]] == client
        ):
            self.db.del_contact(message[USER], message[ACCOUNT_NAME])
            try:
                send_message(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)
        # Если это запрос известных пользователей
        elif (
            message[ACTION] == USERS_REQUEST
            and self.names[message[ACCOUNT_NAME]] == client
        ):
            response = RESPONSE_202
            response[DATA_AVAILABLE] = [
                user[0] for user in self.db.users_list()
            ]
            try:
                send_message(client, response)
            except OSError:
                self.remove_client(client)
        # Иначе "Плохой запрос"
        else:
            try:
                send_message(client, RESPONSE_400)
            except OSError:
                self.remove_client(client)

    def auth_user(self, message, client):
        """Аутентифицирует пользователя."""
        logger.debug(f"Аутентификация для {message[USER]}")
        if message[USER][ACCOUNT_NAME] in self.names.keys():
            response = RESPONSE_400
            response[ERROR] = "Данный пользователь уже существует."
            try:
                logger.debug(f"Имя занято. Отправлено: {response}")
                send_message(client, response)
            except OSError:
                logger.debug("OSError")
            self.clients.remove(client)
            client.close()
        elif not self.db.check_user(message[USER][ACCOUNT_NAME]):
            response = RESPONSE_400
            response[ERROR] = "Пользователь не зарегистрирован."
            try:
                logger.debug(
                    f"Неизвестный пользователь. Отправлено: {response}"
                )
                send_message(client, response)
            except OSError:
                pass
            self.clients.remove(client)
            client.close()
        else:
            logger.debug("Имя принято. Проверка пароля.")
            message_auth = RESPONSE_511
            random_str = binascii.hexlify(os.urandom(64))
            message_auth[DATA_AUTH] = random_str.decode("ascii")
            # Создаём хэш пароля и связки с рандомной строкой,
            # сохраняем серверную версию ключа.
            hash_string = hmac.new(
                self.db.get_hash(message[USER][ACCOUNT_NAME]),
                random_str,
                "MD5",
            )
            digest = hash_string.digest()
            logger.debug(f"Auth message = {message_auth}")
            try:
                send_message(client, message_auth)
                answer = get_message(client)
            except OSError as error:
                logger.debug(
                    "Ошибка в аутентификационных данных:", exc_info=error
                )
                client.close()
                return
            client_digest = binascii.a2b_base64(answer[DATA_AUTH])
            # Если ответ клиента корректный, то сохраняем его
            # в список пользователей.
            if (
                RESPONSE in answer
                and answer[RESPONSE] == 511
                and hmac.compare_digest(digest, client_digest)
            ):
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                try:
                    send_message(client, RESPONSE_200)
                except OSError:
                    self.remove_client(message[USER][ACCOUNT_NAME])
                # добавляем пользователя в список активных
                self.db.user_login(
                    message[USER][ACCOUNT_NAME],
                    client_ip,
                    client_port,
                    client_digest,
                )
            else:
                response = RESPONSE_400
                response[ERROR] = "Неверный пароль."
                try:
                    send_message(client, response)
                except OSError:
                    pass
                self.clients.remove(client)
                client.close()

    def process_message(self, message):
        """Отправляет сообщения получателю."""
        if (
            message[RECIPIENT] in self.names
            and self.names[message[RECIPIENT]] in self.listen_sockets
        ):
            try:
                send_message(self.names[message[RECIPIENT]], message)
                logger.info(
                    f"Пользователю {message[RECIPIENT]} отправлено "
                    f"сообщение от пользователя {message[SENDER]}."
                )
            except OSError:
                self.remove_client(message[RECIPIENT])
        elif (
            message[RECIPIENT] in self.names
            and self.names[message[RECIPIENT]] not in self.listen_sockets
        ):
            logger.error(
                f"Связь с клиентом {message[RECIPIENT]} потеряна. "
                f"Соединение закрыто."
            )
            self.remove_client(self.names[message[RECIPIENT]])
        else:
            logger.error(
                f"Пользователь {message[RECIPIENT]} не найден, "
                f"отправка сообщения невозможна."
            )

    def service_update_lists(self):
        """Метод реализующий отправку сервисного сообщения 205 клиентам."""
        for client in self.names:
            try:
                send_message(self.names[client], RESPONSE_205)
            except OSError:
                self.remove_client(self.names[client])

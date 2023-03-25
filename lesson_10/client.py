import argparse
import json
import sys
import time
import logging
import log.client_log_config
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from constants import *
from utils import get_message, send_message
from decorators import Log
from metaclasses import ClientVerifier

logger = logging.getLogger("client")


class ClientSend(Thread, metaclass=ClientVerifier):
    def __init__(self, sock, sender):
        super().__init__()
        self.sock = sock
        self.sender = sender

    # Запрашивает сообщение, получателя и формирует словарь на отправку.
    def create_message(self):
        to_user = input("Кому отправить: ")
        message_text = input("Что отправить: ")
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.sender,
            RECIPIENT: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message_text,
        }
        logger.debug(f"Создано сообщение: {message_dict}.")
        return message_dict

    # Формирует сообщение о выходе.
    def create_exit(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.sender,
        }

    # Запрашивает команды отправителя и выполняет действия.
    def run(self):
        print("Отправка сообщений: 'send'. Выход: 'exit'.")
        while True:
            command = input("Введите команду: ")
            if command == "send":
                send_message(self.sock, self.create_message())
                logger.info("Отправлено сообщение.")
            elif command == "exit":
                send_message(self.sock, self.create_exit())
                self.sock.close()
                logger.info("Соединение завершено пользователем.")
                print("Всего доброго!\n")
                time.sleep(0.8)
                break
            else:
                print("Введите корректную команду: 'send' или 'exit'.")


class ClientRead(Thread, metaclass=ClientVerifier):
    def __init__(self, sock, recipient):
        super().__init__()
        self.sock = sock
        self.recipient = recipient

    # Обрабатывает полученные сообщения MESSAGE.
    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if (ACTION in message and message[ACTION] == MESSAGE
                        and RECIPIENT in message and message[RECIPIENT] == self.recipient):
                    print(f"\nПолучено сообщение от пользователя '{message[SENDER]}': '{message[MESSAGE_TEXT]}'.")
                    logger.info(
                        f"Получено сообщение от пользователя '{message[SENDER]}': '{message[MESSAGE_TEXT]}'.")
                else:
                    logger.error(f"Получено некорректное сообщение: '{message}'.")
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                time.sleep(2)
                logger.critical(f"Соединение с сервером разорвано.")
                break


@Log()
def create_presence(account_name="NoName"):
    """
    Формирует presence-сообщение.
    :param account_name:
    :return:
    """
    # {'action': 'presence', 'time': 123.123, 'user': {'account_name': 'NoName'}}
    message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.debug(f"Создано {PRESENCE}-сообщение для пользователя '{account_name}'.")
    return message


@Log()
def process_server_response(message):
    """
    Разбирает ответ сервера.
    :param message:
    :return:
    """
    logger.debug(f"Разбор ответа от сервера: {message}.")
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return "200: OK"
        return f"400: {message[ERROR]}"
    return ValueError


@Log()
def parse_cli_args():
    """
    Парсит аргументы коммандной строки.
    Если параметров нет, то используются значения по умолчанию.
    Пример строки:
    client.py 127.0.0.1 46464
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("address", default=IP_ADDRESS, nargs="?")
    parser.add_argument("port", default=PORT, type=int, nargs="?")
    parser.add_argument("-n", "--name", default=None, nargs="?")
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.address
    server_port = namespace.port
    client_name = namespace.name

    if server_port < 1024 or server_port > 65535:
        logger.error(f"Выбран неверный порт {server_port}, требуется из диапазона: 1024 - 65535.")
        sys.exit(1)

    if client_name is None:
        client_name = input("Введите свое имя: ")

    return server_address, server_port, client_name


def main():
    """Запуск приложения клиента."""
    server_address, server_port, client_name = parse_cli_args()
    print(f"Приложение клиента '{client_name}'.\n")

    logger.info(f"Запуск клиента с параметрами: "
                f"адрес сервера: {server_address}, порт сервера: {server_port}, имя клиента: {client_name}.")

    try:
        connection = socket(AF_INET, SOCK_STREAM)
        connection.connect((server_address, server_port))
        send_message(connection, create_presence(client_name))
        answer = process_server_response(get_message(connection))
        logger.info(f"Принят ответ сервера: '{answer}'.")
        print(f"Установлено соединение с сервером, ответ сервера: {answer}.\n")
    except (ValueError, json.JSONDecodeError):
        logger.error("Некорректное сообщение от сервера.")
        sys.exit(1)
    except ConnectionRefusedError:
        logger.critical(f"Подключение к серверу '{server_address}:{server_port}' не установлено,"
                        f"т.к. конечный компьютер отверг запрос на подключение.")
        sys.exit(1)
    else:
        monitor_read = ClientRead(connection, client_name)
        monitor_read.daemon = True
        monitor_read.start()

        monitor_send = ClientSend(connection, client_name)
        monitor_send.daemon = True
        monitor_send.start()

        logger.debug("Старт потоков.")

        while True:
            time.sleep(1)
            if monitor_send.is_alive() and monitor_read.is_alive():
                continue
            break


if __name__ == "__main__":
    main()

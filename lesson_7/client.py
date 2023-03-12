import json
import sys
import time as t
import logging
import log.client_log_config
from socket import socket, AF_INET, SOCK_STREAM

from constants import ACTION, ACCOUNT_NAME, ERROR, IP_ADDRESS,\
    MESSAGE, MESSAGE_TEXT, PORT, PRESENCE, RESPONSE, TIME, USER
from utils import get_message, send_message
from decorators import Log

logger = logging.getLogger("client")


@Log()
def create_presence(account_name="User"):
    """
    Формирует presence-сообщение.
    :param account_name:
    :return:
    """
    # {'action': 'presence', 'time': 1677341493.1306949, 'user': {'account_name': 'User'}}
    message = {
        ACTION: PRESENCE,
        TIME: t.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.debug(f"Создано {PRESENCE}-сообщение для пользователя '{account_name}'")
    return message


@Log()
def create_message(msg, account_name="User"):
    """
    Формирует сообщение.
    :param msg:
    :param account_name:
    :return:
    """
    message = {
        ACTION: MESSAGE,
        TIME: t.time(),
        USER: {
            ACCOUNT_NAME: account_name
        },
        MESSAGE_TEXT: msg
    }
    logger.debug(f"Создано {MESSAGE}-сообщение для пользователя '{account_name}'")
    return message


@Log()
def parse_server_response(message):
    """
    Разбирает сообщение сервера.
    :param message:
    :return:
    """
    logger.debug(f"Разбор сообщения от сервера: {message}")
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return "200: OK"
        return f"400: {message[ERROR]}"
    return ValueError


def main():
    """
    Проверка параметров командной строки.
    Если параметров нет, то используются значения по умолчанию.
    Пример строки:
    client.py 127.0.0.1 46464
    :return:
    """
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = IP_ADDRESS
        server_port = PORT
        logger.info("Установлены параметры по умолчанию: "
                    f"адрес сервера: {server_address}, порт: {server_port}.")
    except ValueError:
        logger.error(f"Выбран неверный порт {server_port}, требуется из диапазона: 1024 - 65535.")
        sys.exit(1)

    logger.info(f"Запуск клиента с параметрами: "
                f"адрес сервера: {server_address}, порт: {server_port}.")

    try:
        connection = socket(AF_INET, SOCK_STREAM)
        connection.connect((server_address, server_port))
        message_to_server = create_presence()
        send_message(connection, message_to_server)
        answer = parse_server_response(get_message(connection))
        logger.info(f"Принят ответ сервера: '{answer}'")
        print(f"Установлено соединение с сервером, ответ сервера: {answer}.")
    except (ValueError, json.JSONDecodeError):
        logger.error("Некорректное сообщение от сервера.")
        sys.exit(1)
    except ConnectionRefusedError:
        logger.critical(f"Подключение к серверу '{server_address}:{server_port}' не установлено,"
                        f"т.к. конечный компьютер отверг запрос на подключение.")
        sys.exit(1)
    else:
        print("Отправка сообщений. Для выхода: 'exit'.")
        while True:
            msg = input("Введите ваше сообщение: ")
            if msg == "exit":
                connection.close()
                logger.info("Соединение завершено пользователем.")
                print("Всего доброго!")
                sys.exit(0)
            send_message(connection, create_message(msg))


if __name__ == "__main__":
    main()

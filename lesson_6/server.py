import json
import socket as s
import sys
import logging
import log.server_log_config

from constants import (ACTION, ACCOUNT_NAME, ERROR, MAX_CONNECTIONS,
                       PORT, PRESENCE, RESPONSE, TIME, USER)
from utils import get_message, send_message
from decorators import Log

logger = logging.getLogger("server")


@Log()
def parse_client_response(message):
    """
    Разбирает сообщение клиента и проверяет на корректность.
    :param message:
    :return:
    """
    logger.debug(f"Разбор сообщения от клиента: {message}")
    if (ACTION in message and message[ACTION] == PRESENCE and TIME in message
            and USER in message and message[USER][ACCOUNT_NAME] == "User"):
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: "Bad request"
    }


def main():
    """
    Проверка параметров командной строки.
    Если параметров нет, то используются значения по умолчанию.
    Пример строки:
    server.py -a 127.0.0.1 -p 46464
    :return:
    """
    logger.debug("Start App.")
    # Проверить параметр -а и ip-адрес
    try:
        if "-a" in sys.argv:
            idx = sys.argv.index("-a")
            listening_address = sys.argv[idx + 1]
        else:
            listening_address = ""
    except IndexError:
        logger.critical("После параметра '-a' не указан ip-адрес.")
        sys.exit(1)

    # Проверить параметр -р и порт
    try:
        if "-p" in sys.argv:
            idx = sys.argv.index("-p")
            listening_port = int(sys.argv[idx + 1])
        else:
            listening_port = PORT
        if listening_port < 1024 or listening_port > 65535:
            raise ValueError
    except IndexError:
        logger.critical("После параметра '-p' не указан номер порта.")
        sys.exit(1)
    except ValueError:
        logger.error(f"Выбран неверный порт {listening_port}, требуется из диапазона: 1024 - 65535.")
        sys.exit(1)

    logger.info(f"Запуск сервера по адресу: {listening_address}, порт: {listening_port}.")

    connection = s.socket(s.AF_INET, s.SOCK_STREAM)
    connection.bind((listening_address, listening_port))
    connection.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = connection.accept()
        logger.info(f"Установлено соединение с клиентом: {client_address}")
        try:
            message_from_client = get_message(client)
            logger.debug(f"Получено сообщение: {message_from_client}")
            # {'action': 'presence', 'time': 1677344644.1893244, 'user': {'account_name': 'User'}}
            response = parse_client_response(message_from_client)
            logger.info(f"Создан ответ клиенту: {response}")
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            logger.error("Некорректное сообщение от клиента.")
            client.close()


if __name__ == "__main__":
    main()

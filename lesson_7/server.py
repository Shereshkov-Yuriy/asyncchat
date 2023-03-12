import json
import sys
import logging
import log.server_log_config
import select
from socket import socket, AF_INET, SOCK_STREAM

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
    if (ACTION in message and TIME in message and USER in message
            and message[USER][ACCOUNT_NAME] == "User"):
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: "Bad request"
    }


def read_requests(read_clients, all_clients):
    """
    Чтение запросов из списка клиентов.
    Возвращает словарь ответов для сервера вида {socket: request}
    :param read_clients:
    :param all_clients:
    :return:
    """
    responses = {}
    for client in read_clients:
        try:
            message_from_client = get_message(client)
            logger.debug(f"Получено сообщение: {message_from_client}")
            # {'action': 'presence', 'time': 1677344644.1893244, 'user': {'account_name': 'User'}}
            responses[client] = message_from_client
        except:
            logger.info(f"Клиент {client.getpeername()} отключился.")
            all_clients.remove(client)
    return responses


@Log()
def write_responses(requests, write_clients, all_clients):
    """
    Эхо-ответ сервера клиентам, от которых были запросы.
    :param requests:
    :param write_clients:
    :param all_clients:
    :return:
    """
    for client in write_clients:
        if client in requests:
            try:
                # Подготовить и отправить ответ сервера
                response = parse_client_response(requests[client])
                logger.info(f"Создан ответ клиенту: {response}")
                send_message(client, response)
            except:
                # Сокет недоступен, клиент отключился
                logger.info(f"Клиент {client.getpeername()} отключился.")
                client.close()
                all_clients.remove(client)


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

    connection = socket(AF_INET, SOCK_STREAM)
    connection.bind((listening_address, listening_port))
    connection.listen(MAX_CONNECTIONS)
    connection.settimeout(0.4)

    clients = []

    while True:
        try:
            client, client_address = connection.accept()
        except OSError:
            pass  # Ошибка по таймауту
        else:
            logger.info(f"Установлено соединение с клиентом: {client_address}")
            clients.append(client)
        finally:
            wait = 10
            read_list = []
            write_list = []
            error_list = []
            try:
                read_list, write_list, error_list = select.select(clients, clients, [], wait)
            except:
                pass

            # Сохранить запросы клиентов
            requests = read_requests(read_list, clients)
            if requests:
                # Выполнить отправку ответов клиентам
                write_responses(requests, write_list, clients)


if __name__ == "__main__":
    main()

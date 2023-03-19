import argparse
import sys
import logging
import log.server_log_config
import select
from socket import socket, AF_INET, SOCK_STREAM

from constants import *
from utils import get_message, send_message
from decorators import Log

logger = logging.getLogger("server")


@Log()
def process_client_message(message, messages, client, clients, names):
    """
    Разбирает сообщение клиента и проверяет на корректность.
    Отправляет ответ сервера, удаляет клиента или добавляет сообщение в очередь.
    :param message:
    :param messages:
    :param client:
    :param clients:
    :param names:
    :return:
    """
    logger.debug(f"Разбор сообщения от клиента: {message}")
    if (ACTION in message and message[ACTION] == PRESENCE
            and TIME in message and USER in message):
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = "Данный пользователь уже существует."
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    # Сообщения добавить в очередь.
    elif (ACTION in message and message[ACTION] == MESSAGE and RECIPIENT in message
          and TIME in message and SENDER in message and MESSAGE_TEXT in message):
        messages.append(message)
        return
    # Удалить уходящего клиента из списка.
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        send_message(client, RESPONSE_400)
        return


@Log()
def process_message(message, names, sockets):
    """
    Отправляет сообщения получателю. Ничего не возвращает.
    :param message:
    :param names:
    :param sockets:
    :return:
    """
    if message[RECIPIENT] in names and names[message[RECIPIENT]] in sockets:
        send_message(names[message[RECIPIENT]], message)
        logger.info(f"Пользователю {message[RECIPIENT]} отправлено сообщение от пользователя {message[SENDER]}.")
    elif message[RECIPIENT] in names and names[message[RECIPIENT]] not in sockets:
        raise ConnectionError
    else:
        logger.error(f"Пользователь {message[RECIPIENT]} не найден, отправка сообщения невозможна.")


@Log()
def parse_cli_args():
    """
    Парсит аргументы коммандной строки.
    Если параметров нет, то используются значения по умолчанию.
    Пример строки:
    server.py -a 127.0.0.1 -p 46464
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", default="", nargs="?")
    parser.add_argument("-p", default=PORT, type=int, nargs="?")
    namespace = parser.parse_args(sys.argv[1:])
    listening_address = namespace.a
    listening_port = namespace.p

    if listening_port < 1024 or listening_port > 65535:
        logger.error(f"Выбран неверный порт {listening_port}, требуется из диапазона: 1024 - 65535.")
        sys.exit(1)

    return listening_address, listening_port


def main():
    """Запуск приложения сервера."""
    logger.debug("Start App.")
    listening_address, listening_port = parse_cli_args()

    logger.info(f"Запуск сервера по адресу: {listening_address}, порт: {listening_port}.")

    connection = socket(AF_INET, SOCK_STREAM)
    connection.bind((listening_address, listening_port))
    connection.listen(MAX_CONNECTIONS)
    connection.settimeout(0.4)

    clients = []
    messages = []
    # {username: socket}
    names = {}

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
            except OSError:
                pass

            if read_list:
                for client in read_list:
                    try:
                        process_client_message(get_message(client), messages, client, clients, names)
                    except Exception:
                        logger.info(f"Клиент '{client.getpeername()}' отключился.")
                        clients.remove(client)

            for msg in messages:
                try:
                    process_message(msg, names, write_list)
                except Exception:
                    logger.info(f"Связь с клиентом '{msg[RECIPIENT]}' потеряна.")
                    clients.remove(names[msg[RECIPIENT]])
                    del names[msg[RECIPIENT]]
            messages.clear()


if __name__ == "__main__":
    main()

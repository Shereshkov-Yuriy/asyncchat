import argparse
import sys
import logging
import log.server_log_config
import select
import socket

from constants import *
from utils import get_message, send_message
from decorators import Log
from descriptors import Port
from metaclasses import ServerVerifier

logger = logging.getLogger("server")


class Server(metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listening_host, listening_port):
        self.host = listening_host
        self.port = listening_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.messages = []
        # {username: socket}
        self.names = {}

    def listen(self):
        logger.info(f"Запуск сервера по адресу: {self.host}, порт: {self.port}.")
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(0.4)
        self.socket.listen(MAX_CONNECTIONS)

    def run(self):
        self.listen()

        while True:
            try:
                client, client_address = self.socket.accept()
            except OSError:
                pass  # Ошибка по таймауту
            else:
                logger.info(f"Установлено соединение с клиентом: {client_address}")
                self.clients.append(client)
            finally:
                wait = 8
                read_list = []
                write_list = []
                # error_list = []
                try:
                    read_list, write_list, error_list = select.select(self.clients, self.clients, [], wait)
                except OSError:
                    pass

                if read_list:
                    for client in read_list:
                        try:
                            self.process_client_message(get_message(client), client)
                        except OSError:
                            logger.info(f"Клиент '{client.getpeername()}' отключился.")
                            self.clients.remove(client)

                for msg in self.messages:
                    try:
                        self.process_message(msg, write_list)
                    except OSError:
                        logger.info(f"Связь с клиентом '{msg[RECIPIENT]}' потеряна.")
                        self.clients.remove(self.names[msg[RECIPIENT]])
                        del self.names[msg[RECIPIENT]]
                self.messages.clear()

    def process_client_message(self, message, client):
        """
        Разбирает сообщение клиента и проверяет на корректность.
        Отправляет ответ сервера, удаляет клиента или добавляет сообщение в очередь.
        :param message:
        :param client:
        :return:
        """
        logger.debug(f"Разбор сообщения от клиента: {message}")
        if (ACTION in message and message[ACTION] == PRESENCE
                and TIME in message and USER in message):
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = "Данный пользователь уже существует."
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Сообщения добавить в очередь.
        elif (ACTION in message and message[ACTION] == MESSAGE and RECIPIENT in message
              and TIME in message and SENDER in message and MESSAGE_TEXT in message):
            self.messages.append(message)
            return
        # Удалить уходящего клиента из списка.
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        else:
            send_message(client, RESPONSE_400)
            return

    def process_message(self, message, sockets):
        """
        Отправляет сообщения получателю. Ничего не возвращает.
        :param message:
        :param sockets:
        :return:
        """
        if message[RECIPIENT] in self.names and self.names[message[RECIPIENT]] in sockets:
            send_message(self.names[message[RECIPIENT]], message)
            logger.info(f"Пользователю {message[RECIPIENT]} отправлено сообщение от пользователя {message[SENDER]}.")
        elif message[RECIPIENT] in self.names and self.names[message[RECIPIENT]] not in sockets:
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
    listening_host = namespace.a
    listening_port = namespace.p

    return listening_host, listening_port


def main():
    """Запуск приложения сервера."""
    logger.debug("Start App.")
    host, port = parse_cli_args()
    server = Server(host, port)
    server.run()


if __name__ == "__main__":
    main()

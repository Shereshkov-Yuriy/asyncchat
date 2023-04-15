import argparse
import json
import sys
import logging
from PyQt5.QtWidgets import QApplication

from constants import *
from decorators import Log
from client.client_db import ClientDatabase
from client.connection import ClientConnection
from client.client_gui import MainWindow
from client.start_dialog import UserNameDialog

logger = logging.getLogger("client")


@Log()
def parse_cli_args():
    """
    Парсит аргументы коммандной строки.
    Если параметров нет, то используются значения по умолчанию.
    Пример строки:
    client.py 127.0.0.1 7777
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

    if server_port not in range(1024, 65536):
        logger.error(f"Выбран неверный порт {server_port}, требуется из диапазона: 1024 - 65535.")
        sys.exit(1)

    return server_address, server_port, client_name


def get_client_name(name, app):
    start_dialog = UserNameDialog()
    app.exec_()

    if start_dialog.ok_pressed:
        name = start_dialog.client_name.text()
        del start_dialog
    else:
        sys.exit(0)

    return name


def main():
    """Запуск приложения клиента."""
    logger.debug("Start Client App.")
    server_host, server_port, client_name = parse_cli_args()
    client_app = QApplication(sys.argv)

    if client_name is None:
        client_name = get_client_name(client_name, client_app)

    logger.info(f"Запуск клиента с параметрами: адрес сервера: {server_host}, "
                f"порт сервера: {server_port}, имя клиента: {client_name}.")

    db = ClientDatabase(client_name)

    try:
        connection = ClientConnection(server_host, server_port, client_name, db)
    except (ValueError, json.JSONDecodeError):
        logger.error("Некорректное сообщение от сервера.")
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(f"Подключение к серверу '{server_host}:{server_port}' не установлено,"
                        f"т.к. конечный компьютер отверг запрос на подключение.")
        sys.exit(1)
    else:
        connection.daemon = True
        connection.start()

    main_ = MainWindow(connection, db)
    main_.make_connection(connection)
    main_.setWindowTitle(f"Приложение клиента '{client_name}'.")
    client_app.exec_()

    connection.connection_shutdown()
    connection.join()


if __name__ == "__main__":
    main()

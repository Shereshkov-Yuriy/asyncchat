"""Модуль запускает приложение клиента."""
import argparse
import logging
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from client.client_db import ClientDatabase
from client.client_gui import MainWindow
from client.connection import ClientConnection
from client.start_dialog import UserNameDialog
from common.constants import IP_ADDRESS, PORT
from common.decorators import Log
from common.errors import ServerError

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
    parser.add_argument("-p", "--password", default="", nargs="?")
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.address
    server_port = namespace.port
    client_name = namespace.name
    client_password = namespace.password

    if server_port not in range(1024, 65536):
        logger.error(
            f"Выбран неверный порт {server_port}, "
            f"требуется из диапазона: 1024 - 65535."
        )
        sys.exit(1)

    return server_address, server_port, client_name, client_password


def main():
    """Запуск приложения клиента."""
    logger.debug("Start Client App.")
    server_host, server_port, client_name, client_passwd = parse_cli_args()
    logger.debug("Аргументы загружены.")
    client_app = QApplication(sys.argv)

    start_dialog = UserNameDialog()
    if not client_name or not client_passwd:
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_passwd = start_dialog.client_passwd.text()
            logger.debug(
                f"Using USERNAME = {client_name}, PASSWD = {client_passwd}."
            )
        else:
            sys.exit(0)

    logger.info(
        f"Запущен клиент с параметрами: адрес сервера: {server_host}, "
        f"порт сервера: {server_port}, имя клиента: {client_name}."
    )

    client_db = ClientDatabase(client_name)

    try:
        connection = ClientConnection(
            server_host, server_port, client_name, client_db, client_passwd
        )
        logger.debug("Соединение с сервером установлено.")
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, "Ошибка сервера", error.text)
        sys.exit(1)
    connection.daemon = True
    connection.start()

    del start_dialog

    main_ = MainWindow(connection, client_db)
    main_.make_connection(connection)
    main_.setWindowTitle(f"Приложение клиента '{client_name}'.")
    client_app.exec_()

    connection.connection_shutdown()
    connection.join()


if __name__ == "__main__":
    main()

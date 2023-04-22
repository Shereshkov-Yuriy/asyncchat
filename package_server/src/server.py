"""Модуль запускает приложение сервера."""
import argparse
import logging
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from common.constants import PORT
from common.decorators import Log
from server.core import ServerClass
from server.server_db import ServerStorage
from server.server_gui import MainWindow

logger = logging.getLogger("server")


@Log()
def parse_cli_args():
    """
    Парсит аргументы коммандной строки.
    Если параметров нет, то используются значения по умолчанию.
    Пример строки:
    server.py -a 127.0.0.1 -p 7777
    :return:
    """
    logger.debug(
        f"Инициализация парсера аргументов коммандной строки: {sys.argv}"
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", default="", nargs="?")
    parser.add_argument("-p", default=PORT, type=int, nargs="?")
    namespace = parser.parse_args(sys.argv[1:])
    listening_host = namespace.a
    listening_port = namespace.p
    logger.debug("Аргументы успешно загружены.")
    return listening_host, listening_port


def main():
    """Запуск приложения сервера."""
    logger.debug("Start Server App.")
    host, port = parse_cli_args()
    server_db = ServerStorage()
    server_app = ServerClass(host, port, server_db)
    server_app.start()

    # Создать графическое приложение.
    server_gui = QApplication(sys.argv)
    server_gui.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    main_win = MainWindow(server_db, server_app)
    main_win.show()
    sys.exit(server_gui.exec_())


if __name__ == "__main__":
    main()

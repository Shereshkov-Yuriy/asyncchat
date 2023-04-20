import argparse
import logging
import sys
import logs.server.server_log_config
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from common.constants import *
from common.decorators import Log
from server.core import Server
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
    logger.debug(f"Инициализация парсера аргументов коммандной строки: {sys.argv}")
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
    db = ServerStorage()
    server = Server(host, port, db)
    server.start()

    # Создать графическое приложение.
    server_app = QApplication(sys.argv)
    server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
    main_win = MainWindow(db, server)
    server_app.exec_()

    server.running = False


if __name__ == "__main__":
    main()

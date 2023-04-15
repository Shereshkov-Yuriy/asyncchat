"""Конфигуратор логгера сервера"""
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from common.constants import LOG_FILE

log_file = LOG_FILE / "server" / "server.log"

logger = logging.getLogger("server")
logger.propagate = False

formatter = logging.Formatter(
    "%(asctime)-24s :: %(levelname)-10s :: %(module)-20s -- %(message)s")

file_handler = TimedRotatingFileHandler(log_file, when="midnight",
                                        encoding="utf-8")
file_handler.setFormatter(formatter)
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARNING)
console.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logger.info("Информация!")
    logger.debug("Отладочная информация!")
    logger.warning("Внимание!")
    logger.error("Ошибка!")
    logger.critical("Критическая ошибка!")

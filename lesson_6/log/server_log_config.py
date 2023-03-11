"""Конфигуратор логгера сервера"""
import logging
import logging.handlers as lh
import sys
import os

sys.path.append(os.path.join(os.getcwd(), ".."))
path = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(path, "server.log")

logger = logging.getLogger("server")
logger.propagate = False

formatter = logging.Formatter("%(asctime)-24s :: %(levelname)-10s :: %(module)-20s -- %(message)s")

file_handler = lh.TimedRotatingFileHandler(log_file, when="midnight", encoding="utf-8")
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

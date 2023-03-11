"""Реализация декоратора"""
import inspect
import logging
import sys
from functools import wraps
import log.server_log_config
import log.client_log_config

if sys.argv[0].find("client") == -1:
    logger = logging.getLogger("server")
else:
    logger = logging.getLogger("client")


class Log:
    """
    Декоратор фиксирует обращение к декорируемой функции.
    Сохраняет ее имя и аргументы.
    Фиксирует функцию, из которой вызвана декорируемая.
    """

    def __call__(self, func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            logger.debug(f"Обращение к функции {func.__name__} с параметрами: ({args}, {kwargs}). "
                         f"Вызов из функции {inspect.stack()[1][3]}.")
            return result

        return _wrapper

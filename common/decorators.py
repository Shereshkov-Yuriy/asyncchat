"""Реализация декоратора"""
import inspect
import logging
import sys
from functools import wraps
from socket import socket

sys.path.append("../")

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


def login_required(func):
    """
    Декоратор, проверяющий авторизованность пользователя на сервере
    для выполнения той или иной функции.
    Если клиент не авторизован, генерирует исключение TypeError.
    """

    def checker(*args, **kwargs):
        # проверяем, что первый аргумент - экземпляр Server
        from server.core import Server
        from common.constants import ACTION, PRESENCE
        if isinstance(args[0], Server):
            found = False
            for arg in args:
                if isinstance(arg, socket):
                    # Проверяем, что данный сокет есть в списке names класса
                    # MessageProcessor
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            # Теперь надо проверить, что передаваемые аргументы не presence
            # сообщение. Если presense, то разрешаем
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            # Если не не авторизован и не сообщение начала авторизации, то
            # вызываем исключение.
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker

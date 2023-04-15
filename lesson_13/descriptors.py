import sys
import logging

logger = logging.getLogger("server")


class Port:
    def __set__(self, instance, value):
        if value not in range(1024, 65536):
            logger.error(f"Выбран неверный порт {value}, требуется из диапазона: 1024 - 65535.")
            sys.exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name

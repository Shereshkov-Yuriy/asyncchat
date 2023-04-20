"""Утилиты для приема и отправки сообщений"""
import json
import sys

from common.constants import *
from common.decorators import Log

sys.path.append("../")


@Log()
def send_message(sock, message):
    """
    Кодирует и отправляет сообщение.
    :param sock:
    :param message:
    :return:
    """
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    sock.send(encoded_message)


@Log()
def get_message(client):
    """
    Принимает и декодирует сообщение. Проверяет типы.
    :param client:
    :return:
    """
    received_package = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(received_package, bytes):
        decode_package = received_package.decode(ENCODING)
        response = json.loads(decode_package)
        if isinstance(response, dict):
            return response
        raise TypeError
    raise TypeError

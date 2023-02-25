"""Утилиты для приема и отправки сообщений"""

import json
from constants import MAX_PACKAGE_LENGTH, ENCODING


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


def get_message(client):
    """
    Принимает и декодирует сообщение.
    Если что-то не то, то выдаст ошибку ValueError.
    :param client:
    :return:
    """
    received_package = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(received_package, bytes):
        decode_package = received_package.decode(ENCODING)
        response = json.loads(decode_package)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError

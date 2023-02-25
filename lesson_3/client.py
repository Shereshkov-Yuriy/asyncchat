import json
import socket as s
import sys
import time as t

from constants import (ACTION, ACCOUNT_NAME, ERROR, IP_ADDRESS,
                       PORT, PRESENCE, RESPONSE, TIME, USER)
from utils import get_message, send_message


def create_presence(account_name="User"):
    """
    Формирует presence-сообщение.
    :param account_name:
    :return:
    """
    # {'action': 'presence', 'time': 1677341493.1306949, 'user': {'account_name': 'User'}}
    msg = {
        ACTION: PRESENCE,
        TIME: t.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return msg


def parse_server_response(message):
    """
    Разбирает сообщение сервера.
    :param message:
    :return:
    """
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return "200: OK"
        return f"400: {message[ERROR]}"
    return ValueError


def main():
    """
    Проверка параметров командной строки.
    Если параметров нет, то используются значения по умолчанию.
    Пример строки:
    client.py 127.0.0.1 46464
    :return:
    """
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = IP_ADDRESS
        server_port = PORT
    except ValueError:
        print("Доступный диапазон портов: 1024 - 65535")
        sys.exit(1)

    connection = s.socket(s.AF_INET, s.SOCK_STREAM)
    connection.connect((server_address, server_port))
    message_to_server = create_presence()
    send_message(connection, message_to_server)
    try:
        answer = parse_server_response(get_message(connection))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print("Некорректное сообщение от сервера.")


if __name__ == "__main__":
    main()

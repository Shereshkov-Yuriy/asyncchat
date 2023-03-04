"""Unit-тесты утилит"""

import sys
import os
import unittest
import json

sys.path.append(os.path.join(os.getcwd(), ".."))

from lesson_4.constants import (RESPONSE, ERROR, USER, ACCOUNT_NAME,
                                TIME, ACTION, PRESENCE, ENCODING)
from lesson_4.utils import get_message, send_message


class TestSocket:
    """
    Тестовый класс для тестирования отправки и получения сообщения,
    при создании принимает словарь
    """

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        """
        Тестовая функция отправки, корретно  кодирует сообщение,
        а так-же сохраняет то, что должно быть отправлено в сокет.
        message_to_send - то, что отправляется в сокет
        :param message_to_send:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        # закодировать сообщение
        self.encoded_message = json_test_message.encode(ENCODING)
        # сохранить то, что должно быть отправлено в сокет
        self.received_message = message_to_send

    def recv(self, max_len):
        """
        Получает данные из сокета.
        :param max_len:
        :return:
        """
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class Tests(unittest.TestCase):
    """
    Тестовый класс, выполняющий тестирование.
    """
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 132456.123456,
        USER: {
            ACCOUNT_NAME: "Test"
        }
    }
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_err = {
        RESPONSE: 400,
        ERROR: "Bad request"
    }

    def test_send_message(self):
        """
        Тестирует корректность работы фукции отправки,
        создает тестовый сокет и проверяет корректность отправки словаря
        :return:
        """
        # экземпляр тестового словаря, хранит тестовый словарь
        test_socket = TestSocket(self.test_dict_send)
        # вызов тестируемой функции, результаты будут сохранены в тестовом сокете
        send_message(test_socket, self.test_dict_send)
        # проверка корретности кодирования словаря
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)
        # дополнительно, проверка генерации исключения, если на входе не словарь.
        with self.assertRaises(Exception):
            send_message(test_socket, test_socket)

    def test_get_message(self):
        """
        Тест функции получения сообщения
        :return:
        """
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)
        # тест корректной расшифровки корректного словаря
        self.assertEqual(get_message(test_sock_ok), self.test_dict_recv_ok)
        # тест корректной расшифровки ошибочного словаря
        self.assertEqual(get_message(test_sock_err), self.test_dict_recv_err)


if __name__ == "__main__":
    unittest.main()

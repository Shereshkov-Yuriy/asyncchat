"""Unit-тесты сервера"""

import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))

from lesson_4.constants import (RESPONSE, ERROR, USER, ACCOUNT_NAME,
                                TIME, ACTION, PRESENCE)
from lesson_4.server import parse_client_response


class TestServer(unittest.TestCase):
    """Тестовый класс для тестирования функции разбора сообщения"""

    err_dict = {
        RESPONSE: 400,
        ERROR: "Bad request"
    }
    ok_dict = {RESPONSE: 200}

    def test_no_action(self):
        """Ошибка, если нет действия"""
        self.assertEqual(parse_client_response(
            {TIME: 1.1, USER: {ACCOUNT_NAME: "User"}}), self.err_dict)

    def test_unknown_action(self):
        """Ошибка, если неизвестное действие"""
        self.assertEqual(parse_client_response(
            {ACTION: "unknown", TIME: 1.1, USER: {ACCOUNT_NAME: "User"}}), self.err_dict)

    def test_no_time(self):
        """Ошибка, если  запрос не содержит времени"""
        self.assertEqual(parse_client_response(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: "User"}}), self.err_dict)

    def test_no_user(self):
        """Ошибка, если не передан пользователь"""
        self.assertEqual(parse_client_response(
            {ACTION: PRESENCE, TIME: 1.1}), self.err_dict)

    def test_unknown_user(self):
        """Ошибка, если имя пользователя неверно"""
        self.assertEqual(parse_client_response(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: "NotUser"}}), self.err_dict)

    def test_ok_check(self):
        """Корректный запрос"""
        self.assertEqual(parse_client_response(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: "User"}}), self.ok_dict)


if __name__ == "__main__":
    unittest.main()

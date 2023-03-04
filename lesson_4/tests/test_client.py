"""Unit-тесты клиента"""

import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))

from lesson_4.constants import (RESPONSE, ERROR, USER, ACCOUNT_NAME,
                                TIME, ACTION, PRESENCE)
from lesson_4.client import create_presence, parse_server_response


class TestClass(unittest.TestCase):
    """Тестовый класс"""

    def test_def_create_presence(self):
        """Тест коректного запроса. Время задано вручную."""
        test = create_presence()
        test[TIME] = 123456.123456
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 123456.123456, USER: {ACCOUNT_NAME: "User"}})

    def test_answer_200(self):
        """Тест корректного разбора ответа 200"""
        self.assertEqual(parse_server_response({RESPONSE: 200}), "200: OK")

    def test_answer_400(self):
        """Тест корректного разбора ответа 400"""
        self.assertEqual(parse_server_response({RESPONSE: 400, ERROR: "Bad request"}), "400: Bad request")

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(ValueError, parse_server_response, {ERROR: "Bad request"})


if __name__ == "__main__":
    unittest.main()

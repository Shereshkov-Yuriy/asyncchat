Server module
=================================================

Серверный модуль мессенджера. Обрабатывает словари - сообщения, хранит публичные ключи клиентов.

Использование

Модуль подерживает аргементы командной стороки:

1. -p - Порт на котором принимаются соединения
2. -a - Адрес с которого принимаются соединения.

Примеры использования:

``python server.py -p 8080``

*Запуск сервера на порту 8080*

``python server.py -a localhost``

*Запуск сервера принимающего только соединения с localhost*

server.py
~~~~~~~~~

Запускаемый модуль,содержит парсер аргументов командной строки и функционал инициализации приложения.

server. **parse_cli_args** ()
    Парсер аргументов командной строки, возвращает кортеж из 2 элементов:

	* адрес с которого принимать соединения
	* порт

core.py
~~~~~~~~~~~

.. autoclass:: server.core.ServerClass
	:members:

server_db.py
~~~~~~~~~~~

.. autoclass:: server.server_db.ServerStorage
	:members:

server_gui.py
~~~~~~~~~~~~~~

.. autoclass:: server.server_gui.MainWindow
	:members:

add_user.py
~~~~~~~~~~~

.. autoclass:: server.add_user.RegisterUser
	:members:

del_user.py
~~~~~~~~~~~~~~

.. autoclass:: server.del_user.DelUserDialog
	:members:

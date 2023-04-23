Client module documentation
=================================================

Клиентское приложение для обмена сообщениями. Поддерживает
отправку сообщений пользователям которые находятся в сети.

Поддерживает аргументы коммандной строки:

``python client.py {имя сервера} {порт} -n или --name {имя пользователя} -p или -password {пароль}``

1. {имя сервера} - адрес сервера сообщений.
2. {порт} - порт по которому принимаются подключения
3. -n или --name - имя пользователя с которым произойдёт вход в систему.
4. -p или --password - пароль пользователя.

Все опции командной строки являются необязательными, но имя пользователя и пароль необходимо использовать в паре.

Примеры использования:

* ``python client.py``

*Запуск приложения с параметрами по умолчанию.*

* ``python client.py ip_address some_port``

*Запуск приложения с указанием подключаться к серверу по адресу ip_address:port*

* ``python -n test1 -p 123``

*Запуск приложения с пользователем test1 и паролем 123*

* ``python client.py ip_address some_port -n test1 -p 123``

*Запуск приложения с пользователем test1 и паролем 123 и указанием подключаться к серверу по адресу ip_address:port*

client.py
~~~~~~~~~

Запускаемый модуль,содержит парсер аргументов командной строки и функционал инициализации приложения.

client. **parse_cli_args** ()
    Парсер аргументов командной строки, возвращает кортеж из 4 элементов:
    
	* адрес сервера
	* порт
	* имя пользователя
	* пароль
	
    Выполняет проверку на корректность номера порта.


client_db.py
~~~~~~~~~~~~~~

.. autoclass:: client.client_db.ClientDatabase
	:members:
	
connection.py
~~~~~~~~~~~~~~

.. autoclass:: client.connection.ClientConnection
	:members:

client_gui.py
~~~~~~~~~~~~~~

.. autoclass:: client.client_gui.ainWindow
	:members:

start_dialog.py
~~~~~~~~~~~~~~~

.. autoclass:: client.start_dialog.UserNameDialog
	:members:


make_add.py
~~~~~~~~~~~~~~

.. autoclass:: client.make_add.AddContactDialog
	:members:
	
	
make_del.py
~~~~~~~~~~~~~~

.. autoclass:: client.make_del.DelContactDialog
	:members:
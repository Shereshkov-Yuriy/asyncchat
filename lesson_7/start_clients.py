"""Запуск нескольких клиентов"""
from subprocess import Popen, CREATE_NEW_CONSOLE

process = []  # Список клиентских процессов
while True:
    action = input("Запустить сервер и клиентов (s)\nЗакрыть клиентов (x)\n"
                   "Выйти (q)\nВыберите действие: ")
    if action == "q":
        break
    elif action == "s":
        process.append(Popen("python server.py", creationflags=CREATE_NEW_CONSOLE))
        for _ in range(4):
            process.append(Popen('python client.py', creationflags=CREATE_NEW_CONSOLE))
    elif action == "x":
        for p in process:
            p.kill()
        process.clear()

"""Запуск нескольких клиентов"""
from subprocess import Popen, CREATE_NEW_CONSOLE

process = []  # Список клиентских процессов
while True:
    print("Запустить сервер и клиентов (s). Закрыть клиентов (x). Выйти (q)")
    action = input("Выберите действие: ")
    if action == "q":
        break
    elif action == "s":
        num_clients = int(input("Введите число тестовых клиентов: "))
        process.append(Popen("python server.py", creationflags=CREATE_NEW_CONSOLE))
        for i in range(num_clients):
            process.append(Popen(f"python client.py --name tester{i + 1}", creationflags=CREATE_NEW_CONSOLE))
    elif action == "x":
        for p in process:
            p.kill()
        process.clear()

"""Запуск нескольких клиентов"""
from subprocess import Popen, CREATE_NEW_CONSOLE


def main():
    """Запускает опрос команд через командную строку."""
    processes = []  # Список клиентских процессов
    while True:
        print("Запустить сервер и клиентов (s). Закрыть клиентов (x). Выйти (q)")
        action = input("Выберите действие: ")
        if action == "q":
            break
        if action == "s":
            num_clients = int(input("Введите число тестовых клиентов: "))
            processes.append(Popen("python server.py", creationflags=CREATE_NEW_CONSOLE))
            for i in range(num_clients):
                processes.append(Popen(f"python client.py --name tester{i + 1} -p 123456",
                                     creationflags=CREATE_NEW_CONSOLE))
        elif action == "x":
            for process in processes:
                process.kill()
            processes.clear()


if __name__ == "__main__":
    main()

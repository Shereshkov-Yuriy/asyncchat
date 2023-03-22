"""
Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса. По результатам проверки должно
выводиться соответствующее сообщение.
"""
from ipaddress import ip_address
from task_1 import host_ping


def host_range_ping():
    """
    Проверить заданный диапазон.
    :return:
    """
    while True:
        try:
            ipv4 = ip_address(input("Введите ip-адрес: "))
            last_octet = int(str(ipv4).split('.')[3])
            break
        except ValueError:
            print("Некорректный ip-адрес. Пример: 127.0.0.1")

    while True:
        try:
            num_ip = int(input("Какое количество адресов проверить? "))
            if num_ip < 0:
                print("Введите неотрицательное число.")
                continue
        except:
            print("Введите целое число.")

        if 0 <= (last_octet + num_ip) <= 256:
            break
        else:
            print(f"Меняться должен только последний октет каждого адреса в диапазоне 0 - 255.\n"
                  f"Максимальное число в данном случае {256 - last_octet}")

    ip_list = [str(ip_address(ipv4) + i) for i in range(num_ip)]
    return host_ping(ip_list)


if __name__ == "__main__":
    host_range_ping()

"""
Введите ip-адрес: 217.77.52.100
Какое количество адресов проверить? 4
Узел 217.77.52.100 Доступен
Узел 217.77.52.101 Недоступен
Узел 217.77.52.102 Доступен
Узел 217.77.52.103 Недоступен
"""

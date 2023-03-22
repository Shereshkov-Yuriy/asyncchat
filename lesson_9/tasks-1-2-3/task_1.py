"""
Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться
доступность сетевых узлов. Аргументом функции является список, в котором каждый сетевой
узел должен быть представлен именем хоста или ip-адресом. В функции необходимо
перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с
помощью функции ip_address().
"""
from subprocess import Popen, PIPE
from ipaddress import ip_address
from socket import gethostbyname


def host_ping(ip_addrs, n=2, w=400):
    """
    Параметры команды 'ping':
    -n <число>           Число отправляемых запросов проверки связи.
    -w <время_ожидания>  Задает время ожидания каждого ответа (в миллисекундах).
    :param ip_addrs:
    :param n:
    :param w:
    :return:
    """
    availability = {0: "Доступен", 1: "Недоступен"}
    result = {"Доступен": [], "Недоступен": []}
    for addr in ip_addrs:
        try:
            ipv4 = ip_address(addr)
        except ValueError:
            # если адрес представлен именем
            ipv4 = gethostbyname(addr)
        # словарь имени и ip-адреса
        hosts = {ipv4: addr}
        # проверить доступность
        proc_ping = Popen(f"ping {ipv4} -n {n} -w {w}", shell=False, stdout=PIPE)
        proc_ping.wait()
        # добавить в словарь
        result[availability[proc_ping.returncode]].append(str(ipv4))
        # вывести
        print(f"Узел {hosts[ipv4]} {availability[proc_ping.returncode]}")
    return result


if __name__ == "__main__":
    ip_list = ["3.187.153.168", "217.77.52.252", "ya.ru", "54.239.5.213"]
    host_ping(ip_list)

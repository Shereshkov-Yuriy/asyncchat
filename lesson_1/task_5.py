"""
Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты
из байтовового в строковый тип на кириллице.
"""

import subprocess
import chardet

args_list = [
    ['ping', 'yandex.ru'],
    ['ping', 'youtube.com'],
]

for args in args_list:
    subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in subproc_ping.stdout:
        info = chardet.detect(line)
        # print(info)
        line = line.decode(info["encoding"]).encode('utf-8')
        print(line.decode('utf-8'))

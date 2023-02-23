"""
Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных из файлов
info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:
Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание данных.
В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров «Изготовитель
системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в соответствующий список.
Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. В этой же функции
создать главный список для хранения данных отчета — например, main_data — и поместить в него названия столбцов отчета
в виде списка: «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения для этих столбцов также
оформить в виде списка и поместить в файл main_data (также для каждого файла);
Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение данных
через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
Проверить работу программы через вызов функции write_to_csv().
"""
import re
import csv
import os


def get_data():
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = [["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]]

    root = os.getcwd()
    for file in os.listdir(root):
        if file.endswith(".txt"):
            with open(file) as f:
                data = f.read()

                os_prod_re = re.compile(r"Изготовитель системы:\s*\S*")
                os_prod_list.append(os_prod_re.findall(data)[0].split()[2])
                os_name_re = re.compile(r"Windows\s*\S*")
                os_name_list.append(os_name_re.findall(data)[0])
                os_code_re = re.compile(r"Код продукта:\s*\S*")
                os_code_list.append(os_code_re.findall(data)[0].split()[2])
                os_type_re = re.compile(r"Тип системы:\s*\S*")
                os_type_list.append(os_type_re.findall(data)[0].split()[2])

    len_list = len(os_prod_list)
    row_list = [[os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]] for i in range(len_list)]
    main_data.extend(row_list)

    return main_data


def write_to_csv(output_file):
    data = get_data()
    with open(output_file, "w", encoding="utf-8") as f:
        f_writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        f_writer.writerows(data)

    with open(output_file, "r", encoding="utf-8") as f:
        print(f.read())


write_to_csv("data.csv")

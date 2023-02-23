"""
Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных в файле YAML-формата.
Для этого: Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список, второму — целое
число, третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом, отсутствующим
в кодировке ASCII (например, €);
Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml. При этом обеспечить стилизацию файла
с помощью параметра default_flow_style, а также установить возможность работы с юникодом: allow_unicode = True;
Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.
"""
import yaml

upload_data = {
    "items": ["tower", "monitor", "peripherals"],
    "quantity": 2,
    "price": {"tower": "4000\u00a5",
              "monitor": "1500\u00a5",
              "peripherals": "500\u00a5"}
}

with open("file.yaml", "w", encoding="utf-8") as f:
    yaml.dump(upload_data, f, default_flow_style=False, allow_unicode=True)

with open("file.yaml", "r", encoding="utf-8") as f:
    load_data = yaml.load(f, Loader=yaml.SafeLoader)

print(upload_data == load_data)

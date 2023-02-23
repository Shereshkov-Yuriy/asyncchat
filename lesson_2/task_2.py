"""
Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах. Написать скрипт,
автоматизирующий его заполнение данными. Для этого: Создать функцию write_order_to_json(), в которую передается
5 параметров — товар (item), количество (quantity), цена (price), покупатель (buyer), дата (date). Функция должна
предусматривать запись данных в виде словаря в файл orders.json. При записи данных указать величину отступа
в 4 пробельных символа;
Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
"""
import json


def write_order_to_json(item, quantity, price, buyer, date):
    with open("orders.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    with open("orders.json", "w", encoding="utf-8") as f:
        orders_list = data["orders"]
        upload_data = {
            "item": item,
            "quantity": quantity,
            "price": price,
            "buyer": buyer,
            "date": date,
        }
        orders_list.append(upload_data)
        json.dump(data, f, indent=4, ensure_ascii=False)


write_order_to_json("PC", "4", "22000", "Romanov G.M.", "04.06.2016")
write_order_to_json("МФУ", "6", "8000", "Rogov N.V.", "08.08.2018")
write_order_to_json("printer", "10", "10000", "Иванов И.И.", "14.04.2017")

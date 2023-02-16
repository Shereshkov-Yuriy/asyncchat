"""
Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить
тип и содержание соответствующих переменных. Затем с помощью онлайн-конвертера преобразовать
строковые представление в формат Unicode и также проверить тип и содержимое переменных.
"""

word_list = ["разработка", "сокет", "декоратор"]

for word in word_list:
    print(word, type(word), sep=', ', end='\n')

word_list_unicode = [
    b"\xd1\x80\xd0\xb0\xd0\xb7\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xba\xd0\xb0",
    b"\xd1\x81\xd0\xbe\xd0\xba\xd0\xb5\xd1\x82",
    b"\xd0\xb4\xd0\xb5\xd0\xba\xd0\xbe\xd1\x80\xd0\xb0\xd1\x82\xd0\xbe\xd1\x80",
]

for word in word_list_unicode:
    print(word, type(word), sep=', ', end='\n')

"""
Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления
в байтовое и выполнить обратное преобразование (используя методы encode и decode).
"""

word_list = ["разработка", "администрирование", "protocol", "standard"]
word_list_unicode = [w.encode('utf-8') for w in word_list]

print(*word_list_unicode, sep='\n')

for word in word_list_unicode:
    print(word.decode('utf-8'), end='\n')

"""
Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования
в последовательность кодов (не используя методы encode и decode) и определить
тип, содержимое и длину соответствующих переменных.
"""

word_list = [b"class", b"function", b"method"]

for word in word_list:
    print(word, type(word), len(word), sep=', ', end='\n')

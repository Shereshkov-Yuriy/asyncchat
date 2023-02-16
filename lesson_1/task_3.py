"""
Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
"""

word_list = ["attribute", "класс", "функция", "type"]

for word in word_list:
    try:
        print(bytes(word, 'ascii'), end='\n')
    except UnicodeEncodeError:
        print(f"Слово '{word}' нельзя записать в байтовом типе")

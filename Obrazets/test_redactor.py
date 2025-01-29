def encode_dict_values(input_dict):
    encoded_dict = {}
    for key, value in input_dict.items():
        if isinstance(value, str):
            # Применяем .encode('utf-8') к строковым значениям
            encoded_dict[key] = value.encode('utf-8')
        elif isinstance(value, dict):
            # Если значение — это словарь, рекурсивно обрабатываем его
            encoded_dict[key] = encode_dict_values(value)
        else:
            # Если значение не строка и не словарь, просто копируем его
            encoded_dict[key] = value
    return encoded_dict

# Пример использования
my_dict = {
    'name': 'Alice',
    'age': 30,
    'city': 'Moscow',
    'nested': {
        'hobby': 'reading',
        'language': 'Russian'
    }
}

encoded_dict = encode_dict_values(my_dict)

# Проверяем результат
for key, value in encoded_dict.items():
    print(f"{key}: {value} (type: {type(value)})")
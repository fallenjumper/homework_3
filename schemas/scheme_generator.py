import json
import requests
from os import path, makedirs
import re


# Приводим типизацию питона к используемой в либе jsonschema
def get_type_obj(obj):
    NoneType = type(None)
    if isinstance(obj, str):
        return "string"
    elif isinstance(obj, (int, float)):
        return "number"
    elif isinstance(obj, dict):
        return "object"
    elif isinstance(obj, list):
        return "array"
    elif isinstance(obj, bool):
        return "boolean"
    elif isinstance(obj, NoneType):
        return "null"
    else:
        raise TypeError(f"Невозможно переопределить тип объекта. Тип: {type(obj)}")


# метод для создания базовых схем на основе единичного запроса
def create_scheme(res, api_url, test_name):
    result_dict = {"type": get_type_obj(res), "properties": {}, "required": []}

    # если на входе словарь, значит достаточно один раз пронать все элементы и присвоить типы
    if result_dict["type"] == "object":
        for key, value in res.items():
            result_dict["properties"].update({key: {"type": get_type_obj(value)}})
            result_dict["required"].append(key)

    # если принят список, то требуется прогнать все элементы
    elif result_dict["type"] == "array":
        for item in res:
            for key, value in item.items():
                # если ключа нет в словаре - просто его добавляем
                if key not in result_dict["properties"]:
                    result_dict["properties"].update({key: {"type": get_type_obj(value)}})
                    result_dict["required"].append(key)

                # если key такой уже есть и такого value еще нет в словаре -> добавляем
                elif get_type_obj(value) not in result_dict["properties"][key]["type"]:
                    if isinstance(result_dict["properties"][key]["type"], str):
                        old_value = result_dict["properties"][key]["type"]
                        result_dict["properties"].update({key: {"type": [old_value, get_type_obj(value)]}})
                    elif isinstance(result_dict["properties"][key]["type"], list):
                        result_dict["properties"][key]["type"].append(get_type_obj(value))

    # записываем результаты в schemas/название теста/требуемый запрос (если нужно - создаем подпапки)
    filename = f"schemas/{test_name}/{api_url}.data"
    makedirs(path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        s = json.dumps(result_dict, indent=4)
        f.write(s)


# загружаем схему из файла(если нет такой -> создаем)
def get_scheme(base_url, api_url, test_name):
    # заменяем пробелы на " "
    api_url = re.sub('%20', ' ', api_url)

    # когда апи на базовом адресе - подставляем своё значение в api_url
    if api_url == "":
        api_url = "index_api"
        res = requests.get(base_url).json()
    else:
        res = requests.get(base_url + api_url).json()

    # заменяем запрещенные символы для названий папок или файлов на / (подпапки в каталоге схем)
    api_url = re.sub('[:*?"<>|=]', '/', api_url)

    # Решение чисто для теста и в реальности лучше убрать и вынести создание схемы через аргумент, либо руками
    if not path.isfile(f"schemas/{test_name}/{api_url}.data"):
        create_scheme(res, api_url, test_name)

    with open(f"schemas/{test_name}/{api_url}.data", "r") as file:
        return json.loads(file.read())

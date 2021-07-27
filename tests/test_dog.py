import requests
import pytest
from jsonschema import validate
from schemas.scheme_generator import get_scheme
from helpers import get_count_obj

base_url = "https://dog.ceo/api/"


# Проверка соответствия схеме
@pytest.mark.parametrize("api_url", ["breeds/list/all", "breed/hound/images", "breed/hound/list"])
def test_api_json_schema(api_url):
    res = requests.get(base_url + api_url)
    validate(instance=res.json(), schema=get_scheme(base_url, api_url, __name__))


# Проверка количества изображений в зависимости от аргумента
@pytest.mark.parametrize("api_url, count_obj",
                         [("breeds/image/random/3", 3), ("breeds/image/random/10", 10), ("breeds/image/random/50", 50)])
def test_count_random_obj(api_url, count_obj):
    res = requests.get(base_url + api_url).json()
    assert get_count_obj(res["message"]) == count_obj
    assert res["status"] == "success"


# Тест поиска по породе
@pytest.mark.parametrize("breed_value", ["hound", "mastiff", "retriever"])
def test_search_by_breed(breed_value):
    target_url = f"{base_url}breed/{breed_value}/images"
    res = requests.get(target_url).json()
    for item in res["message"]:
        assert breed_value in item
    assert res["status"] == "success"


# Тест поиска соответствия пород
@pytest.mark.parametrize("breed_value, sub_breed_values",
                         [("australian", ["shepherd"]), ("buhund", ["norwegian"]), ("mountain", ["bernese", "swiss"])])
def test_search_by_sub_breed(breed_value, sub_breed_values):
    target_url = f"{base_url}breed/{breed_value}/list"
    res = requests.get(target_url).json()
    for item in sub_breed_values:
        assert item in res["message"]
    assert res["status"] == "success"


# Тест проверки соответствия адреса картинки для запроса
@pytest.mark.parametrize("breed_value, sub_breed_value",
                         [("australian", "shepherd"), ("buhund", "norwegian"), ("mountain", "bernese")])
def test_sub_breed_images(breed_value, sub_breed_value):
    target_url = f"{base_url}breed/{breed_value}/{sub_breed_value}/images"
    res = requests.get(target_url).json()
    for item in res["message"]:
        assert f"{breed_value}-{sub_breed_value}" in item
    assert res["status"] == "success"

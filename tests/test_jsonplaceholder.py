import requests
import pytest
from random import randint
from jsonschema import validate
from schemas.scheme_generator import get_scheme
from helpers import get_count_obj, check_is_downloadable

base_url = "https://jsonplaceholder.typicode.com/"


# Проверка соответствия схеме
@pytest.mark.parametrize("api_url", ["albums", "users", "posts"])
def test_api_json_schema(api_url):
    res = requests.get(base_url + api_url)
    validate(instance=res.json(), schema=get_scheme(base_url, api_url, __name__))


# Проверка количества элементов в ответе
@pytest.mark.parametrize("api_url,count_obj", [("albums", 100), ("users", 10), ("posts", 100)])
def test_count_obj(api_url, count_obj):
    res = requests.get(base_url + api_url).json()
    assert get_count_obj(res) == count_obj


# Проверка равнозначности продублированных под разными адресами api
@pytest.mark.parametrize("user_id", [randint(1, 10) for i in range(5)])
def test_nested_resource(user_id):
    res1 = requests.get(base_url + f"users/{user_id}/todos")
    res2 = requests.get(base_url + f"todos?userId={user_id}")
    assert res1.status_code == 200
    assert res1.json() == res2.json()


# Проверка возможности скачивания по указанным в ответе ссылкам
@pytest.mark.parametrize("photo_id", [1, 2, 3])
def test_is_downloadable_img(photo_id):
    res = requests.get(base_url + f"photos/{photo_id}").json()
    assert check_is_downloadable(res['url'])


# Проверка отсутствия реакции на передачу None агрумента
@pytest.mark.parametrize("arg", ['title', 'body', 'userId'])
def test_none_input(arg):
    res = requests.post(base_url + "posts", data={f"{arg}": None}).json()
    assert res == {'id': 101}

import requests
import pytest
from jsonschema import validate
from schemas.scheme_generator import get_scheme
from helpers import get_count_obj

base_url = "https://api.openbrewerydb.org/"


# Проверка соответствия схеме
@pytest.mark.parametrize("api_url",
                         ["breweries", "breweries/search?query=dog", "breweries/9180", "breweries?by_city=san%20diego"])
def test_api_json_schema(api_url):
    res = requests.get(base_url + api_url)
    validate(instance=res.json(), schema=get_scheme(base_url, api_url, __name__))


# Проверка ограничения количества постов
@pytest.mark.parametrize("api_url,count_obj", [("breweries?page=15", 20), ("breweries?per_page=25", 25)])
def test_count_obj(api_url, count_obj):
    res = requests.get(base_url + api_url).json()
    assert get_count_obj(res) == count_obj


# Проверка соответствия id запросе и ответе
@pytest.mark.parametrize('id_value', [13018, 12202, 9094])
def test_api_filtering(id_value):
    res = requests.get(base_url + f"/breweries/{id_value}").json()
    assert res['id'] == id_value


# Проверка api поиска(если смотреть по всем результатам, то будет выдача лишнего - баг api)
@pytest.mark.parametrize('query', ["dog", "beer", "tree"])
def test_api_search(query):
    res = requests.get(base_url + f"/breweries/search?query={query}").json()
    assert query in res[0]["name"].lower()


# Проверка autocomplete поиска
@pytest.mark.parametrize('query', ["dog", "beer", "tree"])
def test_api_autocomplete(query):
    res = requests.get(base_url + f"/breweries/autocomplete?query={query}").json()
    for item in res:
        assert query in item["name"].lower()

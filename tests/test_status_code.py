import requests


def test_url_status(base_url, requested_status_code):
    res = requests.get(base_url)
    assert res.status_code == requested_status_code

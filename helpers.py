import requests


def get_count_obj(obj):
    if isinstance(obj, dict):
        return len(obj.items())
    elif isinstance(obj, list):
        return len(obj)
    else:
        TypeError("Неизвестный формат ответа")


def check_is_downloadable(url):
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True

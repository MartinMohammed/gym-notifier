import requests
from log import log

@log
def make_http_request(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status() # raise an HTTPError if the status code is not 200  
        raw_html = response.content # type string 
    except requests.exceptions.RequestException as e:
        print(f"The HTTP request to {url} failed.\n{e}")
        return f"Failed HTTP request to {url}."
    return raw_html
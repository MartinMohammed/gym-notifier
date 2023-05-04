# What is python-decouple? 
'''
A generic python library that helps to organize settings (development, production, stage, etc) without having to redeploy the app
* store parameters in ini or .env files;
'''
from decouple import config
import requests

TELEGRAM_API_ACCESS_TOKEN = config("TELEGRAM_API_ACESS_TOKEN")
TELEGRAM_CHAT_ID = config("MY_TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = "https://api.telegram.org"


def call_telegram_method(method_name: str, **kwargs) -> requests.Response:
    # Check if parameters were specified in the dict
    query_string = "" # default value 
    if(len(kwargs.keys()) != 0):
        query_string = f"?"
        for (key, value) in kwargs.items():
            query_string += f'{key}={value}&'
    try:
        print(query_string)
        response = requests.get(f"{TELEGRAM_API_URL}/bot{TELEGRAM_API_ACCESS_TOKEN}/{method_name}{query_string}") 
        response.raise_for_status() # if status code is not 200 / OK
        return response.json()
    except requests.exceptions.RequestException as e:
       print(e)

def send_message(chat_id: str, message: str):
    response = call_telegram_method("sendMessage", chat_id = chat_id, text = message)
    print(response)

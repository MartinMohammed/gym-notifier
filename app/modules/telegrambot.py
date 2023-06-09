# Ensure that this module can only be imported and
# cannot be run as the main program
if __name__ != "__main__":
    # What is python-decouple? 
    '''
    A generic python library that helps to organize settings
     (development, production, stage, etc) without having to redeploy the app
    * store parameters in ini or .env files;
    '''
    # from decouple import config
    import requests
    import sys
    import os
    import logging
    from decouple import config
    from helper import check_env_defined

    telegram_logger = logging.getLogger("telegram_logger")

    # TELEGRAM_API_ACCESS_TOKEN = config("TELEGRAM_API_ACESS_TOKEN")
    TELEGRAM_API_ACCESS_TOKEN = os.environ.get("TELEGRAM_API_ACESS_TOKEN") or config("TELEGRAM_API_ACESS_TOKEN")
    check_env_defined(TELEGRAM_API_ACCESS_TOKEN, name="Telegram API Access Token")
    # TELEGRAM_CHAT_ID = config("MY_TELEGRAM_CHAT_ID")
    TELEGRAM_CHAT_ID = os.environ.get("MY_TELEGRAM_CHAT_ID") or config("MY_TELEGRAM_CHAT_ID")
    check_env_defined("Telegram Chat Id", name="Telegram Chat Id")
    TELEGRAM_API_URL = "https://api.telegram.org"


    def call_telegram_method(method_name: str, **kwargs) -> requests.Response:
        # Check if parameters were specified in the dict
        query_string = ""  # default value
        if len(kwargs.keys()) != 0:
            query_string = f"?"
            for (key, value) in kwargs.items():
                query_string += f'{key}={value}&'
        try:
            response = requests.get(f"{TELEGRAM_API_URL}/bot{TELEGRAM_API_ACCESS_TOKEN}/{method_name}{query_string}") 
            response.raise_for_status()  # if status code is not 200 / OK
            telegram_logger.info("Success: Message was sent.")
        except requests.exceptions.RequestException as e:
            # ! Telegram bot error logging
            telegram_logger.critical(f"Error with Telegram method call: {method_name}. {e}")
            sys.exit(1)
        else: 
            return response

    # @log
    def send_message(chat_id: str, message: str) -> requests.Response:
        response = call_telegram_method("sendMessage", chat_id=chat_id, text=message)
        return response

elif __name__ == "__main__":
    print(f"This module cannot be ran as the main program, instead must be imported.")
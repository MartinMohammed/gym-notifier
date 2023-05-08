# Ensure that this moudle can only be imported and 
# cannot be run as the main program
if __name__ != "__main__":
    import requests
    # from log import log
    import logging 
    import logging.config

    # logging.config.fileConfig("logging.conf")
    request_cycle_logger = logging.getLogger("request_cycle")


    # @log
    def make_http_request(url: str):
        try:
            response = requests.get(url)
            response.raise_for_status() # raise an HTTPError if the status code is not 200  
            raw_html = response.content # type string 
        except requests.exceptions.RequestException as e:
            request_cycle_logger.error(f"There was an error in making an request to {url}.\n{e}", exc_info=True)
        else:
            request_cycle_logger.info(f"Successfully made an Request to {url}.")
            return raw_html
            

elif __name__ == "__main__":
    print(f"This module cannot be ran as the main program, instead must be imported.")
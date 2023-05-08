import datetime
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
        '''
        Makes an HTTP request to the specified url and returns the content of the response.

        :param url: The url the request goes to.
        '''
        try:
            response = requests.get(url)
            response.raise_for_status() # raise an HTTPError if the status code is not 200  
            raw_html = response.content # type string 
        except requests.exceptions.RequestException as e:
            request_cycle_logger.error(f"There was an error in making an request to {url}.\n{e}", exc_info=True)
        else:
            request_cycle_logger.info(f"Successfully made an Request to {url}.")
            return raw_html
            
    def calculate_sleep_time_in_minutes(time_interested_in: dict[str, int], current_time: datetime.datetime, next_day: bool) -> int:
        '''
        Calculates the time difference between the current time and the time the user is interested in.
        Returns the time difference in minutes.
        
        :param time_interested_in: A dictionary containing the hour and minute the user is interested in. Example: {"start": 9, "end": 10}
        :param current_time: The current datetime.
        :param next_day: A boolean value indicating whether the user is interested in a time that is tomorrow (True) or today (False).
        :return: The time difference in minutes.
        '''

        # If the user is interested in a time that is tomorrow (e.g. interested in 17h and it is 9h), 
        # then calculate the time difference until that time tomorrow (e.g. sleep for 8 hours)
        if next_day:
            # The number of hours until the interested time
            hours_difference = time_interested_in.get("start") - current_time.hour
            # The number of minutes until the next hour
            minutes_difference = 60 - current_time.minute
            # The total number of minutes to sleep
            total_minutes = ((minutes_difference)) + ((hours_difference - 1) * 60)
            return total_minutes

        # If the user is interested in a time that is today (e.g. interested in 9h and it is 17h),
        # then calculate the time difference until that time tomorrow (e.g. sleep for 16 hours)

        # When 00:00 is reached, current_time.hour will become smaller than time_intersted_in.get("start") 
        # which will cause to execute block 1 and calculate the amount of minutes until the point of time
        # at the same day
        else:
            # The number of minutes until the next hour
            minutes_difference = 60 - current_time.minute
            # The number of hours until the interested time tomorrow
            hours_difference = (24 - current_time.hour)
            # The total number of minutes to sleep
            total_minutes = ((minutes_difference)) + ((hours_difference - 1) * 60)
            return total_minutes



elif __name__ == "__main__":
    print(f"This module cannot be ran as the main program, instead must be imported.")
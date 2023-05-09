import sys
# Ensure that this module can only be imported and
# cannot be run as the main program
if __name__ == "__main__":
    print(f"This module cannot be ran as the main program, instead must be imported.")
    sys.exit(1)


# 3rd Party libs
import time
import logging
import datetime
from bs4 import BeautifulSoup
from decouple import config

# Own libs
from .helper import make_http_request, calculate_sleep_time_in_minutes
from .telegrambot import send_message

# ----------- GET LOGGER -----------
root_logger = logging.getLogger("root_logger")
request_cycle_logger = logging.getLogger("request_cycle")

REFRESH_CYCLE_TIME = 30  # minutes


class Studio: 
    """
    Studio(document_table_row_number: int, location: str, current_people: int, maximum: int)

    {
        [location]: Studio(document_table_row_number: int, location: str, current_people: int, maximum: int)
    }
    """

    all_dict = {}
    # 1. HTTP request an __URL to get the document 
    __URL = config("FITNESS_FABRIK_BASE_URL")

    # Static and Class Methods defined with a simple question: 
    # Do I need this functionality on my instances it'self', if the answer is no: 
    @classmethod
    def instantiate_studios(cls) -> None: 
        """
        This method instantiates a Studio object for each studio and adds it to the class's all_dict dictionary.

        :param cls: The class that the method is a part of.
        :return: None

        The method first retrieves all the studios and their data from the website by calling the
         __get_all_occupancy_data() method of the class.

        Then, the for loop iterates over each studio in the studios list,
         and extracts the following information for each studio:
            - Row number
            - Location
            - Current number of people
            - Maximum number of people allowed

        The method creates a new Studio object with the extracted data
         and adds it to the all_dict dictionary with the location as the key:
            cls.all_dict[location] = Studio(row, location, current, maximum)

        Finally, the method logs a message indicating that all the studios were successfully instantiated.

        Overall, this method initializes the Studio objects
        and makes them available in the all_dict dictionary for other methods to use.
        """

        # Fetch all Studios (including their occupancy, name...)
        studios = cls.__get_all_occupancy_data()
        for studio in studios:
            row_number = studio.get("row_number")
            location = studio.get("location")
            current = studio.get("current")
            maximum_people = studio.get("maximum_people")

            # Instantiate a new Studio, and add it to the Studios Dictionary
            cls.all_dict[location] = Studio(
                document_table_row_number=row_number,
                location=location, current=current, maximum_people=maximum_people)
        request_cycle_logger.info("Successful instantiated studios.")

    @classmethod
    def notify_on_people_amount_criteria(
            cls, time_interested_in: dict[str, int], minimum: int = None,
            maximum: int = None, specific_studio_name="",
            telegram_chat_id: str = "", recipient_name: str = ""):
        """
        Function Parameters:
        * time_interested_in: a dictionary that specifies the time range
        the user is interested in being notified for a match, with keys "start" and "end".
        * minimum (optional):
        an integer representing the minimum number of people in the gym for the user to be interested in,
         default is None.
        * maximum (optional):
        an integer representing the maximum number of people in the gym for the user to be interested in,
         default is None (maximum will be fetched from the studio).
        * specific_studio_name (optional):
        a string representing the name of the studio to monitor, default is an empty string which means all studios.
        * telegram_chat_id:
        a string representing the Telegram chat ID of the user to send the notification to.
        * recipient_name: a string representing the name of the recipient of the notification.
        * Returns: None

        Description:
        This function continuously monitors the number of people in a gym (or a specific gym if specified)
        within a time range
        specified by the user, and sends a message via Telegram to the user if the number of people meets their
        preferences (minimum and maximum).
        The function runs on an infinite loop and sleeps until the next check or until the notification is sent.
        The function requires a valid Telegram chat ID to send the notification.
        The function also logs relevant information, such as the current number of people in the gym and whether
        the criteria for the user's preference have been met.
        """

        try:
            # Do some validation 
            assert cls.check_location_exists(specific_studio_name),\
                f"Specified studio name '{specific_studio_name}' is not valid!"
            if maximum is None:
                maximum = cls.all_dict.get(specific_studio_name).maximum_people  # The default value
            if time_interested_in.get("end") is None or time_interested_in.get("end") < time_interested_in.get("start"):
                time_interested_in["get"] = 23  # the default value

            assert isinstance(maximum, int), f"The maximum of people in the gym must be a number larger 0."
            assert isinstance(minimum, int),\
                f"The minimum of people in the gym must be larger 0 and smaller than {maximum}"
            assert telegram_chat_id is not None,\
                "Telegram chat ID is required in order to send the notification on telegram."
            assert time_interested_in.get("start") is not None,\
                "Please specify start time (in hours) you are interested in getting notified for match."
            assert recipient_name != "", "Your name must be specified for the message."
            assert time_interested_in.get("start") <= time_interested_in.get("end"),\
                "The start time you are interested in must be smaller or equal then the end time."
        except Exception as e: 
            root_logger.error(e, exc_info=True)
        else: 
            # Infinite loop to keep the process going 
            while True:   
                # Only do the checking between 5PM and 7PM 
                now = datetime.datetime.now()  # German time format 0 - 24h
                # Time range the user is interested in and not sent and notification today
                if time_interested_in.get("start") <= now.hour <= time_interested_in.get("end"):
                    studio_check_request = Studio.__check_occupancy(
                        specific_studio_name=specific_studio_name, minimum=minimum, maximum=maximum)
                    root_logger.info(f'{now.strftime("%m/%d/%Y, %H:%M:%S")} {str(studio_check_request)}')
                    
                    # Criteria fulfilled -> send message
                    if studio_check_request.get("criteria_fulfilled"):
                        # The default message
                        message = f"""
                        Hey {recipient_name}!
                        \nBereit, fit zu werden und Spaß zu haben? Komm zu uns ins
                         Fitnessstudio in {studio_check_request.get("location")}!
                        \nAktuell sind nur {studio_check_request.get("current")}
                         Leute hier, also kannst du dein Workout ohne Menschenmassen genießen.
                        \nVerpasse nicht die Gelegenheit, deine Gesundheit zu verbessern und neue Leute kennenzulernen!
                        \nWir sehen uns im Fitnessstudio!"
                        """.strip()
                        try:
                            # Actually got already status checking inside the function definiton
                            response = send_message(chat_id=telegram_chat_id, message=message)
                            assert response.status_code == 200, "Telegram message couldn't be sent."
                        except Exception as e: 
                            request_cycle_logger.error(e, exc_info=True)
                            sys.exit(1)
                        else: 
                            request_cycle_logger.info("Message was sent, sleep until next day.")
                            until_next_day = 24 - now.hour
                            time.sleep(until_next_day * 60 * 60)
                        
                    # Criteria not fulfilled, wait 30 minutes before requesting again
                    else:
                        request_cycle_logger.info(f"Sleep {REFRESH_CYCLE_TIME} minutes before making the next request.")
                        time.sleep(REFRESH_CYCLE_TIME * 60)
                # Important presumption is that start < end, made sure with validation 
                else: 
                    '''
                    If the user is interested in a time that is later than the current time, 
                    and the time of interest is on the next day, calculate the amount of minutes 
                    until 00:00 AM of the next day. 
                    
                    Otherwise, if the time of interest is on the 
                    same day and later than the current time, calculate the amount of minutes 
                    until the time of interest.
                    '''
                    next_day = time_interested_in.get("start") > now.hour
                    sleep_time_in_minutes = calculate_sleep_time_in_minutes(
                        time_interested_in=time_interested_in, current_time=now, next_day=next_day)
                    request_cycle_logger.info(
                        f"Not in the time interval {time_interested_in.get('start')}:00-{time_interested_in.get('end')}"
                        f":00 the user is interested in. Sleep until {time_interested_in.get('start')}:00! "
                        f"({sleep_time_in_minutes}minutes)")
                    time.sleep(60 * sleep_time_in_minutes)

    @classmethod 
    def __check_occupancy(cls, minimum: int = None, maximum: int = None, specific_studio_name="") -> dict:
        """
        This is a class method called __check_occupancy hat checks if a specific studio meets a user-defined
        set of criteria regarding the number of people currently inside the studio. with the following parameters:

        * cls: the class itself.
        * minimum (optional): an integer that represents the minimum amount of people allowed in a studio.
        * maximum (optional): an integer that represents the maximum amount of people allowed in a studio.
        * specific_studio_name (optional): a string that represents the name of the studio that needs to be checked.
        * Returns an object that contains the following keys:
        * location: a string that represents the location of the studio.
        * minimum: an integer that represents the minimum amount of people allowed in the studio.
        * maximum: an integer that represents the maximum amount of people allowed in the studio.
        * criteria_fulfilled: a boolean value that represents if the criteria are fulfilled or not.
        * current: an integer that represents the current amount of people in the studio.
        """

        # Check if the amount of current people inside the studio is between [minimum; maximum]
        def cb(studio):
            """
            Now perform the actual check for the number of people in the gym.

            The studio data should be in the following format:
            {
            "location": location,
            "studio_row_number": studio_row_number,
            "current": new_current,
            "maximum_people": new_maximum_people
            }
            """
            # Default Value
            criteria_fulfilled = True

            try:
                # Validation, least Minimum or Maximum must be defined
                assert minimum is not None and minimum < studio.get("maximum_people"),\
                    "Error. Minimum amount of people in Studio not set appropriately."
                assert maximum is not None and maximum <= studio.get("maximum_people"),\
                    "Error. Minimum amount of people in Studio not set appropriately."
            except Exception as e:
                root_logger.error(f"There was an error with the Minimum and Maximum people amount in the Studio.{e}")
            else:
                current_people = studio.get("current")
                location = studio.get("location")
                # Check if minimum was specified 
                # current_people should be above minimum
                # Too few people
                if minimum:
                    assert isinstance(minimum, int), "The minimum for checking studio people must be an integer."
                    if current_people < minimum:
                        criteria_fulfilled = False
                
                # Check if maximum was specified
                # current_people should be below minimum
                # Too many people
                if maximum:
                    assert isinstance(maximum, int), "The maximum for checking studio people must be an integer."
                    if current_people > maximum:
                        criteria_fulfilled = False

                # Condition was fulfilled
                return {"location": location,  "minimum": minimum,
                        "maximum": maximum, "criteria_fulfilled": criteria_fulfilled, "current": current_people}
        try:
            studio_criteria_check = cls.__get_occupancy_data(studio_name=specific_studio_name, cb=cb)
            assert studio_criteria_check is not None,\
                f"There was an Error with the criteria_fulfilled_result. It should be a boolean value," \
                f" instead {studio_criteria_check.get('criteria_fulfilled')}!"
        except Exception as e:
            request_cycle_logger.error(e, exc_info=True)
        else:
            request_cycle_logger.info(f"Successfully checked if studio matches user defined criteria!"
                                      f" ({'Yes' if studio_criteria_check.get('criteria_fulfilled') else 'No'})")
            return studio_criteria_check

    @staticmethod
    def __get_occupancy_data(studio_name: str, cb=None):
        """
        :param studio_name: A string representing the name of the studio whose data is to be updated.
        :param cb: An optional callback function that receives the fetched Studio data.
        This is a static method called __get_occupancy_data in the Studio class.
         It updates the data of a specified studio.

        The method performs the following steps:
        - Check if the specified studio_name is valid by calling the check_location_exists method.
        - If the studio name is invalid, an error message is logged.
        - If the studio name is valid, the method proceeds to fetch the data for the specified studio
         from a URL using the make_http_request function.
        - The fetched data is then parsed using the BeautifulSoup library,
         and the relevant data is extracted from the parsed HTML.
        - The studio data is then updated based on the fetched data.
        - If a callback function was provided, it is called with the fetched studio data as an argument.
        - The method is decorated with the @staticmethod decorator,
         which means that it can be called on the class itself and
          does not require an instance of the class to be created.
        """

        try:
            # Check if the studio is already saved -- because we do fetch all in the beginning
            assert Studio.check_location_exists(studio_name), f"Specified studio name '{studio_name}' is not valid!"
        except AssertionError as e:
            # If the studio name is invalid, just update all studios 
            # IMPORTANT: prints the program's location,
            # the line where the error was encountered, and the name and relevant information about the error.
            root_logger.error(e, exc_info=True)
        else: 
            # old request made with @log decorator 
            # raw_html = make_http_request(
            # url = Studio.__URL, config = {"show_parameters": True,
            # "file_name": "http-requests-logs.txt", "return_value": False})
            raw_html = make_http_request(url=Studio.__URL)
            soup = BeautifulSoup(raw_html, 'html5lib')

            # Gives us the representation of the parse tree created from the raw html content
            '''
            Definition of 'parse Tree' / HTML structure of the document 
            An ordered, rooted tree representing the structure of a sentence, broken down to parts-of-speech
            '''

            # The data we are interested in are in table rows 
            data = soup.find("table", attrs={'id': "meineTabelle"})
            table_body = data.tbody
            studios = table_body.find_all("tr")
        
            studio_row_number = Studio.all_dict.get(studio_name).document_table_row_number
            studio_data_rows = studios[studio_row_number].find_all('td')
            location, new_current, new_maximum_people = Studio.__extract_studio_data_from_row(studio_data_rows).values()
            # Now update the studio data from the fetched data

            Studio.all_dict.get(location).current = new_current 
            Studio.all_dict.get(location).location = new_maximum_people 
            request_cycle_logger.info(f"Succesfull updated the updated the studio data of {studio_name}!")

            # OPTIONAL CALLBACK CALL WITH THE STUDIO DATA FETCHED 
            if cb is not None:
                cb_return_value = cb(
                    {"location": location, "studio_row_number": studio_row_number,
                     "current": new_current, "maximum_people": new_maximum_people})
                return cb_return_value 
            
    @staticmethod
    def __get_all_occupancy_data():
        """
        This is a private static method in the Studio class. The method __get_all_occupancy_data
         is used to fetch all the studios' data from a website and then instantiate a
        Studio object for each studio and store them in a dictionary all_dict.
         It also determines the studio row number and name dict constant defined above.

        The method returns a list of dictionaries, where each dictionary
        represents a studio and contains the following keys:

        * row_number: The row number of the studio in the HTML table.
        * location: The location of the studio.
        * current: The number of people currently in the studio.
        * maximum_people: The maximum number of people that can be in the studio.
        The function starts by making an HTTP request to the website specified in Studio.__URL
         using the make_http_request function. It then parses the HTML document using the BeautifulSoup library and
          searches for the data we are interested in, which are in table rows.
           It extracts the data for each studio and instantiates an object with the data.
            Finally, it adds the studio object to the all_dict dictionary.

        Since this is a private static method, it can only be accessed within the Studio class,
         and it's not intended to be called outside class.
        """

        # old request made with @log decorator 
        # raw_html = make_http_request(
        # url=Studio.__URL, config = {"show_parameters": True, "file_name": "http-requests-logs.txt",
        # "return_value": False})
        raw_html = make_http_request(url=Studio.__URL)
        # 2. Parsing the HMTL document 
        '''
        BeautifulSoup library is that it is built on the top of the HTML parsing
         libraries like html5lib, lxml, html.parser
        '''
        soup = BeautifulSoup(raw_html, 'html5lib')

        # Gives us the representation of the parse tree created from the raw html content
        '''
        Definition of 'parse Tree' / HTML structure of the document 
        An ordered, rooted tree representing the structure of a sentence, broken down to parts-of-speech
        '''

        # 3. Searching and navigating through the parse tree 

        # The data we are interested in are in table rows 
        data = soup.find("table", attrs={'id': "meineTabelle"})
        
        table_body = data.tbody

        studios = []
        for row_number, studio in enumerate(table_body.find_all("tr")): 
            '''
                    [<td>
                        Darmstadt            </td>, } location 
                    <td>
                        144            </td> } maximum 
                    <td>,
                        49            </td>] } current 
            '''
            # location_data_cell, maximum_data_cell, current_data_cell = table_body.tr
            # print(location_data_cell)

            studio_data_cells = studio.find_all("td")
            # Extract the studio data 
            '''
            Takes the extracted data for the particular studio and instantiates an object.
            Appends the object in the 'all_dict'.
            '''        
            single_studio_data = Studio.__extract_studio_data_from_row(studio_row=studio_data_cells)
            location, current, maximum_people = single_studio_data.values()
            studio = {"row_number": row_number,
                      "location": location, "current": current, "maximum_people": maximum_people}
            studios.append(studio)
        return studios

    @staticmethod
    def __extract_studio_data_from_row(studio_row) -> dict:
        """
        Function name: extract_studio_data
        Parameters:
          - table_data_cells (list): A list of table data cells containing data for a single studio.

        This function extracts the location, current occupancy, and maximum
         occupancy data from a list of table data cells for a single studio,
          performs some validation, and returns a dictionary containing the extracted data.
        The function first extracts the location data by stripping the leading and
         trailing whitespaces and raises an assertion error if the location string is empty.
        It then tries to convert the maximum and current occupancy data from string to
         integers using the int() function and catches a ValueError if the conversion fails.
          In case of an error, the function logs the error message using the root_logger object and
           includes the exception traceback information.
        Finally, if the data extraction and validation are successful,
         the function returns a dictionary containing the extracted data with the keys "location",
          "current", and "maximum_people".

        """

        location = studio_row[0].text.strip()
        assert location != "", "The location string is not allowed to be empty!"
        try:
            maximum_people = int(studio_row[1].text)
            current = int(studio_row[2].text)
        except ValueError as e: 
            # failed to convert string to integer 
            root_logger.error(f'Failed to convert string to integer: {e}', exc_info=True)
        else:
            return {"location": location, "current": current, "maximum_people": maximum_people}

    @staticmethod
    def check_location_exists(location: str) -> bool:
        return True if location in Studio.all_dict else False

    # ------------------- MAGIC METHODS -------------------
    def __init__(self, document_table_row_number: int, location: str, current: int, maximum_people: int):
        # VALIDATION
        try:
            assert isinstance(location, str), f"The given location '{location}' is not a string!"
            assert current >= 0, f"The amount of current people in the studio {self.current} cannot be less than 0!"
            assert maximum_people >= 0,\
                f"The amount of the maximum people allowed in the studio {self.current} cannot be less than 0!"
        except Exception as e: 
            root_logger.error(e)
        else: 
            # ENCAPSULATION
            self.__document_table_row_number = document_table_row_number
            self.__location = location
            self.__current = current
            self.__maximum_people = maximum_people
    
    def __repr__(self) -> str: 
        # INSTANCE CONSOLE PRINT REPRESENTATION
        return f"{self.__class__.__name__}('{self.__location}', {self.__current}, {self.__maximum_people})"

    # ------------------- GETTER -------------------
    @property
    def document_table_row_number(self) -> int:
        return self.__document_table_row_number

    @property
    def location(self) -> str:
        return self.__location 
    
    @property
    def current(self) -> int:
        return self.__current
    
    @property
    def maximum_people(self) -> int:
        return self.__maximum_people

    # ------------------- SETTER -------------------

    @location.setter
    def location(self, value: str):
        self.__location = value 
    
    @current.setter
    def current(self, value: int):
        self.__current = value 

    @maximum_people.setter
    def maximum_people(self, value: int):
        self.__maximum_people = value 

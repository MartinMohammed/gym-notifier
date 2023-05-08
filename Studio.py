# 3rd Party libs
import sys
import json 
from bs4 import BeautifulSoup
import time
import datetime
import logging
from helper import make_http_request
from decouple import config

# Own libs
# from log import log
from telegrambot import send_message


root_logger = logging.getLogger("root_logger")
request_cycle_logger = logging.getLogger("request_cycle")

REFRESH_CYCLE_TIME = 30 #mins

class Studio: 
    '''
    Studio(document_table_row_number: int, location: str, current_people: int, maximum: int)
    '''
    '''
    {
        [location]: Studio(document_table_row_number: int, location: str, current_people: int, maximum: int)
    }
    ''' 
    all_dict = {} 
    # 1. HTTP request an __URL to get the document 
    __URL = config("FITNESS_FABRIK_BASE_URL")


    # Static and Class Methods defined with a simple question: 
    # Do I need this functionality on my instances it'self', if the answer is no: 
    @classmethod
    def instantiate_studios(cls) -> None: 
        '''
        This function instantiates a Studio object for each studio and adds it to the class's all_dict dictionary.
        studios = cls.__get_all_occupancy_data() retrieves all the studios and their data from the website by calling the __get_all_occupancy_data() method of the class.
        The for loop then iterates over each studio in the studios list, and extracts the row number, location, current number of people, and maximum number of people allowed for the studio.
        The cls.all_dict[location] = Studio(...) line creates a new Studio object with the extracted data and adds it to the all_dict dictionary with the location as the key.
        The last line logs a message indicating that all the studios were successfully instantiated.
        Overall, this method is responsible for initializing the Studio objects and making them available in the all_dict dictionary for other methods to use.
        '''
        studios = cls.__get_all_occupancy_data()
        for studio in studios:
            row_number = studio.get("row_number")
            location = studio.get("location")
            current = studio.get("current")
            maximum_people = studio.get("maximum_people")
            cls.all_dict[location] = Studio(document_table_row_number=row_number, location = location, current = current, maximum_people = maximum_people)
        request_cycle_logger.info("Successfull instantiated studios.")


    @classmethod
    def notify_on_people_amount_criteria(cls, time_interested_in, minimum: int = None, maximum: int = None, specific_studio_name = "", telegram_chat_id: str = "", recipient_name: str = ""):
        '''
        Parameters:
        * time_interested_in: a dictionary that specifies the time range the user is interested in being notified for a match, with keys "start" and "end".
        * minimum (optional): an integer representing the minimum number of people in the gym for the user to be interested in, default is None.
        * maximum (optional): an integer representing the maximum number of people in the gym for the user to be interested in, default is None (maximum will be fetched from the studio).
        * specific_studio_name (optional): a string representing the name of the studio to monitor, default is an empty string which means all studios.
        * telegram_chat_id: a string representing the Telegram chat ID of the user to send the notification to.
        * recipient_name: a string representing the name of the recipient of the notification.
        * Returns: None

        Description:
        This function continuously monitors the number of people in a gym (or a specific gym if specified) within a time range 
        specified by the user, and sends a message via Telegram to the user if the number of people meets their preferences (minimum and maximum).
        The function runs on an infinite loop and sleeps until the next check or until the notification is sent. The function requires a valid Telegram chat ID to send the notification.
        The function also logs relevant information, such as the current number of people in the gym and whether the criteria for the user's preference have been met.
        '''
        try:
            # Do some validation 
            assert cls.__check_location_exists(specific_studio_name), f"Specified studio name '{specific_studio_name}' is not valid!"
            if maximum == None: 
                maximum = cls.all_dict.get(specific_studio_name).maximum_people # The default value
            if time_interested_in.get("end") == None or time_interested_in.get("end") < time_interested_in.get("start"):
                time_interested_in["get"] = 23 # the default value 

            assert isinstance(maximum, int), f"The maximum of people in the gym must be a number larger 0."
            assert isinstance(minimum, int), f"The minimum of people in the gym must be larger 0 and smaller than {maximum}"
            assert telegram_chat_id != None, "Telegram chat ID is required in order to send the notification on telegram."
            assert time_interested_in.get("start") != None , "Please specifiy start time (in hours) you are intersted in getting notified for match."
            assert recipient_name != "", "Your name must be specified for the message."
            assert time_interested_in.get("start") <= time_interested_in.get("end"), "The start time you are interested in must be smaller or equal then the end time."
        except Exception as e: 
            root_logger.error(e, exc_info=True)
        else: 
            # Infinite loop to keep the process going 
            while True:   
                # Only do the checking between 5PM and 7PM 
                now = datetime.datetime.now() # German time format 0 - 24h
                # Time range the user is interested in and not sent and notification today
                if now.hour >= time_interested_in.get("start") and now.hour <= time_interested_in.get("end"):
                    studio_check_request = Studio.__check_occupancy(specific_studio_name=specific_studio_name, minimum=minimum, maximum=maximum)
                    root_logger.info(f'{now.strftime("%m/%d/%Y, %H:%M:%S")} {str(studio_check_request)}')
                    
                    # Criteria fullfilled -> send message
                    if studio_check_request.get("criteria_fullfilled") == True: 
                        # The default message
                        message = f"""
                        Hey {recipient_name}!
                        \nBereit, fit zu werden und Spaß zu haben? Komm zu uns ins Fitnessstudio in {studio_check_request.get("location")}!
                        \nAktuell sind nur {studio_check_request.get("current")} Leute hier, also kannst du dein Workout ohne Menschenmassen genießen.
                        \nVerpasse nicht die Gelegenheit, deine Gesundheit zu verbessern und neue Leute kennenzulernen!
                        \nWir sehen uns im Fitnessstudio!"
                        """.strip()
                        try:
                            # Actually got already status checking inside the function definiton
                            response = send_message(chat_id=telegram_chat_id, message = message)
                            assert response.status_code == 200, "Telegram message couldn't be sent."
                        except Exception as e: 
                            request_cycle_logger.error(e, exc_info=True)
                            sys.exit(1)
                        else: 
                            request_cycle_logger.info("Message was sent, sleep until next day.")
                            until_next_day = 24 - now.hour
                            time.sleep(until_next_day * 60 * 60)
                        
                        
                    # Criteria not fullfilled, wait 30 mins before requesting again 
                    else: 
                        request_cycle_logger.info(f"Sleep {REFRESH_CYCLE_TIME} minutes before making the next request.")
                        time.sleep(REFRESH_CYCLE_TIME * 60)
                # Important presumption is that start < end, made sure with validation 
                else: 
                        request_cycle_logger.info(f"Not in the time interval {time_interested_in.get('start')}:00-{time_interested_in.get('end')}:00 the user is interested in. Sleep until {time_interested_in.get('start')}:00!")
                        # Lets say the user is interested in 17h and it is 9h, then sleep 17 - 9 = 8 hours 
                        if(time_interested_in.get("start") > now.hour):
                            hours_difference = time_interested_in.get("start") - now.hour 
                            time.sleep(hours_difference * 60 * 60)
                        # lets say the user is intersted in 9h and it is 17h, then sleep 24 - 17 + 9 = 16 hours
                        else:
                            hours_difference = (24 - now.time) + time_interested_in.get("start")
                            time.sleep(hours_difference * 60 * 60)


    @classmethod
    def __pretty_print_studios(cls, specific_studio_name = "") -> None:
        # No specific studio name called: print all 
        if(specific_studio_name == ""):
            # vars() as __dict__, get the instance attributes of an instance as a dict
            print(json.dumps([vars(instance) for instance in cls.all_dict.values()], indent=4))

        else:
            # Get the studio entry for the specific name
            assert specific_studio_name in cls.all_dict, f"Error.{specific_studio_name} is not a valid studio name. No entry found for this."
            # TODO: maybe do a refetch of all entries
            specific_studio = cls.all_dict[specific_studio_name]
            # ! To build a dictionary from an arbitrary object, it's sufficient to use __dict__
            print(json.dumps(vars(specific_studio), indent=4)) # do the json formatted print 

    @classmethod 
    def __check_occupancy(cls, minimum: int = None, maximum: int = None, specific_studio_name = "") -> object:
        '''
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
        * criteria_fullfilled: a boolean value that represents if the criteria are fulfilled or not.
        * current: an integer that represents the current amount of people in the studio.
        '''
        # Check if the amount of current people inside the studio is between [minimum; maximum]
        def cb(studio) -> bool:
            '''
            Now do the acutal checking for the amount of people in the gym. 

            Studio in the format of: 
            {
                "location": location,
                "studio_row_number" : studio_row_number,
                "current": new_current,
                "maximum_people" : new_maximum_people
            }
            '''
            criteria_fullfilled = True

            try:
                # Valdiation, atleast Minimum or Maximum must be defined
                assert minimum != None and minimum < studio.get("maximum_people"), "Error. Minimum amount of people in Studio not set appropriately."
                assert maximum != None and maximum <= studio.get("maximum_people"), "Error. Minimum amount of people in Studio not set appropriately."
            except Exception as e:
                root_logger.error(f"There was an error with the Minimum and Maximum people amoutn in the Studio.{e}")
            else:
                current_people = studio.get("current")
                location = studio.get("location")
                # Check if minimum was specified 
                # current_people should be above minimum
                # Too less peope
                if(minimum):
                    assert isinstance(minimum, int), "The minimum for checking studio people must be an integer."
                    if current_people < minimum:
                        criteria_fullfilled = False
                

                # Check if maximum was specified
                # current_people should be below minimum
                # Too many people
                if(maximum):
                    assert isinstance(maximum, int), "The maximum for checking studio people must be an integer."
                    if(current_people > maximum):
                        criteria_fullfilled = False

                # Condition was fullfilled
                return {"location": location,  "minimum": minimum, "maximum": maximum, "criteria_fullfilled": criteria_fullfilled, "current": current_people}
        try:
            studio_criteria_check = cls.__get_occupancy_data(studio_name=specific_studio_name, cb=cb)
            assert studio_criteria_check != None, f"There was an Error with the criteria_fullfilled_result. It should be a boolean value, instead {studio_criteria_check.get('criteria_fullfilled')}!"
        except Exception as e:
            request_cycle_logger.error(e, exc_info=True)
        else:
            request_cycle_logger.info(f"Successfully checked if studio matches user defined criteria! ({'Yes' if studio_criteria_check.get('criteria_fullfilled') else 'No'})")
            return studio_criteria_check

    @staticmethod
    # @log
    def __get_occupancy_data(studio_name: str, cb = None):
        '''
        This is a static method called __get_occupancy_data in the Studio class. It updates the data of a specified studio, given the name of the studio.
        The method takes in two arguments, studio_name and cb. The studio_name argument is a string representing the name of the studio whose data is to be updated.
        The cb argument is an optional callback function that receives the fetched Studio data.
        The method first checks if the specified studio_name is valid by calling the __check_location_exists method, which checks if the studio is already saved.
        If the studio name is invalid, an error message is logged. If the studio name is valid, the method proceeds to fetch the data for the specified studio from a URL using the make_http_request function.
        The fetched data is then parsed using the BeautifulSoup library, and the relevant data is extracted from the parsed HTML. The studio data is then updated based on the fetched data.
        If a callback function was provided, it is called with the fetched studio data as an argument.
        The method is decorated with the @staticmethod decorator, which means that it can be called on the class itself and does not require an instance of the class to be created.
        '''
        try:
            # Check if the studio is already saved -- because we do fetch all in the beginning
            assert Studio.__check_location_exists(studio_name), f"Specified studio name '{studio_name}' is not valid!"
        except AssertionError as e:
            # If the studio name is invalid, just update all studios 
            # IMPORTANT: prints the program's location, the line where the error was encountered, and the name and relevant information about the error.
            root_logger.error(e, exc_info=True)
        else: 
            # old request made with @log decorator 
            # raw_html = make_http_request(url = Studio.__URL, config = {"show_parameters": True, "file_name": "http-requests-logs.txt", "return_value": False})
            raw_html = make_http_request(url = Studio.__URL)
            soup = BeautifulSoup(raw_html, 'html5lib')

            # Gives us the representation of the parse tree created from the raw html content
            '''
            Definition of 'parse Tree' / HTML structure of the document 
            An ordered, rooted tree representing the structure of a sentence, broken down to parts-of-speech
            '''

            # print(soup.prettify)

            # The data we are interested in are in table rows 
            data = soup.find("table", attrs = {'id': "meineTabelle"})
            table_body = data.tbody
            studios = table_body.find_all("tr")
        
            studio_row_number = Studio.all_dict.get(studio_name).document_table_row_number
            studio_data_rows = studios[studio_row_number].find_all('td')
            location, new_current, new_maximum_people =  Studio.__extract_studio_data_from_row(studio_data_rows).values()
            # Now update the studio data from the fetched data

            Studio.all_dict.get(location).current = new_current 
            Studio.all_dict.get(location).location = new_maximum_people 
            request_cycle_logger.info(f"Succesfull updated the updated the studio data of {studio_name}!")

            # OPTIONAL CALLBACK CALL WITH THE STUDIO DATA FETCHED 
            if(cb != None):
                cb_return_value = cb({"location": location, "studio_row_number" : studio_row_number, "current": new_current, "maximum_people" : new_maximum_people})
                return cb_return_value 
            
                                    
    @staticmethod
    def __get_all_occupancy_data():
        '''
        This is a private static method in the Studio class. The method __get_all_occupancy_data is used to fetch all the studios' data from a website and then instantiate a 
        Studio object for each studio and store them in a dictionary all_dict. It also determines the studio row number and name dict constant defined above.

        The method returns a list of dictionaries, where each dictionary represents a studio and contains the following keys:

        * row_number: The row number of the studio in the HTML table.
        * location: The location of the studio.
        * current: The number of people currently in the studio.
        * maximum_people: The maximum number of people that can be in the studio.
        The function starts by making an HTTP request to the website specified in Studio.__URL using the make_http_request function. It then parses the HTML document using the BeautifulSoup library and searches for the data we are interested in, which are in table rows. It extracts the data for each studio and instantiates an object with the data. Finally, it adds the studio object to the all_dict dictionary.

        Since this is a private static method, it can only be accessed within the Studio class, and it's not intended to be called outside of the class.
        '''

        # old request made with @log decorator 
        # raw_html = make_http_request(url=Studio.__URL, config = {"show_parameters": True, "file_name": "http-requests-logs.txt", "return_value": False})
        raw_html = make_http_request(url=Studio.__URL)
        # 2. Parsing the HMTL document 
        '''
        BeautifulSoup library is that it is built on the top of the HTML parsing libraries like html5lib, lxml, html.parser
        '''
        soup = BeautifulSoup(raw_html, 'html5lib')

        # Gives us the representation of the parse tree created from the raw html content
        '''
        Definition of 'parse Tree' / HTML structure of the document 
        An ordered, rooted tree representing the structure of a sentence, broken down to parts-of-speech
        '''
        # print(soup.prettify)

        # 3. Searching and navigating through the parse tree 

        # The data we are interested in are in table rows 
        data = soup.find("table", attrs = {'id': "meineTabelle"})
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
            studio = {"row_number": row_number, "location": location, "current": current, "maximum_people": maximum_people}
            studios.append(studio)
        return studios


    @staticmethod
    def __extract_studio_data_from_row(studio_row):
        '''
        This function takes in a list of table data cells containing data for a single studio, extracts the location, current occupancy, and maximum occupancy data from it,
        erforms some validation, and returns a dictionary containing the extracted data.
        The function first extracts the location data by stripping the leading and trailing whitespaces 
        and raises an assertion error if the location string is empty.
        It then tries to convert the maximum and current occupancy data from string to integers using the int() function 
        and catches a ValueError if the conversion fails. In case of an error, the function logs the error message using the root_logger object and includes the exception traceback information.
        Finally, if the data extraction and validation are successful, the function returns a dictionary containing the extracted data with the keys "location", "current", and "maximum_people".       
        '''

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
    def __check_location_exists(location: str) -> bool:
        return True if location in Studio.all_dict else False

    # ------------------- MAGIC METHODS -------------------
    def __init__(self, document_table_row_number: int, location: str, current: int, maximum_people: int):
        # VALIDATION
        try:
            assert isinstance(location, str), f"The given location '{location}' is not a string!"
            assert current >= 0, f"The amount of current people in the studio {self.current} cannot be less than 0!"
            assert maximum_people >= 0, f"The amount of the maximum people allowed in the studio {self.current} cannot be less than 0!"
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
    # @document_table_row_number.setter
    # def document_table_row_number(self, value: int):
    #     self.__document_table_row_number = value


    @location.setter
    def location(self, value: str):
        self.__location = value 
    
    @current.setter
    def current(self, value: int):
        self.__current = value 

    @maximum_people.setter
    def maximum_people(self, value: int):
        self.__maximum_people = value 

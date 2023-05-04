# 3rd Party libs
import json 
from bs4 import BeautifulSoup
from helper import make_http_request
import time
import datetime

# Own libs
from log import log
from telegrambot import send_message


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
    __URL = 'http://besucher.fitnessfabrik.de/'


    # Static and Class Methods defined with a simple question: 
    # Do I need this functionality on my instances it'self', if the answer is no: 
    @classmethod
    def instantiate_studios(cls) -> None: 
        studios = cls.__update_all_studio_data()
        for studio in studios:
            row_number = studio.get("row_number")
            location = studio.get("location")
            current = studio.get("current")
            maximum_people = studio.get("maximum_people")
            cls.all_dict[location] = Studio(document_table_row_number=row_number, location = location, current = current, maximum_people = maximum_people)


    @classmethod
    def notify_on_people_amount_criteria(cls, time_interested_in, minimum: int = None, maximum: int = None, specific_studio_name = "", telegram_chat_id: str = "", recipient_name: str = ""):
        '''
        Parameters it takes: notify_on_people_amount_criteria(cls, time_interested_in, minimum: int = None, maximum: int = None, specific_studio_name = "", telegram_chat_id: str = "", recipient_name: str = ""):
        Uses an infinite loop, to keep the send message process going. 
        Fetches / updates only the data needed for the specific studio (every 30 minutes). 
        Compares the amount of people inside the studio and check if the user preferences match (minimum, maximum) for the time he is interested in. 
        If match, send one message each day via telegram to the user. 
        '''

       
        notification_sent_today = False # Only send one message a day!
        


        # Do some validation 
        assert specific_studio_name in cls.all_dict, f"Specified studio name '{specific_studio_name}' is not valid!"
        if maximum == None: 
            maximum = cls.all_dict.get(specific_studio_name).maximum_people # The default value
        if time_interested_in.get("end") == None or time_interested_in.get("end") < time_interested_in.get("start"):
            time_interested_in["get"] = 23 # the default value 

        assert isinstance(maximum, int), f"The maximum of people in the gym must be a number larger 0."
        assert isinstance(minimum, int), f"The minimum of people in the gym must be larger 0 and smaller than {maximum}"
        assert telegram_chat_id != None, "Telegram chat ID is required in order to send the notification on telegram."
        assert time_interested_in.get("start") != None , "Please specifiy start time (in hours) you are intersted in getting notified for match."
        assert recipient_name != "", "Your name must be specified for the message."
        # Infinite loop to keep the process going 
        while True:   
            # Only do the checking between 5PM and 7PM 
            now = datetime.datetime.now() # German time format 0 - 24h
            if not notification_sent_today:  
                # Time range the user is interested in
                if now.hour >= time_interested_in.get("start") and now.hour <= time_interested_in.get("end"):
                    studio_check_request = Studio.__check_studio_people_on_criteria(specific_studio_name=specific_studio_name, minimum=minimum, maximum=maximum)
                    print(now.strftime("%m/%d/%Y, %H:%M:%S"), studio_check_request)

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
                        send_message(chat_id=telegram_chat_id, message = message)
                        notification_sent_today = True
                    # Criteria not fullfilled, wait 30 mins before requesting again 
                    else: 
                        time.sleep(REFRESH_CYCLE_TIME * 60)
                
            # Reset becuase the day passed by 
            if now.hour == 0:
                # TODO do some clean up, deleting the loging files and co. 
                notification_sent_today = False
    

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
    def __check_studio_people_on_criteria(cls, minimum: int = None, maximum: int = None, specific_studio_name = "") -> object:
        '''
        Check if the specific studio current people are either
        Over the minimum or below the maximum. 
        Return value: 
        {
            "location": str,
            "minimum": int,
            "maximum": int,
            "criteria_fullfilled": bool,
            "current": int
        }
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

            # Valdiation, atleast Minimum or Maximum must be defined
            assert minimum != None, "Error. Minimum must be specified for checking studio people!"
            assert maximum != None, "Error. Maximum must be specified for checking studio people!"


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
        return cls.__update_studio_data(studio_name=specific_studio_name, cb=cb)

    @staticmethod
    @log
    def __update_studio_data(studio_name: str, cb = None):
        '''
        After __update_all_studio_data() has initialized all studios, we use this function 
        to update the data of the studios we want.

        cb: function(Studio)
        an optional callback function that receives the fetched Studio data 
        '''
        try:
            # Check if the studio is already saved -- because we do fetch all in the beginning
            assert studio_name in Studio.all_dict, f"Specified studio name '{studio_name}' is not valid!"


            raw_html = make_http_request(url = Studio.__URL, config = {"show_parameters": True, "file_name": "http-requests-logs.txt", "return_value": False})
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
            # OPTIONAL CALLBACK CALL WITH THE STUDIO DATA FETCHED 
            if(cb != None):
                return_value = cb({"location": location, "studio_row_number" : studio_row_number, "current": new_current, "maximum_people" : new_maximum_people})
                return return_value
        except AssertionError as e:
            # If the studio name is invalid, just update all studios 
            # IMPORTANT: prints the program's location, the line where the error was encountered, and the name and relevant information about the error.
            return e
                                    
    @staticmethod
    def __update_all_studio_data():
        '''
        Fetches all the studios and instantiate for every studio one Studio instance
        Also responsible for determining the studio row number name dict constant defined above
        Initialization step

        Return value: 
        studios = [
            {
            row_number: int, 
            location: str, 
            current: int, 
            maximum_people: int
            }
        ]
        '''
        raw_html = make_http_request(url=Studio.__URL, config = {"show_parameters": True, "file_name": "http-requests-logs.txt", "return_value": False})

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
        Receives table Data cells, extract data and so some validation:
          [<td>
                Darmstadt            </td>, } location 
            <td>
                144            </td>, } maximum 
            <td>
                49            </td>] } current         
        '''

        # TODO: do some testing check if it is really location ...

        location = studio_row[0].text.strip()
        try:
            maximum_people = int(studio_row[1].text)
            current = int(studio_row[2].text)
        except ValueError as verr: 
            # failed to convert string to integer 
            print(f'Failed to convert string to integer: {verr}')

        assert location != "", "The location string is not allowed to be empty!"
        return {"location": location, "current": current, "maximum_people": maximum_people}

    # ------------------- MAGIC METHODS -------------------
    def __init__(self, document_table_row_number: int, location: str, current: int, maximum_people: int):
        # VALIDATION
        assert isinstance(location, str), f"The given location '{location}' is not a string!"
        assert current >= 0, f"The amount of current people in the studio {self.current} cannot be less than 0!"
        assert maximum_people >= 0, f"The amount of the maximum people allowed in the studio {self.current} cannot be less than 0!"

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

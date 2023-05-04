# 3rd Party libs
import json 
import requests 
from bs4 import BeautifulSoup

# Own libs
from log import log


# 1. HTTP request an URL to get the document 
URL = 'http://besucher.fitnessfabrik.de/'


class Studio: 
    '''
    Studio(document_table_row_number: int, location: str, current_people: int, maximum: int)
    '''
    all_dict = {} # listed studios based on the name 

    # Static and Class Methods defined with a simple question: 
    # Do I need this functionality on my instances it'self', if the answer is no: 

    @classmethod
    def instantiate_studios(cls) -> None: 
        studios = cls.fetch_all_studio_data()
        for studio in studios:
            # unpacking 
            row_number = studio.get("row_number")
            location = studio.get("location")
            current = studio.get("current")
            maximum_people = studio.get("maximum_people")
            cls.all_dict[location] = Studio(document_table_row_number=row_number, location = location, current = current, maximum_people = maximum_people)


    @staticmethod
    # @log
    def fetch_studio_data(studio_name: str):
        '''
        After fetch_all_studio_data() has initialized all studios, we use this function 
        to update the data of the studios we want. 
        '''
        raw_html = Studio.__make_http_request(url = URL, config = {"show_parameters": True, "file_name": "http-requests-logs.txt"})
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
        studios = table_body.find_all("tr")
        studio_row_number = Studio.all_dict[studio_name].document_table_row_number
        studio_data_rows = studios[studio_row_number].find_all('td')
        location, new_current, new_maximum_people =  Studio.__extract_studio_data_from_row(studio_data_rows)
        # Now update the studio data from the fetched data
        Studio.all_dict[location].current = new_current 
        Studio.all_dict[location].maximum_people = new_maximum_people 
    
    @staticmethod
    # @log
    def fetch_all_studio_data():
        '''
        Fetches all the studios and instantiate for every studio one Studio instance
        Also responsible for determining the studio row number name dict constant defined above
        Initialization step
        '''
        response = requests.get(URL)
        raw_html = response.content # type string 

        # 2. Parsing the HMTL document 
        '''
        BeautifulSoup library is that it is built on the top of the HTML parsing libraries like html5lib, lxml, html.parser
        '''

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

        # TODO WRITE IN JSON 
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

    @classmethod
    def pretty_print_studios(cls, studio_name = "") -> None:
        # No specific studio name called: print all 
        if(studio_name == ""):
            print(json.dumps([vars(instance) for instance in cls.all_dict.values()], sort_keys=True, indent=4))

        else:
            # Get the studio entry for the specific name
            assert studio_name in cls.all_dict, f"{studio_name} is not a valid studio name. No entry found for this."
            # TODO: maybe do a refetch of all entries
            specific_studio = cls.all_dict[studio_name]
            # ! To build a dictionary from an arbitrary object, it's sufficient to use __dict__
            print(json.dumps(vars(specific_studio), indent=4, sort_keys=True)) # do the json formatted print 


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

        return {location: location, current: current, maximum_people: maximum_people}
    

    @staticmethod
    @log
    def __make_http_request(url: str) -> str:
        # 1. Get the refresehed data,
        # 2. Update the 'self' values with the new data 
        response = requests.get(url)

        try:
            if response.status_code != 200:
                raise Exception(f"HTTP request failed to {url}; HTTP Status Code is '{response.status_code}'")
            raw_html = response.content # type string 
        except Exception as e:
            return e       
        return raw_html


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

    # ------------------- Functional methods -------------------
    def send_sms(self):
        pass


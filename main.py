from decouple import config

# Own classes 
from Studio import Studio 

TELEGRAM_CHAT_ID = config("MY_TELEGRAM_CHAT_ID")
Studio.instantiate_studios()


''''
CONFIGURATION
'''
TARGET_STUDIO = "Griesheim"
TARGET_MINIMUM = 70
MY_NAME = "Martin"
TIME_INTERESTED_IN = {"start": 17, "end": 18} # included [start, end + 1)


# internal On-going process (infinite while looop!)
Studio.notify_on_people_amount_criteria(time_interested_in= TIME_INTERESTED_IN, recipient_name= MY_NAME, minimum= TARGET_MINIMUM, maximum= None, specific_studio_name= TARGET_STUDIO, telegram_chat_id= TELEGRAM_CHAT_ID)
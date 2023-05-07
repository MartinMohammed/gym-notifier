from decouple import config

# Own classes 
from Studio import Studio 

TELEGRAM_CHAT_ID = config("MY_TELEGRAM_CHAT_ID")
Studio.instantiate_studios()


''''
DEFAULTL CONFIGURATION
'''
TARGET_STUDIO = "Griesheim"
TARGET_MINIMUM = 70
MY_NAME = "Martin"
TIME_INTERESTED_IN = {"start": 17, "end": 18} # included [start, end + 1)



try: 
    # SET UP THE PROGRAM -- GET THE REQUIRED INPUT 
    target_minimum = int(input("Please enter a target minimum of people in the studio: ")) 
    start_time = int(input("Please enter the start hour (e.g. 17h) you are interested in: "))
    end_time = int(input("Please enter the end hour (e.g. 21h) you are intersted in: "))
except Exception as e: 
    print(f"There was an error with receiving the configuration input:\n {e}")


# internal On-going process (infinite while looop!)
Studio.notify_on_people_amount_criteria(time_interested_in= TIME_INTERESTED_IN, recipient_name= MY_NAME, minimum= TARGET_MINIMUM, maximum= None, specific_studio_name= TARGET_STUDIO, telegram_chat_id= TELEGRAM_CHAT_ID)
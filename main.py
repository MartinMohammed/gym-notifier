from decouple import config
import sys

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


'''
Get the command line arguments from the bash script 
* argv[1] = The target minimum of people in the gym 
* argv[2] = The start hour of the gym 
* argv[3] = The end hour of the gym
'''


try:
    target_minimum = int(sys.argv[1])
    start_time = int(sys.argv[2])
    end_time = int(sys.argv[3])
except ValueError as e: 
    print(f"Please make sure that target_minimum, start_time and end_time are passed as numbers!\n{e}")
    # Set default values 
    target_minimum = TARGET_MINIMUM
    start_time = TIME_INTERESTED_IN.get("start")
    end_time = TIME_INTERESTED_IN.get("end")

Studio.notify_on_people_amount_criteria(time_interested_in= {"start": start_time, "end": end_time}, recipient_name= MY_NAME, minimum= target_minimum, maximum= None, specific_studio_name= TARGET_STUDIO, telegram_chat_id= TELEGRAM_CHAT_ID)



import sys
import time
from decouple import config

# Own classes 
from Studio import Studio 
import datetime
from telegrambot import send_message

TELEGRAM_CHAT_ID = config("MY_TELEGRAM_CHAT_ID")
Studio.instantiate_studios()


''''
CONFIGURATION
'''
TARGET_STUDIO = "Griesheim"
TARGET_MINIMUM = 70
MY_NAME = "Martin"
REFRESH_CYCLE_TIME = 30 #mins 
TIME_INTERESTED_IN = {"start": 17, "end": 19} # included [start, end]


# On-going process
while True:
    # Only do the checking between 5PM and 7PM 
    now = datetime.datetime.now() # German time format 0 - 24h
    notification_sent_today = False
    '''
    Only send one message a day!
    '''
    if not notification_sent_today:
        if now.hour >= TIME_INTERESTED_IN.start and now.hour <= TIME_INTERESTED_IN.end:
            studio_check_request = Studio.check_studio_people(specific_studio_name=TARGET_STUDIO, minimum=TARGET_MINIMUM)
            if studio_check_request.get("criteria_fullfilled") == True: 
                message = f"""
                Hey {MY_NAME}!
                \nBereit, fit zu werden und Spaß zu haben? Komm zu uns ins Fitnessstudio in {studio_check_request.get("location")}!
                \nAktuell sind nur {studio_check_request.get("current")} Leute hier, also kannst du dein Workout ohne Menschenmassen genießen.
                \nVerpasse nicht die Gelegenheit, deine Gesundheit zu verbessern und neue Leute kennenzulernen!
                \nWir sehen uns im Fitnessstudio!"
                """.strip()
                send_message(chat_id=TELEGRAM_CHAT_ID, message = message)
                notification_sent_today = True
        time.sleep(REFRESH_CYCLE_TIME * 60)
    
    # Reset becuase the day passed by 
    if now.hour == 0:
        # TODO do some clean up, deleting the loging files and co. 
        notification_sent_today = False
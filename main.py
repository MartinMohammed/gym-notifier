import time
from decouple import config

# Own classes 
from Studio import Studio 
from telegrambot import send_message

TELEGRAM_CHAT_ID = config("MY_TELEGRAM_CHAT_ID")
Studio.instantiate_studios()


''''
CONFIGURATION
'''
TARGET_STUDIO = "Griesheim"
TARGET_MINIMUM = 70

while True:
    time.sleep(1800) # Check every 30 mins if current people amount in the GYM has changed 
    studio_check_request = Studio.check_studio_people(specific_studio_name=TARGET_STUDIO, minimum=TARGET_MINIMUM)
    if studio_check_request.get("criteria_fullfilled") == True: 
        message = f"""
        Hey [X]!
        \nBereit, fit zu werden und Spaß zu haben? Komm zu uns ins Fitnessstudio in {studio_check_request.get("location")}!
        \nAktuell sind nur {studio_check_request.get("current")} Leute hier, also kannst du dein Workout ohne Menschenmassen genießen.
        \nVerpasse nicht die Gelegenheit, deine Gesundheit zu verbessern und neue Leute kennenzulernen!
        \nWir sehen uns im Fitnessstudio!"
        """.strip()
        send_message(chat_id=TELEGRAM_CHAT_ID, message = message)
    
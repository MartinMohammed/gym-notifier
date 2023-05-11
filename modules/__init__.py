import logging
import sys

# Importing functionalities from modules and 
# making them accessible to import from the parent directory

# Relative file imports
root_logger = logging.getLogger()
try:
    # from .helper import make_http_request
    from .helper import calculate_sleep_time_in_minutes
    from .Studio import Studio 
    from .telegrambot import send_message
except ImportError as iE:
    root_logger.critical("There was an error importing the modules inside the 'modules' package.")
    sys.exit(1)
else: 
    root_logger.info("Successfully imported the modules inside the 'modules' package.")

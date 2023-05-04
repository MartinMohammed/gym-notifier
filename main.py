import time

# Own classes 
from Studio import Studio 


Studio.instantiate_studios()
Studio.pretty_print_studios()


# Refresh and print every 15 seconds the data for Griesheim 
while True:
    time.sleep(5)
    Studio.fetch_studio_data("Griesheim")
    # Studio.pretty_print_studios("Griesheim")
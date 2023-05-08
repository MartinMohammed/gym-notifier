Sure, here's the same text in Markdown format:

### This Python program that web-scrapes

This Python program uses [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to traverse and search an HTML document, and extract the relevant data needed for the program. With Beautiful Soup, the program can extract specific elements and contents from HTML, XML, and other markup languages. The extracted data is then used to determine the current number of people training in the gym.

![An image of the Fitness Fabrik Website data](./images/Fitness-Fabrik-Web-Page.png){ width=50% }

### Telegram bot integration

The program also integrates a Telegram bot that sends messages to users whenever the gym occupancy meets the desired criteria (minimum and maximum). The bot is connected through an easy-to-implement API request to the Telegram server, which allows the community to interact with the bot in an automated way. By setting the criteria for the minimum and maximum number of people in the gym, users can receive notifications only when the gym occupancy meets their preferences.

![An image of the Fitness Fabrik Telegram Bot](./images/Fitness-Fabrik-Telegram-Bot.png){ width=50% }

Sure, here's the documentation in Markdown format:

# Fitness Fabrik Gym Occupancy Scraper Documentation

## Overview
This Python program web-scrapes the Fitness Fabrik gym website and uses Beautiful Soup to extract data about the current number of people training in the gym. It also includes integration with a Telegram bot to notify users when the gym occupancy meets their desired criteria.

## How it works
The program works by calling the `get_occupancy_data` function, which sends an HTTP request to the Fitness Fabrik website and retrieves the HTML content of the gym occupancy table. Beautiful Soup is then used to parse the HTML and extract the relevant data. The extracted data is validated and returned as a dictionary with the keys "location", "current", and "maximum_people".

The `instantiate_studios` function is then called, which instantiates `Studio` objects for each gym location and stores them in a dictionary with the location as the key.

The `check_occupancy` function is responsible for checking the current gym occupancy against the minimum and maximum criteria set by the user. If the occupancy meets the criteria, a message is sent to the user via the Telegram bot.

## Functions
### `get_occupancy_data`
This function sends an HTTP request to the Fitness Fabrik website and retrieves the HTML content of the gym occupancy table. It uses Beautiful Soup to parse the HTML and extract the relevant data. The extracted data is validated and returned as a dictionary with the keys "location", "current", and "maximum_people".

### `instantiate_studios`
This function instantiates `Studio` objects for each gym location and stores them in a dictionary with the location as the key.

### `check_occupancy`
This function checks the current gym occupancy against the minimum and maximum criteria set by the user. If the occupancy meets the criteria, a message is sent to the user via the Telegram bot.

## Telegram bot integration
The program integrates with a Telegram bot to notify users when the gym occupancy meets their desired criteria. Users can set the criteria for the minimum and maximum number of people in the gym, and receive notifications only when the gym occupancy meets their preferences.

## Images
The program includes two images to help illustrate the functionality. The first image shows the data displayed on the Fitness Fabrik website, and the second image shows the Telegram bot interface.
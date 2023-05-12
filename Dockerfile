# This line sets the base image as Python with version 3.11.3-bullseye installed
FROM python:3.11.3-bullseye

# This line creates a working directory inside the container 
WORKDIR /gym-tracker-app

# This line sets the timezone environment variable as Europe/Berlin
ENV TZ=Europe/Berlin

# This line copies the pip requirements package list to the working directory
COPY ./requirements.txt .

# This line copies the .env file to the working directory
COPY .env .

# Copy over the virtual environment
COPY ./venv ./venv

# This line copies the logging configuration file to the working directory
COPY logging.conf .

# This line copies the start script to the working directory
COPY ./start.sh .

# This line creates a 'logs' directory inside the working directory
RUN mkdir logs

# This line copies the application folder to the working directory
COPY ./app ./app

# This line sets the command to run the 'start.sh' script when the container is started
CMD ["bash", "start.sh"]
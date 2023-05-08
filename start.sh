#!/bin/bash
# --------------------- GET USER INPUT  ---------------------
echo -n "Welcome to the gym tracker program! Please enter your name: "
read name

echo -n "Please enter the name of the gym you want to track: "
read gym_name

echo -n "What is the minimum number of people you want to see in the gym? Please enter a number: "
read target_minimum

echo -n "What is the start time you are interested in tracking? Please enter the hour in 24-hour format (e.g. 17): "
read start_time

echo -n "What is the end time you are interested in tracking? Please enter the hour in 24-hour format (e.g. 21): "
read end_time

echo "Thank you, $name. The program will now track the gym from $start_time:00 to $end_time:00 and alert you if the number of people falls below $target_minimum."


# --------------------- CONFIGURATION & PACKAGE INSTALLATION---------------------


# if is a shell keyword that starts a conditional statement. If the condition in the statement is true, the commands in the then block are executed; otherwise, the commands in the else block (if present) are executed.
# ! is a shell operator that negates the exit status of a command. If the command succeeds (i.e., exits with a zero status), the ! operator turns the exit status to non-zero (1). If the command fails (i.e., exits with a non-zero status), the ! operator turns the exit status to zero.
# command is a shell command that searches for the specified command in the system's PATH and executes it if found. In this case, we're looking for the python3 command.
# -v is an option that tells the command command to print the full path to the command if found. If the command is not found, nothing is printed.
# python3 is the command we're looking for.
# &> /dev/null redirects both standard output (stdout) and standard error (stderr) of the command command to the null device (/dev/null). This means that any output or error messages produced by the command are discarded and not displayed on the console.

if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi


# $? = special shell variable, sotres the exit status of the last command that was executed in the shell (0 = successfull, else not)

# Make sure the venv environemt is activated
source "$PWD/bin/activate"

if [ $? -eq 0 ]; then
    echo "Venv environment was started succesfully."
else
    echo "There was an error in activating the venv python environment."
    exit 1
fi

# Make sure all required packages are installed
pip3 install -r "$PWD/requirements.txt"

if [ $? -eq 0 ]; then 
    echo "Required packages were installed succesfully."
else 
    exit 1
fi


# --------------------- RUN THE PROGRAM ---------------------

# Run the program as background process
python3 "$PWD/main.py" $name $gym_name $target_minimum $start_time $end_time
if [ $? -eq 0 ]; then
    echo "Program started successfully."
else 
    echo "There was an error running the Python script."
    exit 1
fi

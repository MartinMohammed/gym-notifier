#!/bin/bash
# Get the user input for the program to run 
echo -n "Please enter the target minimum of people in the gym: "
read target_minimum

echo -n "Please enter the start time you are interested (e.g. 17) in tracking the gym: "
read start_time

echo -n "Pleae enter the end time (e.g. 21) you are interested in tracking the gym: "
read end_time

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
fi

# Make sure the venv environemt is activated
source "$PWD/bin/activate"
if [ $? -eq 0 ]; then
    echo "Program was started successfully."
else 
    echo "There wa an error in running the python3 main.py program."
fi

# Run the program as background process
python3 "$PWD/main.py" $target_minimum $start_time $end_time &
if [ $? -eq 0 ]; then
    echo "Program started successfully."
else 
    echo "There was an error running the Python script."
fi

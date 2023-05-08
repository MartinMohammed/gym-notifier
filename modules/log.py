# Ensure that this moudle can only be imported and 
# cannot be run as the main program
if __name__ != "__main__":
    import os
    from datetime import datetime

    def log(cb):
        '''
        * Logs the input arguments of the function call : config['show_parameters'] : bool
        * Logs the output of the function call : config["return_value"] : bool
        * takes an optional message as kwarg arg : config["optional_message"] : str
        * destination file : config["file_name"] : str
        '''

        # call function(...) decorated with log = wrapper(...)
        '''
        for a variable amount of (positional)-arguments
        Args = arguments passed saved in a tuple (5, 10...)
        Kwargs = arguments passed with an key (a = 10, b = 15...)
        '''
        def wrapper(*args, config = {"file_name" : "logs.txt", "return_value" : True, "show_parameters": True}, **kwargs, ):
            now = datetime.now()
            # format as string
            time_str = now.strftime("%Y-%m-%d %H:%M:%S")

            return_value = cb(*args,**kwargs)
            args_string = " ,".join([str(arg) for arg in args])
            kwargs_string = " ,".join([f"{key} = {value}" for (key, value) in kwargs.items()])
            # Initialize context manager “
            with open(f"{os.getcwd()}/logs/" + config.get("file_name"), 'a') as log_file: 
                log_file.write("-----------------------------------------------------------------\n")
                log_file.write(f"The function {cb.__name__} was called with this args at timestamp {time_str}.\n")
                if config.get("show_parameters") == True: 
                    log_file.write(f"The input parameters were:\n" f"*Args : {args_string}\n" if len(args_string) != 0 else '' + f"*Kwargs : {kwargs_string}\n" if len(kwargs_string) != 0 else '')
                if config.get("optional_message") != None:
                    log_file.write(f"A optional message : " + config.get("optional_message") + "\n")
                if config.get("return_value") == True and return_value != None:
                    log_file.write(f"The return value : " + str(return_value) + "\n")
                log_file.write("-----------------------------------------------------------------\n")
            return return_value
        return wrapper 
    

elif __name__ == "__main__":
    print(f"This module cannot be ran as the main program, instead must be imported.")
# This module is ran as the main program 
if __name__ == "__main__":
    from decouple import config
    import sys
    import unittest
    import logging, logging.config
    import time
    logging.config.fileConfig("logging.conf")
    

     # ------------ DISOVER AND RUN ALL THE TEST CASES IN A GIVEN DIR ------------
    # responsible for loading the tests 
    test_loader = unittest.TestLoader()

    # Discover all the test caess in the directory that match the pattern 
    # Returns an TestSuite object that contains all the discovered tests
    test_suite = test_loader.discover(start_dir='./modules', pattern='test_*') 


    # test runner, runningn the tests and reporting the results
    test_runner = unittest.TextTestRunner() 
    
    # runs the the tests in the TestSuite object 
    # results are printed in the consule using text output.

    # test_result : TextTestReuslt object, which provides info.
    # about the test run, inclduing the number of tests run, the number
    # of failures and the number of errors
    root_logger = logging.getLogger()
        
    test_result = test_runner.run(test_suite)
    if not test_result.wasSuccessful():
        root_logger.critical(f"{test_result.failures} tests failed.")
        sys.exit(1)
    else: 
        root_logger.info("All tests passed.")
    # time.sleep(10)

    # Own classes 
    from modules import Studio 

    TELEGRAM_CHAT_ID = config("MY_TELEGRAM_CHAT_ID")
    Studio.instantiate_studios()

    # root_logger = logging.getLogger("root")
    request_cycle_logger = logging.getLogger("request_cycle")

    '''
    argv[1] = Your name
    argv[2] = The target minimum number of people in the gym
    argv[3] = The start hour of the gym
    argv[4] = The end hour of the gym
    '''

    try:
        name=sys.argv[1]
        gym_name = sys.argv[2]
        target_minimum = int(sys.argv[3])
        start_time = int(sys.argv[4])
        end_time = int(sys.argv[5])
    except Exception as e: 
        request_cycle_logger.critical(f"Entered notification program configuration input caused an error:\n{e}", exc_info=True)
    else:
        Studio.notify_on_people_amount_criteria(time_interested_in= {"start": start_time, "end": end_time}, recipient_name= name, minimum= target_minimum, maximum= None, specific_studio_name= gym_name, telegram_chat_id= TELEGRAM_CHAT_ID)
else: 
    print("This program must be ran as the main program.")
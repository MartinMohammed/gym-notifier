
import datetime
import unittest
from helper import calculate_sleep_time_in_minutes



from decouple import config

class TestHelper(unittest.TestCase):

    # Before every test - once
    @classmethod 
    def setUpClass(cls):
        pass

    # After every test - once
    @classmethod 
    def tearDownClass(cls) -> None:
        pass

    # Before any case
    def setUp(self):
        pass
    
    # After any case
    def tearDown(self):
        pass

    # def test_make_http_request(self):
    #     with patch("helper.make_http_request") as mocked_get:
    #         # Set properties on the mocked object -- return props 
    #         mocked_get.return_value.status_code = 200
    #         mocked_get.return_value.content = b"<h2>Success</h2>"

    #         # Run the function 
    #         raw_html = make_http_request(config("FITNESS_FABRIK_BASE_URL"))

    #         # Check function call parameters
    #         mocked_get.assert_called_with(config("FITNESS_FABRIK_BASE_URL"))

    #         # Check the return value of the function call 
    #         self.assertEqual(raw_html, b"<h2>Success</h2>")


    def test_calculate_sleep_time_in_minutes(self):
        # ----------------- START_TIME > CURRENT_TIME = SAME DAY-----------------
        time_interested_in = {"start": 17, "end": 9}
        current_time = datetime.datetime.now()
        next_day = time_interested_in.get("start") > current_time.hour # should be False

        # create a new datetime object with the same year, month, day, hour and second, but with minutes set to 40
        custom_datetime = datetime.datetime(current_time.year, current_time.month, current_time.day, 15, 40, current_time.second)

        result = calculate_sleep_time_in_minutes(time_interested_in=time_interested_in, current_time=custom_datetime, next_day=next_day)
        self.assertEqual(result, 80)

        # ----------------- START_TIME < CURRENT_TIME = NEXT DAY-----------------
        time_interested_in["start"] = 9 # 09:00

        next_day = time_interested_in.get("start") > current_time.hour # should be True
        result = calculate_sleep_time_in_minutes(time_interested_in=time_interested_in, current_time=custom_datetime, next_day=next_day)
        self.assertEqual(result, (60 - custom_datetime.minute) + (24 - custom_datetime.hour - 1) * 60) # minutes until 00:00


# If manually running this test file 

if __name__ == "__main__":
    # Run every testcase in this moudle
    unittest.main()
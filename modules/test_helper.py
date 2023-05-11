
import datetime
import unittest
from helper import calculate_sleep_time_in_minutes


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

    def test_calculate_sleep_time_in_minutes(self):
        # ----------------- START_TIME > CURRENT_TIME = SAME DAY-----------------
        time_interested_in = {"start": 17, "end": 9}
        # create a new datetime object with the same year, month, day, hour and second, but with minutes set to 40
        current_time = datetime.datetime.now()
        custom_datetime = datetime.datetime(
            current_time.year, current_time.month, current_time.day, 15, 40, current_time.second)


        result = calculate_sleep_time_in_minutes(
            time_interested_in=time_interested_in, current_time=custom_datetime)
        self.assertEqual(result, 80)

        # ----------------- START_TIME < CURRENT_TIME = NEXT DAY-----------------
        time_interested_in["start"] = 9  # 09:00

        result = calculate_sleep_time_in_minutes(
            time_interested_in=time_interested_in, current_time=custom_datetime)
        self.assertEqual(
            result, (60 - custom_datetime.minute) + (24 - custom_datetime.hour - 1) * 60)  # minutes until 00:00


# If manually running this test file 

if __name__ == "__main__":
    # Run every testcase in this module
    unittest.main()

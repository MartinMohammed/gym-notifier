# import unittest
# from unittest.mock import patch 
# from "../helper.py" import make_http_request
# from decouple import config

# class TestHelper(unittest.TestCase):

#     # Before every test
#     @classmethod 
#     def setUpClass(cls):
#         pass

#     # After every test 
#     @classmethod 
#     def tearDownClass(cls) -> None:
#         pass

#     # Before any case
#     def setUp(self):
#         pass
    
#     # After any case
#     def tearDown(self):
#         pass

#     def test_make_http_request(self):
#         with patch("make_http_request.get") as mocked_get:
#             # Set properties on the mocked object -- return props 
#             mocked_get.return_value.status_code = 200
#             mocked_get.return_value.content = "<h2>Success</h2>"

#             # Run the function 
#             raw_html = make_http_request(config("FITNESS_FABRIK_BASE_URL"))

#             # Check function call parameters
#             mocked_get.assert_called_with(config("FITNESS_FABRIK_BASE_URL"))

#             # Check the reutrn value of the function call 
#             self.assertEqual(raw_html, "<h2>Success</h2>")


# if __name__ == "__main__":
#     # Run every testcase in this moudle
#     unittest.main()
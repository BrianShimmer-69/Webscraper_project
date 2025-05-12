################################################################################
#                                                                              #  
#                                  Unittests                                   #                                     
#                                                                              #  
#  36122 Python Programming - 1st Semester 2025                                #
#                                                                              #  
#  Dan Hansen                    - Student ID 24718999                         #  
#  Brian Shimmer Bino Deva Kumar - Student ID 25752306                         #  
#  David Pawley                  - Student ID 92072368                         #  
#  Maximus Chandrasekaran        - Student ID 25614189                         #  
#                                                                              #  
################################################################################

import unittest
from Assignment_36122_Group_17 import NewsScraper
import tkinter as tk
from datetime import datetime

class TestNewsScraper(unittest.TestCase):

    def setUp(self):
        root = tk.Tk()
        self.app = NewsScraper(root)

    def test_get_api_ratio(self):
        self.assertEqual(self.app.get_api_ratio(4,6), 0.4)
        self.assertEqual(self.app.get_api_ratio(2,6), 0.25)
        self.assertEqual(self.app.get_api_ratio(0,0), None)

    def test_get_date_info(self):
        list1 = [datetime(2025, 5, 10, 11, 23), datetime(2025, 5, 9, 10, 23), datetime(2025, 5, 8, 8, 58), datetime(2025, 5, 5, 6, 23)]
        list2 = [datetime.now(), datetime.now()]
        list3 = ['a', 'b', 'c']
        list4 = [datetime(2025, 5, 10, 11, 23)]
        self.assertEqual(self.app.get_date_info([]), (None,None))
        self.assertEqual(self.app.get_date_info(list1), (datetime(2025, 5, 5, 6, 23),datetime(2025, 5, 10, 11, 23)))
        self.assertEqual(self.app.get_date_info(list2), (datetime.now(), datetime.now()))
        self.assertEqual(self.app.get_date_info(list3), (None,None))
        self.assertEqual(self.app.get_date_info(list4), (datetime(2025, 5, 10, 11, 23),datetime(2025, 5, 10, 11, 23)))

if __name__ == "__main__":
    unittest.main()

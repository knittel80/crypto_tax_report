#!/usr/bin/python3

import unittest
import crypto_tax_report
from crypto_tax_report import datetime

def get_test_raw_data_entries():
    return [[r'2021-12-02 04:10:03',r'Card Cashback',r'CRO',r'0.02827009',r'',r'',r'EUR',r'0.02',r'0.0219808333',r'referral_card_cashback',r'']]


# Create a test class
class TestRawDataConversions(unittest.TestCase):

    # Test case 1: parsing the date time string into an datetime object
    def test_get_date_time_object(self):
        raw_date_time = r'2021-12-02 04:10:03'       
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(raw_date_time)
        self.assertTrue(parse_successful)
        self.assertEqual(parse_result.year, 2021)
        self.assertEqual(parse_result.month, 12)
        self.assertEqual(parse_result.day, 2)
        self.assertEqual(parse_result.hour, 4)
        self.assertEqual(parse_result.minute, 10)
        self.assertEqual(parse_result.second, 3)

    # Test case 2: parsing fails because of a corrupt or invalid date time 
    def test_get_date_time_object_corrupt_string(self):
        # 1st: parts of string do not convert to int
        invalid_raw_date_time = r'20u21-12-02 04:10:03'       
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)
        # 2nd: the number for the month is invalid
        invalid_raw_date_time = r'2021-13-03 04:10:03'       
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)
        # 3rd: the number for the day is invalid
        invalid_raw_date_time = r'2021-12-33 04:10:03'       
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)
        # 4th: the number for the hour is invalid
        invalid_raw_date_time = r'2021-12-23 25:10:03'       
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)
        # 5th: the number for the minute is invalid
        invalid_raw_date_time = r'2021-12-23 23:60:03'       
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)
        # 6th: the number for the second is invalid
        invalid_raw_date_time = r'2021-12-23 23:50:63'       
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)




        

if __name__ == '__main__':
    unittest.main()


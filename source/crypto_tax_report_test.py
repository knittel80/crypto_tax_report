#!/usr/bin/python3

import unittest
import crypto_tax_report
from crypto_tax_report import datetime


def get_test_raw_data_entries():
    return [[r'2021-12-02 04:10:03', r'Card Cashback', r'CRO', r'0.02827009', r'', r'', r'EUR', r'0.02', r'0.0219808333', r'referral_card_cashback', r'']]


# Create a test class
class TestRawDataConversions(unittest.TestCase):

    # Test case 1: parsing the date time string into an datetime object
    def test_get_date_time_object(self):
        raw_date_time = r'2021-12-02 04:10:03'
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(
            raw_date_time)
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
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(
            invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)
        # 2nd: the number for the month is invalid
        invalid_raw_date_time = r'2021-13-03 04:10:03'
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(
            invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)
        # 3rd: the number for the day is invalid
        invalid_raw_date_time = r'2021-12-33 04:10:03'
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(
            invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)
        # 4th: the number for the hour is invalid
        invalid_raw_date_time = r'2021-12-23 25:10:03'
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(
            invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)
        # 5th: the number for the minute is invalid
        invalid_raw_date_time = r'2021-12-23 23:60:03'
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(
            invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)
        # 6th: the number for the second is invalid
        invalid_raw_date_time = r'2021-12-23 23:50:63'
        parse_successful, parse_result = crypto_tax_report.get_date_time_object(
            invalid_raw_date_time)
        self.assertFalse(parse_successful)
        self.assertEqual(parse_result, None)

    def test_match_buy_crypto_currency_with_euro(self):
        match_successful = crypto_tax_report.match_buy_crypto_currency_with_euro(
            r'EUR -> ADA')
        self.assertTrue(match_successful)
        match_successful = crypto_tax_report.match_buy_crypto_currency_with_euro(
            r'   EUR   ->    CRO  ')
        self.assertTrue(match_successful)
        # Test cases where the match is unsuccessful
        match_successful = crypto_tax_report.match_buy_crypto_currency_with_euro(
            r'CRO -> ADA')
        self.assertFalse(match_successful)
        match_successful = crypto_tax_report.match_buy_crypto_currency_with_euro(
            r'CRO -> EUR')
        self.assertFalse(match_successful)
        match_successful = crypto_tax_report.match_buy_crypto_currency_with_euro(
            r'Random content!!')
        self.assertFalse(match_successful)

    def test_match_sell_crypto_currency_get_euro(self):
        match_successful = crypto_tax_report.match_sell_crypto_currency_get_euro(
            r'CRO -> EUR')
        self.assertTrue(match_successful)
        match_successful = crypto_tax_report.match_sell_crypto_currency_get_euro(
            r'   ETH   ->    EUR  ')
        self.assertTrue(match_successful)
        # Test cases where the match is unsuccessful
        match_successful = crypto_tax_report.match_sell_crypto_currency_get_euro(
            r'CRO -> ADA')
        self.assertFalse(match_successful)
        match_successful = crypto_tax_report.match_sell_crypto_currency_get_euro(
            r'EUR -> ETH')
        self.assertFalse(match_successful)
        match_successful = crypto_tax_report.match_sell_crypto_currency_get_euro(
            r'Random content!!')
        self.assertFalse(match_successful)

    def test_match_swap_of_crypto_currency(self):
        match_successful = crypto_tax_report.match_swap_of_crypto_currency(
            r'CRO -> ADA')
        self.assertTrue(match_successful)
        match_successful = crypto_tax_report.match_swap_of_crypto_currency(
            r'   ETH   ->    SOL  ')
        self.assertTrue(match_successful)
        # Test cases where the match is unsuccessful
        match_successful = crypto_tax_report.match_swap_of_crypto_currency(
            r'CRO -> EUR')
        self.assertFalse(match_successful)
        match_successful = crypto_tax_report.match_swap_of_crypto_currency(
            r'EUR -> ETH')
        self.assertFalse(match_successful)
        match_successful = crypto_tax_report.match_swap_of_crypto_currency(
            r'Random content!!')
        self.assertFalse(match_successful)


class CryptoAquisitionDataTest(unittest.TestCase):

    # Set up the test environment
    def setUp(self):
        # Initialize an instance of the class to be tested
        self.crypto_aquisition_data = crypto_tax_report.CryptoAquisitionData()

    @staticmethod
    def getTestData():
        test_data = [
            ["2021-05-20 12:57:28", "EUR -> ADA", "EUR", "-316.61", "ADA",
                "200.0", "EUR", "316.61", "347.96758155565", "viban_purchase",],
            ["2021-05-29 19:57:07", "EUR -> CRO", "EUR", "-19.91", "CRO",
             "220.0", "EUR", "19.91", "21.88191955015", "viban_purchase",],
            ["2021-06-27 12:41:01", "EUR -> ADA", "EUR", "-107.59", "ADA",
             "100.0", "EUR", "107.59", "118.24589273735", "viban_purchase",],
            ["2021-09-13 13:58:02", "EUR -> CRO", "EUR", "-765.64", "CRO",
             "5000.0", "EUR", "765.64", "841.4702603906", "viban_purchase",],
            ["2021-09-15 13:33:07", "EUR -> CRO", "EUR", "-800.38", "CRO",
             "5000.0", "EUR", "800.38", "879.6509678327", "viban_purchase",],
            ["2021-11-13 12:01:01", "EUR -> SOL", "EUR", "-15.03", "SOL",
             "0.075", "EUR", "15.03", "16.51859622495", "viban_purchase",],
        ]
        return test_data

    def assert_crypto_aquisition_data_entry(self, crypto_aquisition_data_entry, raw_data_entry):
        expected_date_time = crypto_tax_report.get_date_time_object(
            raw_data_entry[crypto_tax_report.Heading.TIMESTAMP.value])
        self.assertEqual(expected_date_time,
                         crypto_aquisition_data_entry.date_time)
        self.assertEqual(float(
            raw_data_entry[crypto_tax_report.Heading.TARGET_AMOUNT.value]), crypto_aquisition_data_entry.amount)
        self.assertEqual(float(
            raw_data_entry[crypto_tax_report.Heading.NATIVE_CURRENCY_AMOUNT.value]), crypto_aquisition_data_entry.bought_at)

    # Test case: Test the 'add' method
    def test_add(self):
        test_data = CryptoAquisitionDataTest.getTestData()
        for item in test_data:
            self.crypto_aquisition_data.add(item)

        # Assert the expected result
        self.assertEqual(len(self.crypto_aquisition_data.data_set), 3)
        self.assertEqual(len(self.crypto_aquisition_data.data_set['CRO']), 3)
        # check all three entries
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['CRO'][0], test_data[1])
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['CRO'][1], test_data[3])
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['CRO'][2], test_data[4])
        self.assertEqual(len(self.crypto_aquisition_data.data_set['ADA']), 2)
        # check all two ADA entries
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['ADA'][0], test_data[0])
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['ADA'][1], test_data[2])
        self.assertEqual(len(self.crypto_aquisition_data.data_set['SOL']), 1)
        # check the SOL entry
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['SOL'][0], test_data[-1])

    # Test case: Test the 'add' method, but do not add the entries according to their chronological order
    def test_add_unsorted(self):
        test_data = CryptoAquisitionDataTest.getTestData()
        for item in reversed(test_data):
            self.crypto_aquisition_data.add(item)  # add in reverse order

        # Assert the expected result
        self.assertEqual(len(self.crypto_aquisition_data.data_set), 3)
        self.assertEqual(len(self.crypto_aquisition_data.data_set['CRO']), 3)
        # check all three entries
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['CRO'][0], test_data[1])
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['CRO'][1], test_data[3])
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['CRO'][2], test_data[4])
        self.assertEqual(len(self.crypto_aquisition_data.data_set['ADA']), 2)
        # check all two ADA entries
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['ADA'][0], test_data[0])
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['ADA'][1], test_data[2])
        self.assertEqual(len(self.crypto_aquisition_data.data_set['SOL']), 1)
        # check the SOL entry
        self.assert_crypto_aquisition_data_entry(
            self.crypto_aquisition_data.data_set['SOL'][0], test_data[-1])

    @staticmethod
    def getTestDataForRemoval():
        add_data = [
            ["2021-05-20 12:57:28", "EUR -> ADA", "EUR", "-300.0", "ADA",
                "200.0", "EUR", "300.0", "330.0", "viban_purchase",],
            ["2021-05-29 19:57:07", "EUR -> CRO", "EUR", "-20.0", "CRO",
             "200.0", "EUR", "20.00", "21.2", "viban_purchase",],
            ["2021-06-27 12:41:01", "EUR -> ADA", "EUR", "-100.0", "ADA",
             "100.0", "EUR", "100.0", "110.0", "viban_purchase",],
            ["2021-09-13 13:58:02", "EUR -> CRO", "EUR", "-1000.0", "CRO",
             "5000.0", "EUR", "1000.0", "1100.0", "viban_purchase",],
            ["2021-09-15 13:33:07", "EUR -> CRO", "EUR", "-800.0", "CRO",
             "2000.0", "EUR", "800.0", "880.0", "viban_purchase",],
        ]
        remove_data = [
            ["2021-05-30 10:24:33", "ADA -> EUR", "ADA", "-100.0", "EUR",
                "200.0", "EUR", "200.0", "220.0", "crypto_viban_exchange",],
            ["2022-01-20 10:29:03", "ADA -> EUR", "ADA", "-125.0", "EUR",
             "200.0", "EUR", "200.0", "220.0", "crypto_viban_exchange",],
            ["2022-01-28 08:11:13", "CRO -> EUR", "ADA", "-4000.0", "EUR",
             "2000.0", "EUR", "2000.0", "2200.0", "crypto_viban_exchange",]
        ]

        return (add_data, remove_data)

    def test_remove(self):

        add_data, remove_data = CryptoAquisitionDataTest.getTestDataForRemoval()
        for item in add_data:
            self.crypto_aquisition_data.add(item)
        for item in remove_data:
            self.crypto_aquisition_data.remove(item)

        # Assert the expected result
        self.assertEqual(len(self.crypto_aquisition_data.data_set), 2)


if __name__ == '__main__':
    unittest.main()

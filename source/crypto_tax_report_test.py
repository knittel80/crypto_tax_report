#!/usr/bin/python3

"""
This file provides unit tests for the functionality within the module crypto_tax_report.
"""

# pylint: disable=C0115,C0116

import unittest
import crypto_tax_report
from crypto_tax_report import datetime, CryptoAcquisitionRecord, logger

# Create a test class
class TestRawDataConversions(unittest.TestCase):

    # Test case 1: parsing the date time string into an datetime object
    def test_get_date_time_object(self):
        raw_date_time = r'2021-12-02 04:10:03'
        parse_result = crypto_tax_report.get_date_time_object(raw_date_time)
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
        with self.assertRaises(ValueError):
            crypto_tax_report.get_date_time_object(invalid_raw_date_time)
        # 2nd: the number for the month is invalid
        invalid_raw_date_time = r'2021-13-03 04:10:03'
        with self.assertRaises(ValueError):
            crypto_tax_report.get_date_time_object(invalid_raw_date_time)
        # 3rd: the number for the day is invalid
        invalid_raw_date_time = r'2021-12-33 04:10:03'
        with self.assertRaises(ValueError):
            crypto_tax_report.get_date_time_object(invalid_raw_date_time)
        # 4th: the number for the hour is invalid
        invalid_raw_date_time = r'2021-12-23 25:10:03'
        with self.assertRaises(ValueError):
            crypto_tax_report.get_date_time_object(invalid_raw_date_time)
        # 5th: the number for the minute is invalid
        invalid_raw_date_time = r'2021-12-23 23:60:03'
        with self.assertRaises(ValueError):
            crypto_tax_report.get_date_time_object(invalid_raw_date_time)
        # 6th: the number for the second is invalid
        invalid_raw_date_time = r'2021-12-23 23:50:63'
        with self.assertRaises(ValueError):
            crypto_tax_report.get_date_time_object(invalid_raw_date_time)

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



class SimplePurchaseData:
    @staticmethod
    def as_raw():
        """
        This static method returns a list of lists, where each list represents
        a single purchase of a crypto currency.
        """
        crypto_purchase_data = [
            ["2021-05-20 12:57:28", "EUR -> ADA", "EUR", "-300.0", "ADA",
                "200.0", "EUR", "300.0", "330.0", "viban_purchase",],
            ["2021-05-29 19:57:07", "EUR -> CRO", "EUR", "-20.0", "CRO",
             "200.0", "EUR", "20.00", "21.2", "viban_purchase",],
            ["2021-06-27 12:41:01", "EUR -> ADA", "EUR", "-100.0", "ADA",
             "100.0", "EUR", "100.0", "110.0", "viban_purchase",],
            ["2021-09-13 13:58:02", "EUR -> CRO", "EUR", "-1000.0", "CRO",
             "5000.0", "EUR", "1000.0", "1100.0", "viban_purchase",],
            ["2021-09-15 13:33:07", "EUR -> CRO", "EUR", "-800.0", "CRO",
             "2000.0", "EUR", "800.0", "880.0", "viban_purchase",]
        ]
        return crypto_purchase_data

    @staticmethod
    def as_crypto_acquisition_data():
        """
        This static method converts the raw purchase data into a format suitable
        for crypto acquisition tracking.
        Returns:
            A CryptoAcquisitionData instance populated with the purchase records.
        """
        crypto_acquisition_data = crypto_tax_report.CryptoAquisitionData()
        for item in SimplePurchaseData.as_raw():
            crypto_acquisition_data.add(item)
        return crypto_acquisition_data

class CryptoAquisitionDataTest(unittest.TestCase):

    # Set up the test environment
    def setUp(self):
        logger.info("Entering the test case %s.", self._testMethodName)
        # Initialize an instance of the class to be tested
        self.crypto_acquisition_data = crypto_tax_report.CryptoAquisitionData()

    def tearDown(self) -> None:
        logger.info("Leaving the test case %s.", self._testMethodName)

    @staticmethod
    def get_crypto_purchase_data():
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
            raw_data_entry[crypto_tax_report.Heading.TARGET_AMOUNT.value]),
            crypto_aquisition_data_entry.amount
            )
        self.assertEqual(float(
            raw_data_entry[crypto_tax_report.Heading.NATIVE_CURRENCY_AMOUNT.value]),
            crypto_aquisition_data_entry.bought_at
            )

    # Test case: Test the 'add' method
    def test_add(self):
        test_data = CryptoAquisitionDataTest.get_crypto_purchase_data()
        for item in test_data:
            self.crypto_acquisition_data.add(item)

        # Assert the expected result
        self.assertEqual(len(self.crypto_acquisition_data.data_set), 3)
        self.assertEqual(len(self.crypto_acquisition_data.data_set['CRO']), 3)

        # check the three CRO entries
        reference_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 5, 29, 19, 57, 7),
            amount = 220.0,
            bought_at = 19.91
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['CRO'][0], reference_record)

        reference_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 9, 13, 13, 58, 2),
            amount = 5000.0,
            bought_at = 765.64
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['CRO'][1], reference_record)

        reference_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 9, 15, 13, 33, 7),
            amount = 5000.0,
            bought_at = 800.38
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['CRO'][2], reference_record)

        # check the two ADA entries
        self.assertEqual(len(self.crypto_acquisition_data.data_set['ADA']), 2)

        reference_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 5, 20, 12, 57, 28),
            amount = 200.0,
            bought_at = 316.61
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['ADA'][0], reference_record)

        reference_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 6, 27, 12, 41, 1),
            amount = 100.0,
            bought_at = 107.59
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['ADA'][1], reference_record)

        # check the two SOL entry
        self.assertEqual(len(self.crypto_acquisition_data.data_set['SOL']), 1)

        reference_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 11, 13, 12, 1, 1),
            amount = 0.075,
            bought_at = 15.03
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['SOL'][0],
                         reference_record
                         )

    def test_add_unsorted(self):
        """ Test case: Test the 'add' method, but with unsorted input data.
            The aquisition for each crypto currency should be ordered again.
        """
        test_data = CryptoAquisitionDataTest.get_crypto_purchase_data()
        for item in reversed(test_data):
            self.crypto_acquisition_data.add(item)  # add in reverse order

        # Assert the expected result
        self.assertEqual(len(self.crypto_acquisition_data.data_set), 3)
        self.assertEqual(len(self.crypto_acquisition_data.data_set['CRO']), 3)

        # check the three CRO entries
        reference_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 5, 29, 19, 57, 7),
            amount = 220.0,
            bought_at = 19.91
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['CRO'][0], reference_record)

        reference_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 9, 13, 13, 58, 2),
            amount = 5000.0,
            bought_at = 765.64
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['CRO'][1], reference_record)

        reference_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 9, 15, 13, 33, 7),
            amount = 5000.0,
            bought_at = 800.38
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['CRO'][2], reference_record)

        # check the two ADA entries
        self.assertEqual(len(self.crypto_acquisition_data.data_set['ADA']), 2)

        reference_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 5, 20, 12, 57, 28),
            amount = 200.0,
            bought_at = 316.61
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['ADA'][0], reference_record)

        reference_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 6, 27, 12, 41, 1),
            amount = 100.0,
            bought_at = 107.59
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['ADA'][1], reference_record)

        # check the two SOL entry
        self.assertEqual(len(self.crypto_acquisition_data.data_set['SOL']), 1)

        reference_record = CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 11, 13, 12, 1, 1),
            amount = 0.075,
            bought_at = 15.03
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['SOL'][0], reference_record)

    @staticmethod
    def get_testdata_for_crypto_sale():
        sale_data = [
            ["2021-05-30 10:24:33", "ADA -> EUR", "ADA", "-100.0", "EUR",
                "200.0", "EUR", "200.0", "220.0", "crypto_viban_exchange",],
            ["2022-01-20 10:29:03", "ADA -> EUR", "ADA", "-125.0", "EUR",
             "200.0", "EUR", "200.0", "220.0", "crypto_viban_exchange",],
            ["2022-01-28 08:11:13", "CRO -> EUR", "CRO", "-4000.0", "EUR",
             "2000.0", "EUR", "2000.0", "2200.0", "crypto_viban_exchange",]
        ]
        # Define your key-value pairs
        key_value_pairs = [
            ("ADA", [CryptoAcquisitionRecord(datetime.datetime(2021,6,27,12,41,1), 75., 75)]),
            ("CRO", [
                CryptoAcquisitionRecord(datetime.datetime(2021,9,13,13,58,2), 1200., 240.),
                CryptoAcquisitionRecord(datetime.datetime(2021,9,15,13,33,7), 2000., 800.)
                ]
            )
        ]
        # Create a dictionary using a dictionary comprehension
        expected_remaining_crypto_assets = dict(key_value_pairs)
        return (sale_data, expected_remaining_crypto_assets)

    def test_remove(self):
        # Arrange
        self.crypto_acquisition_data = SimplePurchaseData.as_crypto_acquisition_data()
        # Act
        crypto_sale_data, expected_remaining_crypto_assets = \
            CryptoAquisitionDataTest.get_testdata_for_crypto_sale()
        for item in crypto_sale_data:
            self.crypto_acquisition_data.remove(item)
        # Assert
        self.assertEqual(
            len(self.crypto_acquisition_data.data_set['ADA']),
            len(expected_remaining_crypto_assets['ADA'])
        )
        self.assertEqual(
            self.crypto_acquisition_data.data_set['ADA'],
            expected_remaining_crypto_assets['ADA']
        )
        self.assertEqual(
            len(self.crypto_acquisition_data.data_set['CRO']),
            len(expected_remaining_crypto_assets['CRO'])
        )
        self.assertEqual(
            self.crypto_acquisition_data.data_set['CRO'],
            expected_remaining_crypto_assets['CRO']
        )

    @staticmethod
    def get_testdata_for_sale_of_full_purchase_positions():
        sale_data = [
            ["2021-05-30 10:24:33", "ADA -> EUR", "ADA", "-200.0", "EUR",
                "400.0", "EUR", "400.0", "440.0", "crypto_viban_exchange",],
            ["2022-01-28 08:11:13", "CRO -> EUR", "CRO", "-200.0", "EUR",
             "100.0", "EUR", "100.0", "110.0", "crypto_viban_exchange",]
        ]
        # Define your key-value pairs
        key_value_pairs = [
            ("ADA", [CryptoAcquisitionRecord(datetime.datetime(2021,6,27,12,41,1), 100., 100)]),
            ("CRO", [
                CryptoAcquisitionRecord(datetime.datetime(2021,9,13,13,58,2), 5000., 1000.),
                CryptoAcquisitionRecord(datetime.datetime(2021,9,15,13,33,7), 2000., 800.)
                ]
            )
        ]
        # Create a dictionary using a dictionary comprehension
        expected_remaining_crypto_assets = dict(key_value_pairs)
        return (sale_data, expected_remaining_crypto_assets)

    def test_sell_full_purchase_positions(self):

        # Arrange
        self.crypto_acquisition_data = SimplePurchaseData.as_crypto_acquisition_data()
        crypto_sale_data, expected_remaining_crypto_assets = \
            CryptoAquisitionDataTest.get_testdata_for_sale_of_full_purchase_positions()
        # Act
        for item in crypto_sale_data:
            self.crypto_acquisition_data.remove(item)

        # Assert the expected result
        self.assertEqual(
            len(self.crypto_acquisition_data.data_set['ADA']),
            len(expected_remaining_crypto_assets['ADA'])
        )
        self.assertEqual(
            self.crypto_acquisition_data.data_set['ADA'],
            expected_remaining_crypto_assets['ADA']
        )
        self.assertEqual(
            len(self.crypto_acquisition_data.data_set['CRO']),
            len(expected_remaining_crypto_assets['CRO'])
        )
        self.assertEqual(
            self.crypto_acquisition_data.data_set['CRO'],
            expected_remaining_crypto_assets['CRO']
        )

    @staticmethod
    def get_testdata_for_sale_of_all_assets():
        sale_data = [
            ["2021-05-30 10:24:33", "ADA -> EUR", "ADA", "-99.0", "EUR",
                "180.0", "EUR", "180.0", "198.0", "crypto_viban_exchange",],
            ["2021-07-09 14:01:56", "ADA -> EUR", "ADA", "-44.0", "EUR",
                "100.0", "EUR", "100.0", "110.0", "crypto_viban_exchange",],
            ["2021-09-29 07:00:12", "CRO -> EUR", "CRO", "-3130.0", "EUR",
             "300.0", "EUR", "300.0", "330.0", "crypto_viban_exchange",],
            ["2021-09-30 09:02:00", "ADA -> EUR", "ADA", "-157.0", "EUR",
                "100.0", "EUR", "100.0", "110.0", "crypto_viban_exchange",],
            ["2021-10-10 22:24:43", "CRO -> EUR", "CRO", "-2911.0", "EUR",
             "250.0", "EUR", "250.0", "275.0", "crypto_viban_exchange",],
            ["2021-11-08 18:09:11", "CRO -> EUR", "CRO", "-850.0", "EUR",
             "70.0", "EUR", "70.0", "77.0", "crypto_viban_exchange",],
            ["2022-01-01 01:18:39", "CRO -> EUR", "CRO", "-309.0", "EUR",
             "50.0", "EUR", "50.0", "55.0", "crypto_viban_exchange",]
        ]

        # Define your key-value pairs
        key_value_pairs = [
            ("ADA", []),
            ("CRO", [])
        ]
        # Create a dictionary using a dictionary comprehension
        expected_remaining_crypto_assets = dict(key_value_pairs)
        return (sale_data, expected_remaining_crypto_assets)

    def test_sell_all_crypto_assets(self):
        logger.debug("Entering the test method: ")

        self.crypto_acquisition_data = SimplePurchaseData.as_crypto_acquisition_data()
        crypto_sale_data, expected_remaining_crypto_assets = \
            CryptoAquisitionDataTest.get_testdata_for_sale_of_all_assets()
        for item in crypto_sale_data:
            self.crypto_acquisition_data.remove(item)

        # Assert the expected result
        self.assertEqual(
            len(self.crypto_acquisition_data.data_set['ADA']),
            len(expected_remaining_crypto_assets['ADA'])
        )
        self.assertEqual(
            self.crypto_acquisition_data.data_set['ADA'],
            expected_remaining_crypto_assets['ADA']
        )
        self.assertEqual(
            len(self.crypto_acquisition_data.data_set['CRO']),
            len(expected_remaining_crypto_assets['CRO'])
        )
        self.assertEqual(
            self.crypto_acquisition_data.data_set['CRO'],
            expected_remaining_crypto_assets['CRO']
        )

    @staticmethod
    def get_testdata_for_sale_of_unavailable_ada():
        sale_data = [
            ["2021-05-30 10:24:33", "ADA -> EUR", "ADA", "-99.0", "EUR",
                "180.0", "EUR", "180.0", "198.0", "crypto_viban_exchange",],
            ["2021-07-09 14:01:56", "ADA -> EUR", "ADA", "-44.5", "EUR",
                "100.0", "EUR", "100.0", "110.0", "crypto_viban_exchange",],
            ["2021-09-29 07:00:12", "CRO -> EUR", "CRO", "-3130.0", "EUR",
             "300.0", "EUR", "300.0", "330.0", "crypto_viban_exchange",],
            ["2021-09-30 09:02:00", "ADA -> EUR", "ADA", "-157.0", "EUR",
                "100.0", "EUR", "100.0", "110.0", "crypto_viban_exchange",]
        ]
        return (sale_data, [])

    def test_sale_of_unavailable_crypto_ada(self):
        # Arrange
        self.crypto_acquisition_data = SimplePurchaseData.as_crypto_acquisition_data()
        # Act
        crypto_sale_data, _ = \
            CryptoAquisitionDataTest.get_testdata_for_sale_of_unavailable_ada()
        for item in crypto_sale_data[:-1]:
            self.crypto_acquisition_data.remove(item)
        # Assert
        with self.assertRaises(AssertionError):
            self.crypto_acquisition_data.remove(crypto_sale_data[-1])

    @staticmethod
    def get_testdata_for_sale_of_unavailable_ada_tstamps_considered():
        sale_data = [
            ["2021-05-30 10:24:33", "ADA -> EUR", "ADA", "-99.0", "EUR",
                "180.0", "EUR", "180.0", "198.0", "crypto_viban_exchange",],
            ["2021-06-12 14:01:56", "ADA -> EUR", "ADA", "-101.2", "EUR",
                "160.0", "EUR", "160.0", "176.0", "crypto_viban_exchange",]
        ]
        return (sale_data, [])

    def test_that_assets_added_later_do_not_affect_the_sale_of_assets_added_earlier(self):
        # Arrange
        self.crypto_acquisition_data = SimplePurchaseData.as_crypto_acquisition_data()
        # Act
        crypto_sale_data, _ = \
            CryptoAquisitionDataTest.get_testdata_for_sale_of_unavailable_ada_tstamps_considered()
        for item in crypto_sale_data[:-1]:
            self.crypto_acquisition_data.remove(item)
        # Assert that exception is raised. At the time of removal there are not enough ada assets
        with self.assertRaises(AssertionError):
            self.crypto_acquisition_data.remove(crypto_sale_data[-1])

    @staticmethod
    def get_testdata_for_sale_of_unavailable_cro():
        sale_data = [
            ["2021-05-30 10:24:33", "ADA -> EUR", "ADA", "-99.0", "EUR",
                "180.0", "EUR", "180.0", "198.0", "crypto_viban_exchange",],
            ["2021-07-09 14:01:56", "ADA -> EUR", "ADA", "-44.0", "EUR",
                "100.0", "EUR", "100.0", "110.0", "crypto_viban_exchange",],
            ["2021-09-29 07:00:12", "CRO -> EUR", "CRO", "-3130.0", "EUR",
             "300.0", "EUR", "300.0", "330.0", "crypto_viban_exchange",],
            ["2021-09-30 09:02:00", "ADA -> EUR", "ADA", "-157.0", "EUR",
                "100.0", "EUR", "100.0", "110.0", "crypto_viban_exchange",],
            ["2021-10-10 22:24:43", "CRO -> EUR", "CRO", "-2911.0", "EUR",
             "250.0", "EUR", "250.0", "275.0", "crypto_viban_exchange",],
            ["2021-11-08 18:09:11", "CRO -> EUR", "CRO", "-850.0", "EUR",
             "70.0", "EUR", "70.0", "77.0", "crypto_viban_exchange",],
            ["2022-01-01 01:18:39", "CRO -> EUR", "CRO", "-309.1", "EUR",
             "50.0", "EUR", "50.0", "55.0", "crypto_viban_exchange",]
        ]
        return (sale_data, [])

    def test_sale_of_unavailable_cro(self):
        # Arrange
        self.crypto_acquisition_data = SimplePurchaseData.as_crypto_acquisition_data()
        crypto_sale_data, _ = \
            CryptoAquisitionDataTest.get_testdata_for_sale_of_unavailable_cro()
        # Act
        for item in crypto_sale_data[:-1]:
            self.crypto_acquisition_data.remove(item)
        # Assert
        with self.assertRaises(AssertionError):
            self.crypto_acquisition_data.remove(crypto_sale_data[-1])


class CryptoSwapTest(unittest.TestCase):

    # Set up the test environment
    def setUp(self):
        logger.info("Entering the test case %s.", self._testMethodName)
        # Initialize an instance of the class to be tested
        self.crypto_acquisition_data = crypto_tax_report.CryptoAquisitionData()

    def tearDown(self) -> None:
        logger.info("Leaving the test case %s.", self._testMethodName)

    def test_swap_single_crypto_assets(self):
        """
        ["2021-05-20 12:57:28", "EUR -> ADA", "EUR", "-225.0", "ADA",
            "150.0", "EUR", "225.0", "247.5", "viban_purchase",],
        ["2021-05-29 19:57:07", "EUR -> CRO", "EUR", "-20.0", "CRO",
         "200.0", "EUR", "20.00", "21.2", "viban_purchase",],
        ["2021-06-27 12:41:01", "EUR -> ADA", "EUR", "-100.0", "ADA",
         "100.0", "EUR", "100.0", "110.0", "viban_purchase",],
        ["2021-09-13 13:58:02", "EUR -> CRO", "EUR", "-1000.0", "CRO",
         "5000.0", "EUR", "1000.0", "1100.0", "viban_purchase",],
        ["2021-09-15 13:33:07", "EUR -> CRO", "EUR", "-800.0", "CRO",
             "2000.0", "EUR", "800.0", "880.0", "viban_purchase",]
        """
        # Arrange
        initial_aquistion_data = self.crypto_acquisition_data =  \
            SimplePurchaseData.as_crypto_acquisition_data()
        # Act
        crypto_swap_data = [
            ["2021-12-06 14:01:56", "ADA -> CRO", "ADA", "-50.0", "CRO",
                "200.0", "ADA", "40.0", "40.0", "crypto_viban_exchange",]
        ]
        for item in crypto_swap_data:
            self.crypto_acquisition_data.swap(item)
        # Assert
        self.assertEqual(
            len(self.crypto_acquisition_data.data_set['ADA']),
            2
        )
        self.assertEqual(
            len(self.crypto_acquisition_data.data_set['CRO']),
            4
        )

        # check the three ADA entries
        reduced_ada_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 5, 20, 12, 57, 28),
            amount = 150.0,
            bought_at = 225.0
            )
        self.assertEqual(self.crypto_acquisition_data.data_set['ADA'][0], reduced_ada_record)
        # The other ADA record remains unchanged
        self.assertEqual(self.crypto_acquisition_data.data_set['ADA'][1],
                         initial_aquistion_data.data_set['ADA'][1])


        new_cro_record = crypto_tax_report.CryptoAcquisitionRecord(
            date_time = datetime.datetime(2021, 12, 6, 14, 1, 56),
            amount = 200.0,
            bought_at = 40.0
            )

        # please print the fourth CRO entry
        self.assertEqual(self.crypto_acquisition_data.data_set['CRO'][3], new_cro_record)
        # The other CRO records remain unchanged
        # Breaking down the assertions into multiple lines for better readability
        self.assertEqual(
            self.crypto_acquisition_data.data_set['CRO'][0],
            initial_aquistion_data.data_set['CRO'][0]
        )
        self.assertEqual(
            self.crypto_acquisition_data.data_set['CRO'][1],
            initial_aquistion_data.data_set['CRO'][1]
        )
        self.assertEqual(
            self.crypto_acquisition_data.data_set['CRO'][2],
            initial_aquistion_data.data_set['CRO'][2]
        )


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/python3

"""
The module provides functionality for parsing the transactions of a crypto.com csv file
and calculating the amount of profit for which Germain capital gains taxes have to be paid.
"""

import csv
import datetime
import logging
import re
from enum import Enum
from dataclasses import dataclass

# Define a currency enum class

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Currency(Enum):
    """ Identifiers for all handled crypto currencies."""
    CRO = 1
    SOL = 2
    ADA = 3
    DOT = 4
    USDT = 5
    ETH = 6
    ATOM = 7
    XRP = 8
    LINK = 9
    VVS = 10
    MANA = 11
    ELON = 12
    EUR = 13


class Heading(Enum):
    """ Identifiers for the columns of the read-in crypto.com csv file."""
    TIMESTAMP = 0
    IDENTIFIER = 1
    SOURCE_CURRENCY = 2
    SOURCE_AMOUNT = 3
    TARGET_CURRENCY = 4
    TARGET_AMOUNT = 5
    NATIVE_CURRENCY = 6
    NATIVE_CURRENCY_AMOUNT = 7
    DOLLAR_AMOUNT = 8
    INTERNAL_IDENTIFIER = 9
    HASH_KEY = 10


class TaxPolicy(Enum):
    """ The TaxPolixy states how a profit has to be considered with regards to
    taxation.
    """
    EXEMPT = 0
    CAPITAL_GAINS = 1


# Define the regex pattern with named groups
CURRENCY_EXCHANGE_PATTERN = r'\s*(?P<FromCurrency>[\w]+)\s*->\s*(?P<ToCurrency>[\w]+)\s*'


def get_date_time_object(datetime_as_string):
    """
    Function for converting a string to a datetime.datetime object.
    If the conversion is not possible a ValueError is thrown. Otherwise 
    the datetime.datetime object is returned.
    """
    date_format = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.strptime(datetime_as_string, date_format)


def match_currency_exchange_pattern(string_to_match):
    """
    Check whether the given string matches the pattern
    '<currency1> -> <currency2>', where <currency1> and <currency2>
    are strings, which should represent an arbitrary currency (like
    EUR for Euro) or crypto currency (like ADA). Currently it is not
    checked whether the currency is matches an element of the
    currency enum.
    """
    is_a_match = False
    from_currency = ""
    to_currency = ""
    match_result = re.match(CURRENCY_EXCHANGE_PATTERN, string_to_match)
    if match_result:
        is_a_match = True
        from_currency = match_result.group('FromCurrency')
        to_currency = match_result.group('ToCurrency')
    return (is_a_match, from_currency, to_currency)


def match_buy_crypto_currency_with_euro(string_to_match):
    """
    Check whether the given string matches the pattern 'EUR -> <currency2>',
    where <currency2 is an arbitrary crypto currency. It is not checked
    whether this crypto currency is known in any way.
    """
    is_a_match, from_currency, _ = match_currency_exchange_pattern(
        string_to_match)
    if is_a_match and from_currency == Currency.EUR.name:
        return True
    return False


def match_sell_crypto_currency_get_euro(string_to_match):
    """
    Check whether the given string matches the pattern '<currency1> -> EUR',
    where <currency1> is an arbitrary crypto currency. It is not checked
    whether this crypto currency is known in any way.
    """

    is_a_match, _, to_currency = match_currency_exchange_pattern(
        string_to_match)
    if is_a_match and to_currency == Currency.EUR.name:
        return True
    return False


def match_swap_of_crypto_currency(string_to_match):
    """
    Check whether the given string matches the pattern
    '<currency1> -> <currency2>', where <currency1> and <currency2> are
    arbitrary crypto currencies. It is not checked whether these crypto
    currencies are known in any way, only that they are not equal to 'EUR'.
    """
    is_a_match, from_currency, to_currency = match_currency_exchange_pattern(
        string_to_match)
    if is_a_match and from_currency != Currency.EUR.name and to_currency != Currency.EUR.name:
        return True
    return False


@dataclass
class CryptoAcquisitionRecord:
    """
    Class representing a data entry of a single acquisition transaction of a
    crypto currency. It contains all relevant data in order to compute the capital
    gains tax, if the crypto currency is sold again.
    """
    date_time: datetime
    amount: float
    bought_at: float
    tax_policy: Enum = TaxPolicy.CAPITAL_GAINS

    def __str__(self):
        return (
            f"Date and Time: {self.date_time}, "
            f"Amount: {self.amount}, "
            f"Bought At: {self.bought_at}, "
            f"Tax Policy: {self.tax_policy.name}"
        )


def get_crypto_acquisition_record_from_raw_data_entry(raw_data_entry):
    """
    Functon to convert a list, obtained from reading in a data row in crypto.com's
    csv file, to an object of type CryptoAquisitionRecord.
    """
    date_time = get_date_time_object(raw_data_entry[Heading.TIMESTAMP.value])
    crypto_amount = float(raw_data_entry[Heading.TARGET_AMOUNT.value])
    euro_amount = float(raw_data_entry[Heading.NATIVE_CURRENCY_AMOUNT.value])
    return CryptoAcquisitionRecord(date_time, crypto_amount, euro_amount)


class CryptoAcquisitionRecordRemover: # pylint: disable=too-few-public-methods
    """
    Functor, whose constructor is called with the list of actual aquisition
    records of a certain crypto currency and the amount of how much of it should
    be removed. Upon being called it removes/changes the oldest aquisition
    records accordingly and updates the acquistion record list. It returns the
    Euro amount at which the removed amount of crypto currency has been bought.
    """

    def __init__(self, aquisition_records, amount_to_remove):
        self.amount_to_be_removed = abs(float(amount_to_remove))
        self.removed_crypto_bought_at = 0.0
        self.new_acquisition_records = []
        self.old_acquisition_records = aquisition_records

    def __call__(self):
        logger.debug("Removing the amount of {self.amount_to_be_removed}.")
        for record in self.old_acquisition_records:
            self.__handle_acquisition_record(record)
        self.old_acquisition_records = self.new_acquisition_records
        return self.removed_crypto_bought_at

    def __handle_acquisition_record(self, acquisition_record):
        # do not leave amounts of 1 / 100000 of the original sum
        if self.amount_to_be_removed > (acquisition_record.amount * 0.99999):
            self.amount_to_be_removed -= acquisition_record.amount
            self.removed_crypto_bought_at += acquisition_record.bought_at
        elif self.amount_to_be_removed > 0.0:
            relative_reduction_of_entry = (
                acquisition_record.amount - self.amount_to_be_removed) / acquisition_record.amount
            new_amount = (1.0 - relative_reduction_of_entry) * acquisition_record.bought_at
            self.removed_crypto_bought_at += new_amount
            self.new_acquisition_records.append(CryptoAcquisitionRecord(
                acquisition_record.date_time,
                acquisition_record.amount - self.amount_to_be_removed,
                acquisition_record.bought_at * relative_reduction_of_entry)
                )
            self.amount_to_be_removed = 0.0
        else:
            self.new_acquisition_records.append(acquisition_record)


class CryptoAquisitionData:
    """
    Data class, which holds the aquisitions of each crypto currency. The data
    can be manipulated by the member function add, remove and swap, which
    correspond to buying, selling and exchanging crypto currencies.
    """

    def __init__(self):
        self.data_set = {}

    def add(self, raw_data_entry):
        """Add an one-time aquisition of a crypto currency to the data class.
        The aquistion is given in terms of a crypto.com csv-datafile entry,
        which has been converted from a string to a list."""
        crypto_currency = raw_data_entry[Heading.TARGET_CURRENCY.value]
        try:
            currency_entry = get_crypto_acquisition_record_from_raw_data_entry(raw_data_entry)
        except ValueError as e:
            logger.error("A value error was raised: %s.", e)
            logger.error("""While trying to parse the string: %s.
                         The data entry is ignored.""", raw_data_entry
                         )
            return
        self.__add(crypto_currency, currency_entry)

    def __add(self, crypto_currency, currency_entry):
        if not crypto_currency in self.data_set:
            self.data_set[crypto_currency] = []
        logger.debug("Adding entry for crypto currency %s.", crypto_currency)
        self.data_set[crypto_currency].append(currency_entry)
        self.data_set[crypto_currency].sort(key=lambda x: x.date_time)

    def remove(self, raw_data_entry):
        """Remove an amount of a crypto currency from the data class. This
        corresponds to a one-time sale of the crypto currency. The sale is
        given in terms of a crypto.com csv-datafile entry, which has been
        converted from a string to a list.
        """
        crypto_currency = raw_data_entry[Heading.SOURCE_CURRENCY.value]
        if not crypto_currency in self.data_set:
            logger.error(
                "Logical error: there should be an entry for the "
                "crypto currency {cryptoCurrency}."
            )
            return 0.0
        amount = raw_data_entry[Heading.SOURCE_AMOUNT.value]
        logger.debug(
            "Crypto transaction: removing the amount {amount} "
            "of the crypto curreny {crypto_currency}."
        )
        transaction_remover = CryptoAcquisitionRecordRemover(
            self.data_set[crypto_currency], amount)
        transaction_remover()
        self.data_set[crypto_currency] = transaction_remover.new_acquisition_records
        return float(transaction_remover.removed_crypto_bought_at)

    def swap(self, raw_data_entry):
        """Convert an amount of one crypto currency into another crypto 
        currency within the data class. This corresponds to buying one crypto
        currency with another crypto currency. This crypto exchange is given in 
        terms of a crypto.com csv-datafile entry, which has been converted from
        a string to a list.
        """
        bought_at = self.remove(raw_data_entry)
        crypto_currency = raw_data_entry[Heading.TARGET_CURRENCY.value]
        currency_entry = get_crypto_acquisition_record_from_raw_data_entry(
            raw_data_entry)
        currency_entry.bought_at = bought_at
        self.__add(crypto_currency, currency_entry)


class ProfitCalculator: # pylint: disable=too-few-public-methods

    """
    Class calcuting those profits from crypto transactions, which are tax-relevant.
    """

    def __init__(self, crypto_aquistion_data):
        self.crypto_aquistion_data = crypto_aquistion_data
        self.taxable_profit = 0.0

    def process_data(self, raw_crypto_aquisition_data): # pylint: disable=unused-argument

        """Process the data from a crypto.com csv file."""
        return 0

    def __process_raw_entry(self, raw_data_entry):
        if match_buy_crypto_currency_with_euro(raw_data_entry):
            return
        if match_sell_crypto_currency_get_euro(raw_data_entry):
            return
        if match_swap_of_crypto_currency(raw_data_entry):
            return


def main():
    """ Entry point for calling this file directly as a python script."""
    transaction_list = []
    date_times = []
    with open('crypto_transactions_record_20230619_084542.csv', encoding="utf-8",
              mode='r', newline='') as csvfile:
        tax_report_reader = csv.reader(csvfile, delimiter=',')
        for row in tax_report_reader:
            try:
                date_time = get_date_time_object(
                    row[Heading.TIMESTAMP.value])
            except ValueError as e:
                logger.error("""The time stamp in the data file could not be parsed: %s.
                              Skip this line.""", e)
                continue
            date_times.append(date_time)
            new_transaction = row[Heading.IDENTIFIER.value]
            if new_transaction not in transaction_list:
                transaction_list.append(new_transaction)
    date_times.reverse()
    for item in transaction_list:
        print(item)


if "__main__" == __name__:
    main()

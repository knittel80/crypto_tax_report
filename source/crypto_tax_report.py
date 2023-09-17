#!/usr/bin/python3

import csv
import datetime
import functools
import re
from enum import Enum

# Define a currency enum class


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
currencyExchangePattern = r'\s*(?P<FromCurrency>[\w]+)\s*->\s*(?P<ToCurrency>[\w]+)\s*'


def get_date_time_object(dateTimeAsString):
    """
    Function for converting a string to a datetime.datetime object.
    The return values' first element states whether the conversion has been
    successful. If it has been successful, the datetime.datetime object is 
    returned as the second element.
    """
    try:
        dateAsString, timeAsString = dateTimeAsString.split()
        yearAsString, monthAsString, dayAsString = dateAsString.split('-')
        hoursAsString, minutesAsString, secondsAsString = timeAsString.split(
            ':')
        year, month, day, hours, minutes, seconds = int(yearAsString), int(monthAsString), int(
            dayAsString), int(hoursAsString), int(minutesAsString), int(secondsAsString)
        result = datetime.datetime(year, month, day, hours, minutes, seconds)
    except ValueError as ve:
        if not dateTimeAsString == "Timestamp (UTC)":
            print(f'The string {dateTimeAsString} could not be evaluated.')
        return (False, None)
    return (True, result)


def matchCurrencyExchangePattern(stringToMatch):
    """
    Check whether the given string matches the pattern
    '<currency1> -> <currency2>', where <currency1> and <currency2>
    are strings, which should represent an arbitrary currency (like
    EUR for Euro) or crypto currency (like ADA). Currently it is not
    checked whether the currency is matches an element of the
    currency enum.
    """
    isAMatch = False
    fromCurrency = ""
    toCurrency = ""
    matchResult = re.match(currencyExchangePattern, stringToMatch)
    if matchResult:
        isAMatch = True
        fromCurrency = matchResult.group('FromCurrency')
        toCurrency = matchResult.group('ToCurrency')
    return (isAMatch, fromCurrency, toCurrency)


def match_buy_crypto_currency_with_euro(stringToMatch):
    """
    Check whether the given string matches the pattern 'EUR -> <currency2>',
    where <currency2 is an arbitrary crypto currency. It is not checked
    whether this crypto currency is known in any way.
    """
    isAMatch, fromCurrency, toCurrency = matchCurrencyExchangePattern(
        stringToMatch)
    if isAMatch and fromCurrency == Currency.EUR.name:
        return True
    return False


def match_sell_crypto_currency_get_euro(stringToMatch):
    """
    Check whether the given string matches the pattern '<currency1> -> EUR',
    where <currency1> is an arbitrary crypto currency. It is not checked
    whether this crypto currency is known in any way.
    """

    isAMatch, fromCurrency, toCurrency = matchCurrencyExchangePattern(
        stringToMatch)
    if isAMatch and toCurrency == Currency.EUR.name:
        return True
    return False


def match_swap_of_crypto_currency(stringToMatch):
    """
    Check whether the given string matches the pattern
    '<currency1> -> <currency2>', where <currency1> and <currency2> are
    arbitrary crypto currencies. It is not checked whether these crypto
    currencies are known in any way, only that they are not equal to 'EUR'.
    """
    isAMatch, fromCurrency, toCurrency = matchCurrencyExchangePattern(
        stringToMatch)
    if isAMatch and fromCurrency != Currency.EUR.name and toCurrency != Currency.EUR.name:
        return True
    return False


class CryptoAquisitionRecord:
    """
    Class representing a data entry of a single acquisition transaction of a
    crypto currency. It contains all relevant data in order to compute the capital
    gains tax, if the crypto currency is sold again.
    """

    def __init__(self, dateTime, amount, actualValueEuro):
        self.dateTime = dateTime
        self.amount = amount
        self.boughtAt = actualValueEuro
        self.taxPolicy = TaxPolicy.CAPITAL_GAINS


def get_crypto_aquisition_record_from_raw_data_entry(rawDataEntry):
    """
    Functon to convert a list, obtained from reading in a data row in crypto.com's
    csv file, to an object of type CryptoAquisitionRecord.
    """
    dateTime = get_date_time_object(rawDataEntry[Heading.TIMESTAMP.value])
    cryptoAmount = float(rawDataEntry[Heading.TARGET_AMOUNT.value])
    euroAmount = float(rawDataEntry[Heading.NATIVE_CURRENCY_AMOUNT.value])
    return CryptoAquisitionRecord(dateTime, cryptoAmount, euroAmount)


class CryptoAquisitionRecordRemover:
    """
    Functor, whose constructor is called with the list of actual aquisition
    records of a certain crypto currency and the amount of how much of it should
    be removed. Upon being called it removes/changes the oldest aquisition
    records accordingly and updates the acquistion record list. It returns the
    Euro amount at which the removed amount of crypto currency has been bought.
    """

    def __init__(self, aquisition_records, amount_to_remove):
        self.amount_to_be_removed = float(amount_to_remove)
        self.removed_crypto_bought_at = 0.0
        self.new_aquisition_records = []
        self.old_aquisition_records = aquisition_records

    def __call__(self):
        for record in self.old_aquisition_records:
            self.__handle_aquisition_record(record)
        self.old_aquisition_records = self.new_aquisition_records
        return self.removed_crypto_bought_at

    def __handle_aquisition_record(self, aquisition_record):
        if self.amount_to_be_removed > aquisition_record.amount:
            self.amount_to_be_removed -= aquisition_record.amount
            self.removed_crypto_bought_at += aquisition_record.boughtAt
        elif self.amount_to_be_removed > 0.0:
            relativeReductionOfEntry = (
                aquisition_record.amount - self.amount_to_be_removed) / aquisition_record.amount
            self.removed_crypto_bought_at += (1.0 -
                                              relativeReductionofEntry) * aquisition_record.boughtAt
            self.new_aquisition_records.append(CryptoAquisitionRecord(
                aquisition_record.dateTime, aquisition_record.amount - self.amount_to_be_removed, aquisition_record.boughtAt * relativeReductionOfEntry))
            self.amount_to_be_removed = 0.0
        else:
            self.new_aquisition_records.append(aquisition_record)


class CryptoAquisitionData:
    """
    Data class, which holds the aquisitions of each crypto currency. The data
    can be manipulated by the member function add, remove and swap, which
    correspond to buying, selling and exchanging crypto currencies.
    """

    def __init__(self):
        self.dataSet = {}

    def add(self, rawDataEntry):
        cryptoCurrency = rawDataEntry[Heading.TARGET_CURRENCY.value]
        currencyEntry = get_crypto_aquisition_record_from_raw_data_entry(
            rawDataEntry)
        self.__add(cryptoCurrency, currencyEntry)

    def __add(self, cryptoCurrency, currencyEntry):
        if not cryptoCurrency in self.dataSet:
            self.dataSet[cryptoCurrency] = []
        print(f"Adding entry for crypto currency {cryptoCurrency}")
        self.dataSet[cryptoCurrency].append(currencyEntry)
        self.dataSet[cryptoCurrency].sort(key=lambda x: x.dateTime)

    def remove(self, rawDataEntry):
        cryptoCurrency = rawDataEntry[Heading.SOURCE_CURRENCY.value]
        if not cryptoCurrency in self.dataSet:
            print(
                "Logical error: there should be an entry for the crypto currency {cryptoCurrency}.")
            return 0.0
        amount = rawDataEntry[Heading.SOURCE_AMOUNT.value]
        transaction_remover = CryptoAquisitionRecordRemover(
            self.dataSet[cryptoCurrency], amount)
        transaction_remover()
        return float(transaction_remover.removed_crypto_bought_at)

    def swap(self, rawDataEntry):
        boughtAt = self.remove(rawDataEntry)
        crypoCurrency = rawDataEntry[Heading.TARGET_CURRENCY.value]
        currencyEntry = get_crypto_aquisition_record_from_raw_data_entry(
            rawDataEntry)
        currencyEntry.euroAmount = boughtAt
        self.__add(cryptoCurrency, crypoCurrency)


class ProfitCalculator:
    """
    Class calcuting those profits from crypto transactions, which are tax-relevant.
    """

    def __init__(self, transactionData):
        self.transactionData = transactionData
        self.taxableProfit = 0.0

    def processData(self, raw_crypto_aquisition_data):
        return 0

    def __processRawEntry(self, rawDataEntry):
        if match_buy_crypto_currency_with_euro(rawDataEntry):
            return
        if match_sell_crypto_currency_get_euro(rawDataEntry):
            return
        if match_swap_of_crypto_currency(rawDataEntry):
            return


def main():
    transactionList = []
    dateTimes = []
    with open('crypto_transactions_record_20230619_084542.csv', newline='') as csvfile:
        taxReportReader = csv.reader(csvfile, delimiter=',')
        for row in taxReportReader:
            validDateTime, dateTime = get_date_time_object(
                row[Heading.TIMESTAMP.value])
            if validDateTime:
                dateTimes.append(dateTime)
            newTransaction = row[Heading.IDENTIFIER.value]
            if newTransaction not in transactionList:
                transactionList.append(newTransaction)
    dateTimes.reverse()
    for item in transactionList:
        print(item)


if "__main__" == __name__:
    main()

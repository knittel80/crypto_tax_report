#!/usr/bin/python3

import csv
import datetime
import functools
import re
from enum import Enum

# Define a currency enum class
class Currency(Enum):
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
    EXEMPT = 0
    CAPITAL_GAINS = 1

# Define the regex pattern with named groups
currencyExchangePattern = r'\s*(?P<FromCurrency>[\w]+)\s*->\s*(?P<ToCurrency>[\w]+)\s*'

def get_date_time_object(dateTimeAsString):
    try:
        dateAsString, timeAsString = dateTimeAsString.split()
        yearAsString, monthAsString, dayAsString = dateAsString.split('-')
        hoursAsString, minutesAsString, secondsAsString = timeAsString.split(':')
        year, month, day, hours, minutes, seconds = int(yearAsString), int(monthAsString), int(dayAsString), int(hoursAsString), int(minutesAsString), int(secondsAsString)
        result = datetime.datetime(year, month, day, hours, minutes, seconds)
    except ValueError as ve:
        if not dateTimeAsString=="Timestamp (UTC)":
            print(f'The string {dateTimeAsString} could not be evaluated.')
        return (False, None)
    return (True, result)

def matchCurrencyExchangePattern(stringToMatch):
    isAMatch = False
    fromCurrency = ""
    toCurrency = ""
    matchResult = re.match(currencyExchangePattern,stringToMatch)
    if matchResult:
        isAMatch = True
        fromCurrency = matchResult.group('FromCurrency')
        toCurrency = matchResult.group('ToCurrency')
    return (isAMatch, fromCurrency, toCurrency)

def match_buy_crypto_currency_with_euro(stringToMatch):
    isAMatch, fromCurrency, toCurrency = matchCurrencyExchangePattern(stringToMatch)
    if isAMatch and fromCurrency==Currency.EUR.name:
        return True
    return False

def match_sell_crypto_currency_get_euro(stringToMatch):
    isAMatch, fromCurrency, toCurrency = matchCurrencyExchangePattern(stringToMatch)
    if isAMatch and toCurrency==Currency.EUR.name:
        return True
    return False

def match_swap_of_crypto_currency(stringToMatch):
    isAMatch, fromCurrency, toCurrency = matchCurrencyExchangePattern(stringToMatch)
    if isAMatch and fromCurrency!=Currency.EUR.name and toCurrency!=Currency.EUR.name:
        return True
    return False

class CurrencyEntry:
    def __init__(self, dateTime, amount, actualValueEuro):
        self.dateTime = dateTime
        self.amount = amount
        self.boughtAt = actualValueEuro
        self.taxPolicy = TaxPolicy.CAPITAL_GAINS


def set_currency_entry_from_raw_data_entry(rawDataEntry):
    dateTime = get_date_time_object(rawDataEntry[Heading.TIMESTAMP.value])
    cryptoAmount = float(rawDataEntry[Heading.TARGET_AMOUNT.value])
    euroAmount = float(rawDataEntry[Heading.NATIVE_CURRENCY_AMOUNT.value])
    return CurrencyEntry(dateTime, cryptoAmount, euroAmount)


class TransactionRemover:
    def __init__(self, initialCryptoAmount):
        self.cryptoAmountToBeRemoved = initialCryptoAmount
        self.removedCryptoBoughtAt = 0.0
        self.newCryptoTransactions = []

    def __call__(self, currencyEntry):
        if self.cryptoAmountToBeRemoved > currencyEntry.amount:
            self.cryptoAmountToBeRemoved -= currencyEntry.amount
            self.removedCryptoBoughtAt += currencyEntry.boughtAt
        elif self.cryptoAmountToBeRemoved > 0.0:
            relativeReductionOfEntry = ( currencyEntry.amount - self.cryptoAmountToBeRemoved ) / currencyEntry.amount
            self.removedCryptoBoughtAt += (1.0 - relativeReductionofEntry) * currencyEntry.boughtAt
            self.newCryptoTransactions.append(CurrencyEntry(currencyEntry.dateTime, currencyEntry.amount - self.cryptoAmountToBeRemoved, currencyEntry.boughtAt * relativeReductionOfEntry))
            self.cryptoAmountToBeRemoved = 0.0
        else:
            self.newCryptoTransactions.append(currencyEntry)

class TransactionData:
    def __init__(self):
        self.dataSet = {}

    def add(self, rawDataEntry):
        cryptoCurrency = rawDataEntry[Heading.TARGET_CURRENCY.value]
        currencyEntry = set_currency_entry_from_raw_data_entry(rawDataEntry)
        self.__add(cryptoCurrency, currencyEntry)

    def __add(self, cryptoCurrency, currencyEntry):
        if not cryptoCurrency in self.dataSet:
            self.dataSet[cryptoCurrency] = []
        print(f"Adding entry for crypto currency {cryptoCurrency}")
        self.dataSet[cryptoCurrency].append(currencyEntry)
        
    def remove(self, rawDataEntry):
        crypoCurrency = rawDataEntry[Heading.SOURCE__CURRENCY.value]
        if not cryptoCurrency in self.dataSet:
            print("Logical error: there should be an entry for the crypto currency {cryptoCurrency}.")
            return 0.0
        amount = rawDataEntry[Heading.SOURCE_AMOUNT.value]
        transactionRemover = TransactionRemover(amount)
        for currencyEntry in self.dataSet[cryptoCurrency]:
            transactionRemover(currencyEntry)
        self.dataSet[cryptoCurrency] = transactionRemover.newCryptoTransactions
        return float(transactionRemover.removedCryptoBoughtAt)

    def swap(self, rawDataEntry):
        boughtAt = self.remove(rawDataEntry)
        crypoCurrency = rawDataEntry[Heading.TARGET_CURRENCY.value]
        currencyEntry = set_currency_entry_from_raw_data_entry(rawDataEntry)
        currencyEntry.euroAmount = boughtAt
        self.__add(cryptoCurrency, crypoCurrency)

class ProfitCalculator:
    def __init__(self, transactionData):
        self.transactionData = transactionData
        self.taxableProfit = 0.0

    def processData(self, rawTransactionData):
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
            validDateTime, dateTime = get_date_time_object(row[Heading.TIMESTAMP.value])
            if validDateTime:
                dateTimes.append(dateTime)
            newTransaction = row[Heading.IDENTIFIER.value]
            if newTransaction not in transactionList:
                transactionList.append(newTransaction)
    dateTimes.reverse()
    for item in transactionList:
       print(item) 
        

if "__main__"==__name__:
    main()

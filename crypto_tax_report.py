#!/usr/bin/python3

import csv
import datetime
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

# Define the regex pattern with named groups
currencyExchangePattern = r'\s*(?P<FromCurrency>[\w]+)\s*->\s*(?P<ToCurrency>[\w]+)\s*'

def getDateTimeObject(dateTimeAsString):
    print(dateTimeAsString)
    try:
        dateAsString, timeAsString = dateTimeAsString.split()
        yearAsString, monthAsString, dayAsString = dateAsString.split('-')
        hoursAsString, minutesAsString, secondsAsString = timeAsString.split(':')
        year, month, day, hours, minutes, seconds = int(yearAsString), int(monthAsString), int(dayAsString), int(hoursAsString), int(minutesAsString), int(secondsAsString)
    except ValueError as ve:
        if not dateTimeAsString=="Timestamp (UTC)":
            print("The string {dateTimeAsString} could not be evaluated.")
        return (False, dateTimeAsString)
    return (True, datetime.datetime(year, month, day, hours, minutes, seconds))

def matchCurrencyExchangePattern(stringToMatch):
    isAMatch = False
    fromCurrency = ""
    toCurrency = ""
    matchResult = re.match(currencyExchangePattern,stringToMatch)
    if matchResult:
        isAMatch = True
        fromCurrency = match.group('FromCurrency')
        toCurrency = match.group('ToCurrency')
    return (isAMatch, fromCurrency, toCurrency)

def buyCryptoCurrencyWithEuro(stringToMatch):
    isAMatch, fromCurrency, toCurrency = matchCurrencyExchangePattern(stringToMatch)
    if isAMatch and fromCurrency==Currency.EUR.name:
        return (True, toCurrency)
    return (False, '')

def sellCryptoCurrencyGetEuro(stringToMatch):
    isAMatch, fromCurrency, toCurrency = matchCurrencyExchangePattern(stringToMatch)
    if isAMatch and toCurrency==Currency.EUR.name:
        return (True, fromCurrency)
    return (False, '')


class CurrencyEntry:
    def __init__(self, dateTime, amount, actualValueEuro):
        self.dateTime = dateTime
        self.amount = amount
        self.valueInEuro = actualValueEuro

class CurrencyData:
    def __init__(self):
        self.dataSet = {}

    def add(self, cryptoCurrency, currencyEntry):
        if not cryptoCurrency in dataSet:
            self.dataSet[cryptoCurrency] = []
        self.dataSet[cryptoCurrency].append(currencyEntry)

def main():
    transactionList = []
    dateTimes = []
    with open('crypto_transactions_record_20230619_084542.csv', newline='') as csvfile:
        taxReportReader = csv.reader(csvfile, delimiter=',')
        for row in taxReportReader:
            validDateTime, dateTime = getDateTimeObject(row[0])
            if validDateTime:
                dateTimes.append(dateTime)
            newTransaction = row[1]
            if newTransaction not in transactionList:
                transactionList.append(newTransaction)
    dateTimes.reverse()
    for item in transactionList:
       print(item) 
        

if "__main__"==__name__:
    main()

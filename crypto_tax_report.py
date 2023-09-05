#!/usr/bin/python3


import csv
import datetime

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

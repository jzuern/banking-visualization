#!/usr/bin/env python3
# coding=utf-8

import collections
import sys
import itertools
import matplotlib.pyplot as plt
import matplotlib as mpl
import time
import datetime
import numpy as np
import glob

# example
from matplotlib.dates import DayLocator, MonthLocator, HourLocator, DateFormatter, drange
from numpy import arange

# helper functions------------------

def german_value_string_to_float(value_string):
    print(value_string)
    # replace all , by .
    v = value_string.replace(',','.')

    # remove all but last .
    v = v.replace('.','', v.count('.')-1)

    # remove quotation marks
    v = v.replace('"','')

    return float(v)


def operation_equal(operation1, operation2):
    return operation1 == operation2


def einkaeufe(operations):

    einkaeufe = []
    for operation in operations:
        locations = ["Rewe","Aldi","Lidl"]

        if (operation['Verwendungszweck'] in locations):
           einkaeufe.append(operation)

    return einkaeufe

def german_to_datetime(german_date_string):

    values = german_date_string.replace("\r","")
    values = values.replace("\n","")
    values = values.replace("\"","")

    values = values.split(".")
    day = int(values[0])
    month = int(values[1])
    year = int(values[2])

    dt = datetime.datetime(year=year,month=month,day=day)

    return dt


def create_plotting_data(operations,start_balance):

    start_balance_value = german_value_string_to_float(start_balance[1])
    start_balance_time = german_to_datetime(start_balance[0])

    unsorted_dates = []
    unsorted_values = []

    for operation in operations:

        dt = german_to_datetime(operation['Buchungstag'])
        unsorted_dates.append(dt)

        if operation['Soll/Haben'] == "H":
            unsorted_values.append(operation['Umsatz'])
        else:
            unsorted_values.append(-1.0*operation['Umsatz'])

    #sort them
    dates, value = zip(*sorted(zip(unsorted_dates,unsorted_values)))

    # start accumulation with start balance
    current_assets = [start_balance_value]
    operation_dates = [start_balance_time]

    #accumulate values
    for i in range(len(value)):
        current_assets.append(value[i] + current_assets[-1])
        operation_dates.append(dates[i])

    return operation_dates,current_assets

def find_start_balance(balances):

    # find earliest balance:
    most_recent_time = datetime.datetime.now()
    start_balance = ()

    for balance in balances:

        balance_time = german_to_datetime(balance[0])
        if (balance_time < most_recent_time):
            start_balance = balance
            most_recent_time = balance_time

    return start_balance


def load_csv_folder(directory):

    operations = []
    balances = []

    # delimiter for "Haben" (credit)
    delim_H = '"H"'
    # delimiter for "Soll" (debit)
    delim_S = '"S"'

    for csv_filename in glob.glob(directory + '/*.csv'):

        file = open(csv_filename, 'r', encoding = "ISO-8859-1")
        
        # skip first 13 lines
        for i in range(0,13):
            next(file) 

        content = file.read()
        file.close()

        # split based on delimiter for debit
        for block in content.split(delim_S):
            block = block + '"S"'
            for subblock in block.split(delim_H):

                print("subblock  = " + subblock)

                # initiate empty operation and balance
                operation = {}

                if (not ('"S"' in subblock)):
                    operation['Soll/Haben'] = "H"
                else:
                    operation['Soll/Haben'] = "S"

                values = subblock.split(';')

                # handle Anfangsbalance and Endbalance
                if ("Anfangssaldo" in subblock or "Endsaldo" in subblock):
                    date = values[0].replace('\n', '').replace('\r', '')
                    amount = values[-2]
                    balance = (date, amount)
                    balances.append(balance)
                    continue

                if(len(values) == 13): # only process valid blocks
                    print("found valid block")
                    operation['Buchungstag'] = values[0]
                    operation['Valuta'] = values[1]
                    operation['Zahlungsempfaenger'] = values[2]
                    operation['Zahlungspflichtiger'] = values[3]
                    operation['IBAN'] = values[5]
                    operation['BIC'] = values[7]
                    operation['Verwendungszweck'] = values[8].replace('\n', ' ')
                    operation['Waehrung'] = values[10]
                    operation['Umsatz'] = german_value_string_to_float(values[11])

                    operations.append(operation) 
                    continue

    return operations, balances



if __name__ == "__main__":

    operations, balances = load_csv_folder('data')
    print("balances", balances)


    for v in operations:
        if(v['Soll/Haben'] == "H"):
            print(v['Umsatz'])

    # print expenses
    for v in operations:
        if(v['Soll/Haben'] == "S"):
            print(v['Umsatz'])



    # get plotting data

    start_balance = find_start_balance(balances)
    print("start balance", start_balance)
    dates, assets = create_plotting_data(operations,start_balance)

    fig, ax = plt.subplots()

    ax.plot_date(dates, assets, linestyle='solid', marker='.')
    ax.set_xlim(dates[0], dates[-1])

    ax.xaxis.set_major_locator(MonthLocator())
    ax.xaxis.set_minor_locator(DayLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%m/%d/%Y'))
    ax.xaxis.set_minor_formatter(DateFormatter('%d'))

    ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
    fig.autofmt_xdate()

    plt.show()
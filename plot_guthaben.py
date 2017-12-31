#!/usr/bin/env python3
# coding=utf-8

import collections
import sys
import itertools
import matplotlib.pyplot as plt
import time
import datetime
import numpy as np

# plottling library:
# -- plotly: (not free)



# helper functions------------------

def my_to_float(value_string):
    print(value_string)
    # replace all , by .
    v = value_string.replace(',','.')

    # remove all but last .
    v = v.replace('.','', v.count('.')-1)

    # remove quotation marks
    v = v.replace('"','')

    return float(v)


def vorgang_equal(vorgang1, vorgang2):
    return vorgang1 == vorgang2


def einkaeufe(vorgaenge):

    einkaeufe = []
    for vorgang in vorgaenge:
        locations = ["Rewe","Aldi","Lidl"]

        if (vorgang['Verwendungszweck'] in locations):
           einkaeufe.append(vorgang)

    return einkaeufe

def german_to_unix(german_date_string):
    values = german_date_string.replace("\r","")
    values = values.replace("\n","")
    values = values.replace("\"","")

    values = values.split(".")
    day = int(values[0])
    month = int(values[1])
    year = int(values[2])

    dt = datetime.datetime(year=year,month=month,day=day)
    unix_time = time.mktime(dt.timetuple())

    return unix_time


def create_plotting_data(vorgaenge):

    x = []
    y = []


    for vorgang in vorgaenge:

        unix_time = german_to_unix(vorgang['Buchungstag'])
        x.append(unix_time)
        if vorgang['Soll/Haben'] == "H":
            y.append(vorgang['Umsatz'])
        else:
            y.append(-1.0*vorgang['Umsatz'])

    #sort them
    date, value = zip(*sorted(zip(x,y)))

    start_value = 0.0
    accumulated = [start_value]

    #accumulate values
    for i in range(len(value)):
        accumulated.append(value[i] + accumulated[-1])

    return date,accumulated[1:]

# Get started

def load_csv(csv_filename):
    
    file = open(csv_filename, 'r')
    content = file.read()
    file.close()

    vorgaenge = []
    saldos = []

    delim_H = '"H"'
    delim_S = '"S"'


    for block in content.split(delim_S):
        block = block + '"S"'
        for subblock in block.split(delim_H):

            # initiate empty vorgang and saldo
            vorgang = {}
            saldo = {}

            if (not ('"S"' in subblock)):
                vorgang['Soll/Haben'] = "H"
            else:
                vorgang['Soll/Haben'] = "S"

            values = subblock.split(';')

            # handle Anfangssaldo and Endsaldo
            if ("Anfangssaldo" in subblock or "Endsaldo" in subblock):
                date = values[0].replace('\n', '').replace('\r', '')
                amount = values[-2]
                saldo[date] = amount
                print("amount",amount)
                print("date",date)
                continue

            if(len(values) == 13): # only process valid blocks
                vorgang['Buchungstag'] = values[0]
                vorgang['Valuta'] = values[1]
                vorgang['Zahlungsempfaenger'] = values[2]
                vorgang['Zahlungspflichtiger'] = values[3]
                vorgang['IBAN'] = values[5]
                vorgang['BIC'] = values[7]
                vorgang['Verwendungszweck'] = values[8].replace('\n', ' ')
                vorgang['Waehrung'] = values[10]
                vorgang['Umsatz'] = my_to_float(values[11])

                vorgaenge.append(vorgang) 

    return vorgaenge, saldos


vorgaenge, saldos = load_csv('test.csv')


# Drucke Einnahmen:
for v in vorgaenge:
    if(v['Soll/Haben'] == "H"):
        print(v['Umsatz'])

# Drucke Ausgaben
for v in vorgaenge:
    if(v['Soll/Haben'] == "S"):
        print(v['Umsatz'])



# Plotte Verlauf des Guthabens
x,y = create_plotting_data(vorgaenge)

fig = plt.figure()
ax = fig.gca()
plt.grid()
plt.plot(x,y)
plt.show()

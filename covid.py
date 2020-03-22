#!/usr/bin/python3

import csv
import datetime
import requests


class State:
    def __init__(self, population):
        self.Population = population
        self.Snapshots = {}

    def AddSnapshot(self, ts, positive, negative, pending, hospitalized, dead):
        self.Snapshots[ts] = Snapshot(positive, negative, pending, hospitalized, dead)

    def __str__(self):
        return f'{self.Population:>10}=pop  {len(self.Snapshots):>4}=snaps'


class Snapshot:
    def __init__(self, positive, negative, pending, hospitalized, dead):
        self.Positive = positive
        self.Negative = negative
        self.Pending = pending
        self.Hospitalized = hospitalized
        self.Dead = dead


states = {}


def LoadPopulations():
    with open('populations.csv', 'r') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            states[row['State']] = State(int(row['Population']))

def LoadCovidTracking():
    resp = requests.get('https://covidtracking.com/api/states/daily')
    for row in resp.json():
        ts = datetime.datetime.fromisoformat(row['dateChecked'][:-1])
        states[row['state']].AddSnapshot(
                ts,
                row['positive'],
                row['negative'],
                row['pending'],
                row['hospitalized'],
                row['death'],
        )

LoadPopulations()
LoadCovidTracking()

for code, state in sorted(states.items(), key=lambda x: x[1].Population):
    print(f'{code}  {state}')

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

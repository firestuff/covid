#!/usr/bin/python3

import csv
import datetime
import requests


def with_snapshot(func):
    def wrapper(self, ts=None):
        if not ts:
            ts = self.Latest()
        return func(self, self.Snapshots[ts])
    return wrapper


def per_million(func):
    def wrapper(self, *args, **kwargs):
        count = func(self, *args, **kwargs)
        return round(count * 1000000 / self.Population)
    return wrapper


class State:
    def __init__(self, population):
        self.Population = population
        self.Snapshots = {}

    def AddSnapshot(self, ts, positive, negative, pending, hospitalized, dead):
        self.Snapshots[ts] = Snapshot(positive, negative, pending, hospitalized, dead)

    def Latest(self):
        return max(self.Snapshots)

    @with_snapshot
    @per_million
    def TestsPerMillion(self, snap):
        return snap.Tests()

    @with_snapshot
    @per_million
    def PositivePerMillion(self, snap):
        return snap.Positive

    @with_snapshot
    @per_million
    def HospitalizedPerMillion(self, snap):
        return snap.Hospitalized

    @with_snapshot
    @per_million
    def DeadPerMillion(self, snap):
        return snap.Dead

    @with_snapshot
    def PositivePerTestBP(self, snap):
        return round(snap.Positive * 10000 / snap.Tests()) if snap.Tests() else 0

    def __str__(self):
        return f'{self.Population:>10}=pop  {len(self.Snapshots):>4}=snaps  {self.TestsPerMillion():>6}=tpm  {self.PositivePerMillion():>6}=ppm  {self.HospitalizedPerMillion():>6}=hpm  {self.DeadPerMillion():>6}=dpm  {self.PositivePerTestBP():>4}=p‱'


class Snapshot:
    def __init__(self, positive, negative, pending, hospitalized, dead):
        self.Positive = positive or 0
        self.Negative = negative or 0
        self.Pending = pending or 0
        self.Hospitalized = hospitalized or 0
        self.Dead = dead or 0

    def Tests(self):
        return self.Positive + self.Negative


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

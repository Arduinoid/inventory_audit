#!/usr/bin/env python3

import xmltodict as x

system = dict()

specs =['PhysicalLocation','DriveModel','SerialNumber','Size']

with open('/discovery-report.xml') as f:
    doc = x.parse(f.read())


def get_drives(doc):
    return doc['Discovery']['ServerInformation']['StorageControllers']['StorageController']['PhysicalDrives']['PhysicalDisk']


def list_drives(drives):
    for drive in drives:
        drive_specs(drive)
        print('------')


def drive_specs(drive, attribute):
    for a in attribute:
        print(drive[a])


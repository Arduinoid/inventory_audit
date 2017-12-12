import xml.etree.ElementTree as ET
import json
from subprocess import Popen, PIPE

HPDISCOVERY = 'hpdiscovery'
HP_DRIVE_COMMAND = ['hpssacli', 'ctrl', 'slot=0', 'pd', 'all', 'show']
DELL_DRIVE_COMMAND = ['MegaCli64','-PDList','-aALL']

proc = Popen(HP_DRIVE_COMMAND, stdout=PIPE)
output = proc.stdout.read()
hp_report = ET.fromstring(output)
make = [r.text for r in report.iter('SystemName')][0]
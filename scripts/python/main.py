import csv, os
from datetime import datetime
from zebra import zebra

from parser_utils import ChassisParser, CPUParser, DriveParser, MacAddressParse, MemoryParser, NetworkParser, ServerParse
from utils import CSVReport, FileWatcher, PrinterTemplate, ThermalPrinter,TEMPLATE
from config import FILE_PATH, LABEL_DIMENSIONS, PRINTER_NAME, REPORT_NAME

specs = ServerParse(FILE_PATH)
mac = MacAddressParse(FILE_PATH, 'SFP')
net = NetworkParser(FILE_PATH)
drive = DriveParser(FILE_PATH)
cpu = CPUParser(FILE_PATH)
mem = MemoryParser(FILE_PATH)
watcher = FileWatcher(FILE_PATH)
report = CSVReport(FILE_PATH, REPORT_NAME, specs)
chassis = ChassisParser(FILE_PATH)
servers = os.listdir(chassis.path)

z = zebra(queue=PRINTER_NAME)
zeb = ThermalPrinter(mac, z)

if __name__ == "__main__":
    print("   ________________________")
    print(r"//                        \\")
    print(r"||    Script running...   ||")
    print(r"\\________________________//",'\n')
    print('Press: ctrl+c to exit program','\n')

    report.get_po_input()
    report.open_report()
    watcher.watch(report, zeb)

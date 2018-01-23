import csv, os
from datetime import datetime

from parser_utils import CPUParser, DriveParser, MacAddressParse, MemoryParser, NetworkParser, ServerParse
from utils import CSVReport, FileWatcher, PrinterTemplate, ThermalPrinter,TEMPLATE,z

FILE_PATH = "//10.11.203.100/nfs/server-specs"
specs = ServerParse(FILE_PATH)
mac = MacAddressParse(FILE_PATH, 'SFP')
net = NetworkParser(FILE_PATH)
drive = DriveParser(FILE_PATH)
cpu = CPUParser(FILE_PATH)
zeb = ThermalPrinter(cpu)
watcher = FileWatcher(FILE_PATH)
# report = CSVReport(FILE_PATH, 'test_report', mac)
# header_written = False

if __name__ == "__main__":
    print("   ________________________")
    print(r"//                        \\")
    print(r"||    Script running...   ||")
    print(r"\\________________________//",'\n')
    print('Press: ctrl+c to exit program','\n')

    # report.get_po_input()
    # report.open_report()
    watcher.watch(report,zeb)

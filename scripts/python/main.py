import csv
from datetime import datetime

from parser_utils import MacAddressParse, MemoryParser, ServerParse
from utils import CSVReport, FileWatcher, ThermalPrinter,TEMPLATE,z

FILE_PATH = "//10.11.203.100/nfs/server-specs"
specs = ServerParse(FILE_PATH)
mac = MacAddressParse(FILE_PATH, 'SFP')
zeb = ThermalPrinter(TEMPLATE, [mac])
watcher = FileWatcher(FILE_PATH, '-spec')
report = CSVReport(FILE_PATH, 'test_report', mac)
header_written = False

if __name__ == "__main__":
    print("   ________________________")
    print(r"//                        \\")
    print(r"||    Script running...   ||")
    print(r"\\________________________//",'\n')
    print('Press: ctrl+c to exit program','\n')

    report.get_po_input()
    report.open_report()
    watcher.watch(report,zeb)

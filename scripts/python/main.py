import csv, os
from datetime import datetime

from parser_utils import CPUParser, MacAddressParse, MemoryParser, NetworkParser, ServerParse
from utils import CSVReport, FileWatcher, ThermalPrinter,TEMPLATE,z

FILE_PATH = "//10.11.203.100/nfs/server-specs"
specs = ServerParse(FILE_PATH)
mac = MacAddressParse(FILE_PATH, 'SFP')
zeb = ThermalPrinter(TEMPLATE, [mac])
watcher = FileWatcher(FILE_PATH)
report = CSVReport(FILE_PATH, 'test_report', mac)
header_written = False

net = NetworkParser(FILE_PATH)
net_data = net(os.listdir(net.path)[1])

if __name__ == "__main__":
    print("   ________________________")
    print(r"//                        \\")
    print(r"||    Script running...   ||")
    print(r"\\________________________//",'\n')
    print('Press: ctrl+c to exit program','\n')

    report.get_po_input()
    report.open_report()
    watcher.watch(report,zeb)

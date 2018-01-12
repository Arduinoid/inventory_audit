import csv
from datetime import datetime

from parser_utils import BaseProcess, MacAddressParse, ServerParse
from utils import FileWatcher, ThermalPrinter,TEMPLATE,z

FILE_PATH = "//10.11.203.100/nfs/server-specs"
mac = MacAddressParse(FILE_PATH, 'SFP')
zeb = ThermalPrinter(TEMPLATE, mac)
watcher = FileWatcher(FILE_PATH, mac.extract_mac)
specs = ServerParse(FILE_PATH)
header_written = False

if __name__ == "__main__":
    print("   ________________________")
    print(r"//                        \\")
    print(r"||    Script running...   ||")
    print(r"\\________________________//",'\n')

    report_name = 'server-report_{}.csv'.format(datetime.now())
    report_name = report_name.replace(' ','_').replace(':','-')
    
    watcher.watch(zeb)

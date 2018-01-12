import csv, time
from datetime import datetime

from parser_utils import BaseProcess, MacAddressParse, ServerParse
from print_mac import ThermalPrinter,TEMPLATE,z
from utils import FileWatcher, TestObj

FILE_PATH = "//10.11.203.100/nfs/server-specs"
mac = MacAddressParse(FILE_PATH, 'SFP')
zeb = ThermalPrinter(TEMPLATE)
watcher = FileWatcher(FILE_PATH, mac.extract_mac)
specs = ServerParse(FILE_PATH)
test = TestObj('in', 'out')
header_written = False

if __name__ == "__main__":
    print("   ________________________")
    print(r"//                        \\")
    print(r"||    Script running...   ||")
    print(r"\\________________________//",'\n')

    report_name = 'server-report_{}.csv'.format(datetime.now())
    report_name = report_name.replace(' ','_').replace(':','-')
    
    while True:
        result = watcher.check()
        if result != None:
            # print out mac address labels
            [zeb.print_out(mac.extract_mac(int(r))) for r in result]
            # Write scanned in servers to a csv file

            # print(specs.attributes)
            # writer = csv.DictWriter(csvfile, fieldnames=specs.attributes)
            # if not header_written:
            #     writer.writeheader()
            #     header_written = True
            # for r in result:
            #     print(r)
            #     if '-spec' in r:
            #         print(specs.process(r))
            #         writer.writerow(specs.process(r))
            #         print("captured {serial} server to report".format(**specs.process(r)))

        time.sleep(1)

import time

from parser_utils import BaseProcess, MacAddressParse
from print_mac import ThermalPrinter,TEMPLATE,z
from utils import FileWatcher

FILE_PATH = "//10.11.203.100/nfs/server-specs"
mac = MacAddressParse(FILE_PATH, 'SFP')
zeb = ThermalPrinter(TEMPLATE)
watcher = FileWatcher(FILE_PATH, mac.extract_mac)

if __name__ == "__main__":
    print("   ________________________")
    print(r"//                        \\")
    print(r"||    Script running...   ||")
    print(r"\\________________________//",'\n')

    while True:
        result = watcher.check()
        if result != None:
            [zeb.print_out(mac.extract_mac(r)) for r in result]

        time.sleep(1)

from parser_utils import BaseProcess, MacAddressParse
from utils import *

FILE_PATH = "//10.11.203.100/nfs/server-specs"
p = MacAddressParse(FILE_PATH, 'SFP')
w = FileWatcher(FILE_PATH, p.extract_mac)

if __name__ == "__main__":
    print("   ________________________")
    print(r"//                        \\")
    print(r"||    Script running...   ||")
    print(r"\\________________________//",'\n')

    w.watch()
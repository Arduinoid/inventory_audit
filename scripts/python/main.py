from parser_utils import BaseProcess
from utils import *

FILE_PATH = "//10.11.203.100/nfs/server-specs"
p = BaseProcess(FILE_PATH)
w = FileWatcher(FILE_PATH, print)

if __name__ == "__main__":
    print("   ________________________")
    print(r"//                        \\")
    print(r"||    Script running...   ||")
    print(r"\\________________________//",'\n')

    w.watch()
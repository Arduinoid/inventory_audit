import os
import unittest
from parser_utils import ChassisParser, CPUParser, DriveParser, MemoryParser, MacAddressParse, NetworkParser, ServerParse

FILE_PATH = os.path.realpath(r'../../sample_info/server-specs')
FILES = os.listdir(FILE_PATH)

class ParserTests(unittest.TestCase):
    def test_chassis_parser_returns_dict(self):
        obj = ChassisParser(FILE_PATH)
        self.assertIsInstance(obj(FILES[0]),dict)
    
    def test_cpu_parser_returns_list(self):
        obj = CPUParser(FILE_PATH)
        self.assertIsInstance(obj(FILES[0]),list)
    
    def test_drive_parser_returns_list(self):
        obj = DriveParser(FILE_PATH)
        self.assertIsInstance(obj(FILES[0]),list)
    
    def test_memory_parser_returns_list(self):
        obj = MemoryParser(FILE_PATH)
        self.assertIsInstance(obj(FILES[0]),list)
    
    def test_mac_parser_returns_dict(self):
        obj = MacAddressParse(FILE_PATH, 'SFP')
        self.assertIsInstance(obj('HPCardFiberCardTest-spec'),dict)
    
    def test_network_parser_returns_list(self):
        obj = NetworkParser(FILE_PATH)
        self.assertIsInstance(obj(FILES[0]),list)
    
    
if __name__ == '__main__':
    unittest.main()
import os
import unittest
from parser_utils import ChassisParser, CPUParser, DriveParser, MemoryParser, MacAddressParse, NetworkParser, ServerParse

FILE_PATH = os.path.realpath(r'../../sample_info/server-specs')
FILES = os.listdir(FILE_PATH)

class ParserTests(unittest.TestCase):
    def test_chassis_parser_returns_dict_when_called(self):
        obj = ChassisParser(FILE_PATH, FILES[0])
        self.assertIsInstance(obj(),dict)
    
    def test_cpu_parser_returns_list_when_called(self):
        obj = CPUParser(FILE_PATH, FILES[0])
        self.assertIsInstance(obj(),list)
    
    def test_drive_parser_returns_list_when_called(self):
        obj = DriveParser(FILE_PATH, FILES[0])
        self.assertIsInstance(obj(),list)
    
    def test_memory_parser_returns_list_when_called(self):
        obj = MemoryParser(FILE_PATH, FILES[0])
        self.assertIsInstance(obj(),list)
    
    def test_mac_parser_returns_dict_when_called(self):
        obj = MacAddressParse(FILE_PATH, 'HPCardFiberCardTest-spec', 'SFP')
        self.assertIsInstance(obj(),dict)
    
    def test_network_parser_returns_list_when_called(self):
        obj = NetworkParser(FILE_PATH, FILES[0])
        self.assertIsInstance(obj(),list)
    
    def test_server_parser_returns_dict_when_called(self):
        obj = ServerParse(FILE_PATH, FILES[0])
        self.assertIsInstance(obj(),dict)
    
    
if __name__ == '__main__':
    unittest.main()
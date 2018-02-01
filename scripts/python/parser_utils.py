#!/bin/usr python3

from json import JSONDecodeError, loads
import os
import re

from utils import PrinterTemplate


class BaseProcess(object):
    '''
    This is the base class that other parser classes will inherit from.
    It contains the common properties and methods used by other parsers 
    '''

    def __init__(self, file_path, file_name=None):
        assert os.path.exists(file_path), "File path is not valid or does not exist"
        self.path = os.path.abspath(file_path)
        self.file_name = file_name
        self.content = None
        self.delimiter = ':'
        self.empty_terms = None
        self.data = None
        self.tag = None

    def extract_file_content(self, directory):
        """Opens and extracts contents of a file"""
        self.get_service_tag(directory)
        with open(self.path + '\\' + directory + '\\' + self.file_name, 'r') as f:
            if '.txt' in self.file_name:
                self.content = [ i.strip() for i in f.read().split('\n') if i != '' ]
            else:
                self.content = f.read()

    def get_context(self, lines, term):
        '''
        Get the end index for each start index in a list

        example:
        get_context(lines, term=TERM)
        > [3,8]
        '''
        start_index = self.term_index(term,lines)
        end_index = list()

        for index, value in enumerate(lines):
            if start_index[index+1:] == []:
                end_index.append(len(lines))
                context = list(zip(start_index, end_index))
                break
            end_index.append(start_index[index+1] -1 )

        return sublist(context,lines)

    def term_index(self, term, lines):
        '''
        Small function that takes a list and a string and returns a list of line
        indexes where that term shows up
        '''
        result = list()
        for index, line in enumerate(lines):
            if term in line:
                result.append(index)
        return result

    def _fix_json(self, data):
        '''
        Input a string containing json and return a corrected
        json string.

        This function assumes that the invalid json needs to be wrapped in 
        a list and proper comma delimiters be inserted between objects
        '''
        data = data.strip()
        data = self.insert_commas(self.wrap_in_list(self.remove_trailing_comma(data)))
        return data

    def remove_trailing_comma(self, data):
        if ',' in data[-1]:
            data = data[:-1]
        return data

    def wrap_in_list(self, data):
        if data.find('[') != 0:
            data = '[' + data + ']'
        return data

    def insert_commas(self, data):
        data = re.sub("}\s*{", "},{", data)
        return data

    def get_json_data(self):
        self.data = loads(self._fix_json(self.content))

    def get_service_tag(self, directory):
        self.tag = directory.split('-')[0]

    def split_by_term(self, data):
        last_index = 0
        first_index = 0
        result = list()
        for d in self.term_index(data):
            if d == first_index:
                continue
            first_index = d
            result.append(self.list_to_dict(data[last_index:first_index]))
            last_index = first_index
        self.data = result

    def term_index(self, data):
        for index, value in enumerate(data):
            if self.descriptor in value:
                yield index
        else:
            yield len(data)

    def list_to_dict(self, list_):
        '''
        Takes a string and a delimiter then splits into key values.
        returns a dict
        '''
        result = dict()
        key, value = (0, -1)
        for string in list_:
            spec = string.split(self.delimiter)
            result.update({ spec[key].replace(' ','') : spec[value].strip() })
        return result

    def filter_empty_terms(self, dict_):
        '''
        Takes a dict of parts info and returns any that don't
        match empty terms
        '''
        key = list(self.empty_terms)[0]
        terms = self.empty_terms[key]
        return not any(term for term in terms if term in dict_[key])

    def extract_attributes(self):
        result = list()
        for data in self.data:
            result.append({ k: data[v] if isinstance(v,str) else data[v[0]][v[1]] for k,v in self.attributes.items()})
        return result


class MacAddressParse(BaseProcess):
    '''
    This class will extract mac address information
    based on a descriptor in a cards product name
    '''
    def __init__(self,file_path, descriptor, file_name='lshw-network.json'):
        super().__init__(file_path, file_name)
        self.descriptor = descriptor
        self.attributes = ['mac','tag']
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.extract_file_content(directory)
        self.get_json_data()
        print('Printing mac address for server: {}'.format(self.tag))
        return self.get_each_card()

    def get_each_card(self):
            if isinstance(self.data,list):
                for i in self.data:
                    if self._get_mac_address(self._is_product(i)):
                        return self._get_mac_address(self._is_product(i))
            elif isinstance(self.data,dict):
                return self._get_mac_address(self._is_product(self.data))

    def _get_mac_address(self, card):
        if card:
            return {'tag': self.tag, 'mac': card['serial']}

    def _is_product(self, card):
        if self.descriptor in card['product']:
            return card


class ServerParse(BaseProcess):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.file_path = file_path
        self.content = None
        self.data = dict()
        self.components = {
            'chassis' : ChassisParser(file_path),
            'cpu': CPUParser(file_path),
            'memory': MemoryParser(file_path),
            'drives': DriveParser(file_path),
            'network': NetworkParser(file_path),
        }
        self.attributes = {
            'make': 'Manufacturer',
            'model': 'ProductName',
            'tag': 'SerialNumber',
            'cpu': 'cpu',
            'memory': 'memory',
            'storage': 'drives',
            'controller': 'controller',
            'network': 'network',
        }
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.compose_specs(directory)
        return self.data

    def compose_specs(self, directory):
        for key, part in self.components.items():
            part(directory)
            self.data.update(part.sum_())


class MemoryParser(BaseProcess):
    def __init__(self, file_path, term='Size', file_name='dmi-memory.txt'):
        super().__init__(file_path, file_name)
        self.content = None
        self.descriptor = term
        self.attributes = [
            'Size',
            'Type',
            'TypeDetail',
            'Manufacturer',
            'SerialNumber',
            'PartNumber',
            'Rank',
            'Speed',
        ]
        self.empty_terms = {
            'Size': [
                'NoModuleInstalled'
            ]
        }
        self.sum_template = "{total}GB Total {count} pcs x {size}GB"
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.extract_file_content(directory)
        self.split_by_term(self.content)
        self.data = list(filter(self.filter_empty_terms, self.data))
        return self.data

    def sum_(self):
        result = dict()
        mem = self.data[0]
        count = len(self.data)
        total = self.total_installed(self.data)
        size = self.extract_number(mem['Size'])
        result['memory'] = self.sum_template.format(
            total=total,
            count=count,
            size=size
        )
        return result

    def total_installed(self, data):
        total = 0
        for i in data:
            total += self.extract_number(i['Size'])
        return total

    def extract_number(self, data):
        return self.size_convert(int(data.replace('MB','')))

    def size_convert(self, data):
        return data // 1024


class CPUParser(BaseProcess):
    def __init__(self, file_path, file_name='lshw-processor.json'):
        super().__init__(file_path, file_name)
        self.attributes = {
            'make':'vendor',
            'model':'version',
            'speed':'size',
            'cores': ['configuration', 'cores'],
            'width': 'width',
            'threads': ['configuration', 'threads'],
        }
        self.cores = {
            'Dual': '2',
            'Quad': '4',
            'Hex': '6',
            'Oct': '8',
            'Deca': '10',
            'DDec': '12',
            'HDec': '16',
        }
        self.sum_template = "{count}x {cores} {model}"
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.extract_file_content(directory)
        self.get_json_data()
        self.convert_speed()
        return self.extract_attributes()

    def convert_speed(self):
        for d in self.data:
            d['size'] = d['size'] / 1000**3

    def sum_(self):
        result = dict()
        cpu = self.data[0]
        count = len(self.data)
        model = self.cleanup_product_name(cpu['product'])
        result['cpu'] = self.sum_template.format(count=count,cores=self.convert_cores(cpu), model=model)
        return result

    def convert_cores(self, data):
        for name, core in self.cores.items():
            if core == data['configuration']['cores']:
                return name

    def cleanup_product_name(self, data):
        result = data.replace('(R)', '').replace('CPU', '').split()
        return ' '.join(result)


class DriveParser(BaseProcess):
    def __init__(self, file_path, term='physicaldrive', file_suffix='-drives.txt'):
        super().__init__(file_path)
        self.file_suffix = file_suffix
        self.descriptor = term
        self.make = None
        self.hp_attributes = {
            'make': 'Make',
            'model': 'Model',
            'size': 'Size',
            'serial': 'SerialNumber',
            'type': 'DriveType',
            'interface': 'InterfaceType',
            'firmware': 'FirmwareRevision',
        }
        self.dell_attributes = {
            'make': 'Make',
            'model': 'Model',
            'size': 'RawSize',
            'serial': 'Serial',
            'type': 'MediaType',
            'interface': 'PDType',
            'firmware': 'DeviceFirmwareLevel',
        }
        self.attributes = self.dell_attributes
        self.terms = {
            'hp': 'physicaldrive',
            'dell': 'Enclosure Device ID'
        }
        self.procedures = {
            'hp': self.hp_process,
            'dell': self.dell_process,
            'server': self.server_process,
        }
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.set_server_make(directory)
        self.extract_file_content(directory)
        self.split_by_term(self.content)
        self.process_by_make()
        return self.extract_attributes()

    def hp_process(self):
        self.attributes = self.hp_attributes
        self.data = list(map(self.split_hp_model_field, self.data[1:]))

    def dell_process(self):
        self.attributes = self.dell_attributes
        self.data = list(map(self.split_dell_inquiry_field, self.data))

    def server_process(self):
        pass

    def process_by_make(self):
        processor = self.procedures[self.make]
        processor()

    def split_hp_model_field(self, dict_):
        '''
        Takes a dict of HP drive attributes and will parse the 'Model'
        field into 'Make' and 'Model' values. This is because the hp utility 
        that produces this data puts this info together in the 'Model' attribute. 
        There will then be a new dict returned containing a new 'Make' field and the 
        existing 'Model' field will only contain the model info
        '''
        data = dict_['Model'].strip().split()
        dict_['Make'], dict_['Model'] = data
        return dict_

    def split_dell_inquiry_field(self, dict_):
        '''
        split the inquiry field into make, model, and serial.
        The MegaCli utility puts all of the information into on field
        '''
        data = dict_['InquiryData'].strip().split()
        dict_['Make'], dict_['Model'], dict_['Serial'] = data
        dict_['RawSize'] = dict_['RawSize'].split('[')[0].strip()
        return dict_

    def set_server_make(self, directory):
        files = os.listdir(self.path + '\\' + directory)
        for file in files:
            if file.find(self.file_suffix) > -1:
                self.make = file.split('-')[0]
                break
        self.file_name = self.make + self.file_suffix

    def sum_(self):
        return dict()


class NetworkParser(BaseProcess):
    def __init__(self, file_path, file_name='lshw-network.json'):
        super().__init__(file_path, file_name)
        self.attributes = {
            'make': 'vendor',
            'model': 'product',
            'mac': 'serial',
        }
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.extract_file_content(directory)
        self.get_json_data()
        return self.extract_attributes()

    def sum_(self):
        return dict()


class ChassisParser(BaseProcess):
    def __init__(self, file_path, file_name='dmi-system.txt'):
        super().__init__(file_path, file_name)
        
        self.attributes = [
            'Manufacturer',
            'ProductName',
            'SerialNumber',
        ]
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.extract_file_content(directory)
        self.data = self.list_to_dict(self.content)
        self.cleanup_model()
        return self.data

    def sum_(self):
        result = dict()
        result['make'] = self.data['Manufacturer']
        result['model'] = self.data['ProductName']
        result['tag'] = self.data['SerialNumber']
        return result

    def cleanup_model(self):
        self.data['Manufacturer'] = self.data['Manufacturer'].replace('Inc.', '')

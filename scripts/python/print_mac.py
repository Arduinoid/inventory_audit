from zebra import zebra
from drive_parser import DriveProcess, get_context, FILE_PATH

content = '''
^XA
^FO100,100
^A0,60,60
^FD
MAC:{}
^FS
^FO100,200
^A0,60,60
^FD
TAG:{}
^FS
^XZ
'''

z = zebra(queue='ZDesigner GK420d')
lshw = DriveProcess(FILE_PATH)


def print_mac_address(process_obj, printer, content, product):
    for server, files in process_obj.content.items():
        tag = server.split('-')[0]
        for net in get_context(files['lshw-report.txt'],term='*-network'):
            for line in net:
                if 'product' in line.lower():
                    if product not in line.lower():
                        break
                if 'serial' in line.lower():
                    mac = line[line.find(':')+1:].strip()
                    printer.output(content.format(mac,tag))
                    # print(content.format(mac,tag))

print_mac_address(lshw,z,content,'netxtreme')
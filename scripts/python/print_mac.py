from zebra import zebra

TEMPLATE = '''
^XA
^FO100,100
^A0,60,60
^FD
MAC:{mac}
^FS
^FO100,200
^A0,60,60
^FD
TAG:{tag}
^FS
^XZ
'''

z = zebra(queue='ZDesigner GK420d')


class ThermalPrinter(object):
    '''
    p = ThermalPrinter(mac.extract,template, 'Zebra')
    '''
    def __init__(self, template, printer=z):
        self.printer = printer
        self.template = template

    def print_out(self,content):
        if content != None:
            payload = self.template.format(**content)
            self.printer.output(payload)


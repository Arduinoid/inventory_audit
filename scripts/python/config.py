# Configuration file for Audit System
# Use this file to change key settings used to setup the Audit system
# environment on a server

# This is the name of the Zebra thermal printer hooked up to the station
PRINTER_NAME = 'ZDesigner GK420d'
# File path where the generated files from the audit agent will go. This is also
# the path the is used to watch for new files being created
FILE_PATH = '//10.11.203.100/nfs/server-specs'
# The name that the CSV file will have for all generated reports
REPORT_NAME = 'server_audit'
# Label dimensions go here
# This needs to be a dictionary that has the three following values
# 'label_size', 'font_size', 'margin'
# label_size need to have a tuple value which would be (<width>, <height>) in inches
# font_size and margin are integer values
LABEL_DIMENSIONS = {
    'label_size': (3,1),
    'font_size': 30,
    'margin': 20
}
# Inventory Audit system

This project is used to help take inventory of incoming server parts. The idea is to be able to **PXE Boot** each server and pull hardware info from them. This will be achieved using a simple **Ubuntu** image running some command line tools and scripts. The results of which will be stored in a database for use in tracking the life cycle of server parts in inventory.

## Basic Functionality

### _Current state_

* Boot Linux image from USB
* Run `get-specs.sh` script to gather server info
* Running the generated `cleanup.sh` will delete the files created on the server and send them to a file share on the network

### _In Progress_

* Python scripts to parse file contents
* **Django REST framework API** to consume parsed info and write to a **SQLite** database

### _ToDo_

* Design database to accommodate inventory usage
* Make Linux image talk directly to API instead of writing files to network share
* Build a front end to interact with the inventory database
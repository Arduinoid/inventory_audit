#!/bin/bash

INET=`ifconfig -a | sed -n 's/^\S/&/p' | sed -n 's/^e.*/&/p' | cut -d ' ' -f 1`
ETHCONF=/etc/network/interfaces

# Initialize interface file
echo "Setting up interface..."
echo "source /etc/network/interfaces.d*" > $ETHCONF
echo "auto lo" >> $ETHCONF
echo "iface lo inet loopback" >> $ETHCONF
echo "" >> $ETHCONF

# Build out interface file config
for i in $INET
do
    echo "auto $i" >> $ETHCONF
    echo "iface $i inet dhcp" >> $ETHCONF
    echo "" >> $ETHCONF
done

# Bring up each interface
for i in $INET
do
    dhclient $i
    IPADDR=`ip addr show $i | grep -i inet | sed -n 's/\s*//p' | cut -d ' '  -f 2`
    if [ -z "$IPADDR"]
    then
        dhclient $i
        IPADDR=`ip addr show $i | grep -i inet | sed -n 's/\s*//p' | cut -d ' '  -f 2`
    fi
    
    echo "Interface $i is now setup"
    echo $IPADDR
    echo ""
done

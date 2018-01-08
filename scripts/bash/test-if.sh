#!/bin/bash

INET=`ifconfig -a | sed -n 's/^\S/&/p' | sed -n 's/^e.*/&/p' | cut -d ' ' -f 1`
ETHCONF=/etc/network/interfaces
ECODE=0

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
    UPLINK=`cat /sys/class/net/$i/operstate`
    if [ "$UPLINK" = "up" ] || [ "$UPLINK" = "unknown" ]
    then
        dhclient $i
        IPADDR=`ip addr show $i | grep -i inet | sed -n 's/\s*//p' | cut -d ' '  -f 2`
        if [ -z "$IPADDR" ]
        then
            dhclient $i
            IPADDR=`ip addr show $i | grep -i inet | sed -n 's/\s*//p' | cut -d ' '  -f 2`
        fi
        [ ! -z $IPADDR ] && echo "Interface $i is now setup with ip: $IPADDR"; exit 0 || echo "FAILED to setup interface $i"; ((ECODE++))
    else
        echo "interface $i is not connected"
        ((ECODE++))
    fi
done
exit $ECODE

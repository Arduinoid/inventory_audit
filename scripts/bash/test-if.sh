#!/bin/sh

INET=`ifconfig | cut -d ' ' -f 1 | sed -n -e '1p'` | grep -i e
ETHCONF=/etc/network/interfaces

if [ -z "$INET" ]
then
    INET=`ifconfig -a | cut -d ' ' -f 1 | sed -n -e '1p'`
    echo "source /etc/network/interfaces.d*" > $ETHCONF
    echo "auto lo" >> $ETHCONF
    echo "iface lo inet loopback" >> $ETHCONF
    echo "" >> $ETHCONF
    echo "auto $INET" >> $ETHCONF
    echo "iface $INET inet dhcp" >> $ETHCONF

    dhclient $INET
    mount 10.11.203.100:/nfs /mnt
else
    echo 'Interface is up'
fi


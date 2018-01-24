#!/bin/bash

INET=`ifconfig -a | sed -n 's/^\S/&/p' | sed -n 's/^e.*/&/p' | cut -d ' ' -f 1`
ETHCONF=/etc/network/interfaces
ECODE=0

up_link() {
    for i in $@
    do
        echo "Attempting to raise interface: $i"
        ip link set up $i
        sleep 3
        STATE=`cat /sys/class/net/$i/carrier`
        if [ $STATE -eq 1 ]
        then
            ifup $i &
            ECODE=0
            break
        else
            ((ECODE++))
        fi
    done
}

# Initialize interface file
echo "Setting up interface..."
echo "source /etc/network/interfaces.d*" > $ETHCONF
echo "auto lo" >> $ETHCONF
echo "iface lo inet loopback" >> $ETHCONF
echo "" >> $ETHCONF

# Build out interface file config
echo "Creating config file"
for i in $INET
do
    echo "auto $i" >> $ETHCONF
    echo "iface $i inet dhcp" >> $ETHCONF
    echo "" >> $ETHCONF
done
echo "Attempting to raise interfaces..."
up_link $INET
if [ $ECODE -gt 0 ]
then
    ECODE=0
    up_link $INET
fi
echo "network script exited with code: $ECODE" >> /scripts/script-log

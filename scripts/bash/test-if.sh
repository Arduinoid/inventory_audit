#!/bin/bash

INET=`ifconfig -a | sed -n 's/^\S/&/p' | sed -n 's/^e.*/&/p' | cut -d ' ' -f 1`
ETHCONF=/etc/network/interfaces
ECODE=0

check_ips() {
    for i in $INET
    do
        IPADDR=`ip addr show $i | grep -i inet | sed -n 's/\s*//p' | cut -d ' ' -f 2`
        [ ! -z "$IPADDR" ] && echo "Interface $i has ip: $IPADDR"; exit 0 || echo "Couldn't assign interface $i an ip"; ((ECODE++))
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
    echo "Obtaining IP address from DHCP server"
    # dhclient $i
    # sleep 1
    # IPADDR=`ip addr show $i | grep -i inet | sed -n 's/\s*//p' | cut -d ' ' -f 2`
    # [ ! -z "$IPADDR" ] && echo "Interface $i has ip: $IPADDR"; exit 0 || echo "Couldn't assign interface $i an ip"; ((ECODE++))
done

/etc/init.d/networking restart
ifup -a
check_ips

if [ $ECODE -gt 0 ]
then
    ECODE=0
    ifup -a
    check_ips
fi
exit $ECODE

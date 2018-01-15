#!/bin/bash

INET=`ifconfig -a | sed -n 's/^\S/&/p' | sed -n 's/^e.*/&/p' | cut -d ' ' -f 1`
ETHCONF=/etc/network/interfaces
ECODE=0

check_ips() {
    for i in $@
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
done

echo "Going to restart network"
/etc/init.d/networking restart
ifup -a > /dev/null 2>&1 
check_ips $INET

if [ $ECODE -gt 0 ]
then
    ECODE=0
    ifup -a > /dev/null 2>&1
    check_ips $INET
fi
exit $ECODE

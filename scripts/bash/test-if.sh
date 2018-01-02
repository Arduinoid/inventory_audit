#!/bin/sh

INET=`ifconfig | cut -d ' ' -f 1 | sed -n -e '1p' | grep -i e`
ETHCONF=/etc/network/interfaces
NFS="10.11.203.100:/nfs"

if [ -z "$INET" ]
then
    echo "Setting up interface..."
    INET=`ifconfig -a | cut -d ' ' -f 1 | sed -n -e '1p'`
    echo "source /etc/network/interfaces.d*" > $ETHCONF
    echo "auto lo" >> $ETHCONF
    echo "iface lo inet loopback" >> $ETHCONF
    echo "" >> $ETHCONF
    echo "auto $INET" >> $ETHCONF
    echo "iface $INET inet dhcp" >> $ETHCONF

    dhclient $INET
    echo "Interface $INET is now setup"
    mount $NFS /mnt
else
    echo 'Interface is up'
    MOUNT=`df -h | grep -i /mnt`
    if [ -z "$MOUNT" ]
    then
        echo "Mounting NFS from $NFS ..."
        mount 10.11.203.100:/nfs /mnt
        echo "Mount complete"
    else
        echo "NFS mounted from $NFS"
    fi
fi


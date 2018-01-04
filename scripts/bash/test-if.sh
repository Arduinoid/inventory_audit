#!/bin/bash

INET=`ifconfig -a | sed -n 's/^\S/&/p' | sed -n 's/^e.*/&/p' | cut -d ' ' -f 1`
ETHCONF=/etc/network/interfaces
NFS="10.11.203.100:/nfs"

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
    echo "Interface $i is now setup"
done

MOUNT=`df -h | grep -i /mnt`
if [ -z "$MOUNT" ]
then
    echo "Mounting NFS from $NFS ..."
    mount $NFS /mnt

    # Check if mounted after mount attempt
    MOUNT=`df -h | grep -i /mnt`
    [ ! -z "$MOUNT"] && echo "Mount from $NFS complete" || echo "FAILED Mount from $NFS"

else
    echo "NFS already mounted from $NFS"
fi


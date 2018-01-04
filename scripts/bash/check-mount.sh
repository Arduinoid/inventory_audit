#!/bin/bash

SERVER="10.11.203.100:/nfs"
MOUNT=`df | grep -i nfs`
COUNT=1

while [ -z "$MOUNT" ]
do
    echo "Attempting mount try number: $COUNT"
    mount $SERVER /mnt
    ((COUNT++))
    sleep 2
    MOUNT=`df | grep -i nfs`
done

if [ ! -z "$MOUNT" ]
then
    echo "NFS mounted"
    echo $MOUNT
fi

#!/bin/bash

SERVER="10.11.203.100"
MOUNT=`df | grep -i nfs`
COUNT=1
PCOUNT=0

echo "Attempting to reach NFS server at $SERVER"
ping -c 1 $SERVER > /dev/null
[ $? -eq 0 ] && echo "NFS server at $SERVER reached" || echo "First attempt failed, going to retry..."
while [ $? -ne 0 ]
do
    ((PCOUNT++))
    echo "Ping retry count: $PCOUNT"
    ping -c 1 $SERVER > /dev/null
    [ $PCOUNT -eq 4 ] && echo "Could not reach NFS server at $SERVER"; exit $PCOUNT
done

echo "Attempting mount..."
mount $SERVER:/nfs /mnt
MOUNT=`df | grep -i nfs`
[ ! -z "$MOUNT" ] && echo "NFS mounted"; exit 0 || echo "Failed to mount NFS"; exit 1

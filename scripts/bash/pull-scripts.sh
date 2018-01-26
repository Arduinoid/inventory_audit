#!/bin/bash

MOUNT=`df | grep -i nfs`
SRC=/mnt/scripts/*
DEST=/tmp/scripts

if [ ! -z "$MOUNT" ]
then
    echo "Begin script and config sync.."
    mkdir -p /tmp/scripts
    rsync -cv $SRC $DEST
    echo "Finished syning"

    echo "Distributing files throughout system..."
    cp $DEST/get-specs.sh /scripts/
    cp $DEST/check-mount.sh /scripts/ 
    cp $DEST/test-if.sh /scripts/
    cp $DEST/pull-scripts.sh /scripts/
    cp $DEST/config /home/tv/Tom/ 
    cp $DEST/startup.sh /scripts/
    cp $DEST/dhclient.conf /etc/dhcp/
else
    echo "NFS mount not availible"
fi

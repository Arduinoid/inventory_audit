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
    cp $DEST/get-specs.sh /scripts/get-specs.sh 
    cp $DEST/check-mount.sh /scripts/check-mount.sh 
    cp $DEST/test-if.sh /scripts/test-if.sh
    cp $DEST/pull-scripts.sh /scripts/pull-scripts.sh
    cp $DEST/config /home/tv/Tom/config 
    cp $DEST/startup.sh /scripts/startup.sh
else
    echo "NFS mount not availible"
fi

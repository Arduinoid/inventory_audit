#!/bin/bash

MOUNT=`df | grep -i nfs`
SRC=/mnt
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
    cp $DEST/rc.local /etc/rc.local
else
    echo "NFS mount not availible"
fi

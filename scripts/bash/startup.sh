#!/bin/bash

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games

echo ">>>> Startup script ran at $(date)" >> /scripts/test
/scripts/test-if.sh
/scripts/check-mount.sh
/scripts/get-specs.sh
/scripts/cleanup.sh

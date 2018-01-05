#!/bin/bash

STAG=`dmidecode -t 1 | grep -i serial | sed -e 's/^.*:\s//' -e 's/\s//g'`
MANU=`dmidecode -t 1 | grep -i manufact | sed -e 's/^.*:\s//' | cut -d ' ' -f 1`
DIRNAME=$STAG-spec
DIRPATH="/tmp/$DIRNAME"
CLEANUP="/scripts/cleanup.sh"

mkdir $DIRPATH

echo "#!/bin/sh" > $CLEANUP
echo "cp -r $DIRPATH /mnt/server-specs" >> $CLEANUP
echo "rm $CLEANUP" >> $CLEANUP
chmod +x $CLEANUP

dmidecode -t 1 | sed -e 's/\t//g' -e 's/\s//g' | sed -n -e '/Manufacturer/p' -e '/Product/p' -e '/Serial/p' > $DIRPATH/dmi-system.txt
dmidecode -t 3 | sed -e 's/\t//g' -e 's/\s//g' | sed -n '/Asset/p' >> $DIRPATH/dmi-system.txt
dmidecode -t 17 | sed -e 's/\t//g' -e 's/\s//g' | sed -n -e '/Manufacturer/p' -e '/Part/p' -e '/Serial/p' -e '/Size/p' -e'/Type/p' -e '/Rank/p' > $DIRPATH/dmi-memory.txt
lshw -json -quiet > $DIRPATH/lshw-report.json
lshw -html -quiet > $DIRPATH/lshw-report.html
lshw -businfo -quiet > $DIRPATH/lshw-businfo.json
lshw -json -class processor -quiet > $DIRPATH/lshw-processor.json
lshw -json -class memory -quiet > $DIRPATH/lshw-memory.json
lshw -json -class disk -quiet > $DIRPATH/lshw-disk.json
lshw -json -class network -quiet > $DIRPATH/lshw-network.json
hpdiscovery -f $DIRPATH/hpdiscovery-report.xml
lspci -nn | grep -i net > $DIRPATH/lspci-net.txt


case "$MANU" in
"HP")
    hpssacli ctrl slot=0 pd all show detail > $DIRPATH/hp-drives.txt
    ;;
"Dell")
    MegaCli64 -AdpAllInfo -aAll > $DIRPATH/dell-controller.txt
    MegaCli64 -PDList -aALL > $DIRPATH/dell-drives.txt
    ;;
*)
    lshw -class disk -class storage -quiet -json > $DIRPATH/server-drives.json
    ;;
esac


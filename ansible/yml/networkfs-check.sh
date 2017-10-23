#!/bin/bash
b=""
while read _ _ mount _
    do a="`timeout 2 stat -t "$mount"`"
        if [ -z "$a" ];then 
            b="$mount:$b"
        fi 
    done < <(mount -t cifs )
while read _ _ mount _
    do a="`timeout 2 stat -t "$mount"`"
        if [ -z "$a" ];then
            b="$mount:$b"
        fi
    done < <(mount -t nfs )
if [ -z "$b" ];then
    echo "NetdiskOK"
else
    echo $b
fi

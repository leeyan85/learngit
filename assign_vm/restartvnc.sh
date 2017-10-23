#!/bin/bash 
ports="`ps -ef | grep vnc | grep -v 'grep' | awk '{print $9}' | grep -v iconic`"

if [ "`echo $ports`" != "" ]; then 
    for i in `echo "$ports"`;
        do  
           sudo  su - andbase -c "vncserver -kill $i"
           sudo rm -rf /tmp/.X*
           sudo  su - andbase -c "vncserver $i"
        done
    for i in `echo ":10 :11 :12"`
        do 
            sudo  su - andbase -c "vncserver $i"
        done
else 
    for i in `echo ":10 :11 :12"`
        do 
            sudo  su - andbase -c "vncserver $i"
        done

fi

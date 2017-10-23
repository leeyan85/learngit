#!/bin/bash 
sudo killall Xtightvnc
sudo rm -rf /tmp/.X*
for i in `echo ":10 :11 :12"`
do 
    sudo  su - andbase -c "vncserver $i"
done

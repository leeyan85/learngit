#!/bin/bash

#sudo su - andbase -c "vncserver -kill :10"
#sudo su - andbase -c "vncserver -kill :11"
#sudo su - andbase -c "vncserver -kill :12"
shopt -s extglob
#kill vnc port
name_pid=`find /home/andbase/.vnc/ -name vm*.pid`

for i in $name_pid
do
        vncon_pid=`echo $i | sed 's/.*\:\(.*\)\..*/\1/'`
        sudo su - andbase -c "vncserver -kill :$vncon_pid"
done

# rm workspace
cd /letv/workspace
rm -rf *
ls -a | awk '/^\./&&$1 != "."&&$1 != ".."' | xargs rm -rf {}

cd /tmp/tools
tar -xvf andbase.tar

mv /home/andbase /letv/workspace
cp -rf home/andbase /home/

rm -rf /letv/workspace/*
cd /letv

rm -rf !(jenkins_slave|lost+found|Qualcomm|tmp|tools|workspace)

cd /tmp

shopt -s extglob
rm -rf !(andbase|hsperfdata_letv|hsperfdata_root|root|tools)


hostname | grep -e "vm-10-120" -e "vm-10-212" > /dev/null
if [ $? == 0 ];then
cp /tmp/tools/gitconfig-us /home/andbase/.gitconfig
cp /tmp/tools/gitconfig-us /home/andbase/.gitconfig.sample
fi


chown -R andbase:andbase /home/andbase
rm -rf /tmp/tools/*
mkdir /tmp/tools/

sudo su - andbase -c "vncserver :10"
sudo su - andbase -c "vncserver :11"
sudo su - andbase -c "vncserver :12"
sudo su - root -c "echo 'andbase:DtK1DLGUo' | chpasswd"

ln -s /home/andbase/.ssh/vmvnc_manage.py /usr/bin/vmvnc
chmod  777 /home/andbase/.ssh/vmvnc_manage.py
chmod 777 /home/andbase/.ssh/vnc_instruct.py

#!/bin/bash

echo "n
p


w
" | sudo fdisk /dev/vda

sudo partprobe
sudo mkfs.ext4 /dev/vda4
sudo mount /dev/vda4 /letv
sudo echo "/dev/vda4 /letv ext4 defaults 0 0" >> /etc/fstab

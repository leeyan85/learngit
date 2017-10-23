#!/usr/bin/python
import actions
import os
import sys
import re

servers=sys.argv[1]
if re.search("10.120|10.212",servers):
    Nfs_serverip='10.120.0.40'
else:
    Nfs_serverip='10.148.16.47'
if __name__=='__main__':
    print Nfs_serverip
    actions.create_nfs_directory(servers,Nfs_serverip)
    serverips=servers.split(',')
    actions.generate_servers_queue(serverips)
    actions.thread_run(actions.precheck,actions.target_servers_queue,Nfs_serverip)
    actions.thread_run(actions.remote_mount_space,actions.umount_servers_queue,Nfs_serverip)

#!/usr/bin/python
#-*- coding:utf-8 -*-  
import os,sys
import datetime
import time
from jira.client import JIRA
from jira.exceptions import JIRAError
import random
reload(sys)
sys.setdefaultencoding('UTF-8')
import json
sys.path.append('E:\workspace\SCMDB')
sys.path.append('E:\workspace\central2')
sys.path.append('/letv/scripts/SCMDB')
sys.path.append('/letv/scripts/mount_space')
#当使用django作为第三方的脚本调用时必须添加
os.environ['DJANGO_SETTINGS_MODULE'] = 'SCMDB.settings'
import json
import django
import calendar
django.setup()
from servermanage import models
import actions
from django.core.exceptions import ObjectDoesNotExist


def generate_random_password():
    random_string=''.join(random.sample('zyxwvutsrqponmlkjihgfedcba123456789',6))
    return random_string


def vnc_passwd(ip,random_password):
    server=actions.Server(ip,username='letv')
    server.remote_command="(echo %s;echo %s) |sudo su - andbase -c vncpasswd"%(random_password,random_password)
    server.connect()
    server.exec_remote_command()    
    return True
    

def smb_passwd(ip,random_password):
    server=actions.Server(ip,username='letv')
    server.remote_command="(echo %s;echo %s) |sudo smbpasswd andbase"%(random_password,random_password)
    server.connect()
    server.exec_remote_command()

def account_passwd(ip,random_password):
    server=actions.Server(ip,username='letv')
    server.remote_command="echo 'andbase:%s' | sudo chpasswd"%(random_password)
    server.connect()
    server.exec_remote_command()

def write_random_passwd(ip,random_password):
    server=actions.Server(ip,username='letv')
    configfile='/home/andbase/.ssh/vmsetup/vm_setup.conf'
    server.remote_command="sudo chmod 777 /home/andbase/.ssh;sudo chmod 777 %s; echo '[pass]' >> %s; echo \"pas = %s\" >> %s;sudo chmod 766 %s;sudo chmod 700 /home/andbase/.ssh"%(configfile,configfile,random_password,configfile,configfile)
    #print server.remote_command
    server.connect()
    server.exec_remote_command()

def set_random_passwd(ip,random_password):
    vnc_passwd(ip,random_password)
    smb_passwd(ip,random_password)
    account_passwd(ip,random_password)
    return True

if __name__=='__main__':
    for ip in sys.argv[1].split(','):
        random_password=generate_random_password()
        set_random_passwd(ip,random_password)
        print random_password

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
sys.path.append('/letv/scripts/SCMDB')
sys.path.append('/letv/scripts/mount_space')
sys.path.append('E:\workspace\central2')
#当使用django作为第三方的脚本调用时必须添加
os.environ['DJANGO_SETTINGS_MODULE'] = 'SCMDB.settings'
import json
import django
import calendar
django.setup()
from servermanage import models
import actions
from django.core.exceptions import ObjectDoesNotExist
from ssh_key import *
from jira_recycle_vm import VM

issue_link_type="Relates"
InUse_status_id='11'
Unassign_status_id='41'
def get_vm_owner_according_ip(ip_list_file):
    ip_list=[]
    b={}
    with open('%s'%ip_list_file,'r') as f:
        ips=f.readlines()
    for ip in ips:
        ip_list.append(ip.strip('\n'))

    for i in ip_list:
        a=i.split('\t')
        b[a[0]]=a[1]
    return b


server_group_dict=get_vm_owner_according_ip('group.txt')
print server_group_dict
for host,value in server_group_dict.items():
    print host,value
    if value in ['IOV','IOV-EUI','IOV-OTHER']:
        value="IOV"
    elif value in ['MOBILE-CAMERA','MOBIEL-MODEM','MOBIEL',"MOBILE"]:
        value="Mobile"
    elif value in ['TV','TV-EUI']:
        value='TV'
    elif value in ['PLATFORM']:
        value='Platform'
    elif value=='LeEco':
        value="US"
    host=models.Hosts.objects.get(name=host)
    print host.host
    host_inventory=models.HostInventory.objects.get(hostid=host.hostid)
    host_inventory.tag=value
    host_inventory.save()
   
    

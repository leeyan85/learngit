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

from zabbix_delete_hosts import get_InUse_ip
from ump import modify_zabbix_info_according_ip
def get_notes(filename):
    ip_list=[]
    with open(filename) as f:
        hosts=f.readlines()
    for host in hosts:
        info=host.split(';')
        print info
        note=info[1]
        ip=info[0]
        ip_list.append({ip:note})
        
    return ip_list
if __name__=='__main__':
    ip_list=get_notes(sys.argv[1])
    for host in ip_list:
        print type(host)
        for key,value in host.items():
            print key,value.strip()
            modify_zabbix_info_according_ip(key,value.strip())

#!/usr/bin/python
#-*- coding:utf-8 -*-  
import os,sys
import datetime
import time
from jira.client import JIRA
reload(sys)
sys.setdefaultencoding('UTF-8')
import json
sys.path.append('E:\workspace\SCMDB')
sys.path.append('/letv/scripts/SCMDB')
#当使用django作为第三方的脚本调用时必须添加
os.environ['DJANGO_SETTINGS_MODULE'] = 'SCMDB.settings'
import json
import django
import calendar
django.setup()
from servermanage import models
from django.core.exceptions import ObjectDoesNotExist

def get_all_vm_tag():
    a=[]
    hosts = models.Hosts.objects.filter(name__startswith='vm')
    for host in hosts:
        host_inventory = models.HostInventory.objects.get(hostid=host.hostid)
        if host_inventory.tag not in a:
            print host_inventory.tag

get_all_vm_tag()

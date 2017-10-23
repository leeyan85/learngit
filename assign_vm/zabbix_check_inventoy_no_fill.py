#!/usr/bin/python
#-*- coding:utf-8 -*-  
import os,sys
import datetime
import time
pro_dir=os.getcwd()
sys.path.append(pro_dir)
sys.path.append('E:\workspace\SCMDB')
sys.path.append('/letv/scripts/SCMDB')
#当使用django作为第三方的脚本调用时必须添加
os.environ['DJANGO_SETTINGS_MODULE'] = 'SCMDB.settings'
import json
import django
import calendar
django.setup()

import xlsxwriter
from servermanage import models

import json,sys,argparse
from zabbix_api import ZabbixAPI
from django.core.exceptions import ObjectDoesNotExist

server = "http://zabbix.devops.letv.com/zabbix"
username = "Admin"
password = "Admin@zabbix"
zapi = ZabbixAPI(server=server, path="", log_level=0)
zapi.login(username, password)
from zabbix_util import get_hostid_according_ip
if __name__=='__main__':
    host_inventorys=models.HostInventory.objects.all()
    for host_inventory in host_inventorys:
        if host_inventory.location=="":
            interfaces=models.Interface.objects.filter(hostid=host_inventory.hostid.hostid)
            print interfaces[0].ip
            

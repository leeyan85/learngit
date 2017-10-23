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

from zabbix_util import get_InUse_ip, check_zabbix_ip
from ump import http_get

def get_servers_tree_mapping(result,):
    exist_ip=[]
    servers_tree={}
    for server in result['data']:
         #print json.dumps(server,indent=4,ensure_ascii=False)
         tree=server["servicetree"][0]["parents"]+'_'+server["servicetree"][0]["name"]
         
         for ip_data in server["ip_data"]:
             
             ip=ip_data['ipaddr']
             if ip in not_in_zabbix_list:
                 print ip,tree
                 not_in_zabbix_list.remove(ip)
    for ip in not_in_zabbix_list:
        print ip
                 
if __name__=='__main__':
    not_in_zabbix_list=[]
    in_zabbix_list=[]
    ip_list=get_InUse_ip(sys.argv[1])
    for ip in ip_list:
        a=check_zabbix_ip(ip)
        if a=="not in zabbix":
            not_in_zabbix_list.append(ip)
        else:
            in_zabbix_list.append(ip)
            
    print len(not_in_zabbix_list),len(in_zabbix_list)
    result=http_get()
    get_servers_tree_mapping(result)

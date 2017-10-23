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

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", help="host name")
    parser.add_argument("-G", "--group", help="group name")
    # 解析所传入的参数
    args = parser.parse_args()    
    if not args.host:
        print "please input the host"
        return False
    return args
     
def get_host_id(host):
    get_host_id = zapi.host.get(
        {
            "output": "hostid",
            "filter": {
                "host":host.split(",")
            }
        }
    )   
    host_id = []
    host_id=[I['hostid'] for I in get_host_id]
    return get_host_id

def get_InUse_ip(filename):
    ip_list=[]
    with open(filename) as f:
        hosts=f.readlines()
    for host in hosts:
        ip_list.append(u'%s'%host.strip("\n"))
    return ip_list

def get_group_id():
    get_group_id=zapi.hostgroup.get(
    {
        "output": "groupid",
        "filter": {
            "name": [
                "Sepical VM",
                "andbase VM",
            ]
        }
    }
    )
    return get_group_id

def get_hostid_according_ip(ip):
    try:
       interfaces=models.Interface.objects.filter(ip=ip)
       if len(interfaces)==0:
           print ip," not in zabbix"
           return "not in zabbix"
       print interfaces
       interface=interfaces[0]
       hostid=interface.hostid.hostid
       print ip,hostid
       return hostid
    except ObjectDoesNotExist:
       print ip," not in zabbix"
       return "not in zabbix"
    
def delete_host(host_id):
    hosts_id=[host_id]
    hosts_delete = zapi.host.delete(hosts_id)
    return "host delete success!"
    

def host_group_massadd(group,hosts):
    params={"groups":group,"hosts":hosts}
    zapi.hostgroup.massadd(params)
    
if __name__ == "__main__":
    filename=sys.argv[1]
    not_in_zabbix=[]
    hosts_ip=get_InUse_ip(filename)
    for ip in hosts_ip:
        hostid=get_hostid_according_ip(ip)
        if hostid=='not in zabbix':
            not_in_zabbix.append(ip)
        else:
            delete_host(hostid)
    for ip in not_in_zabbix:
        print ip

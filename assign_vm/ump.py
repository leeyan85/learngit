#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib2
import re
USLA=re.compile(ur"洛杉矶") #洛杉矶机房
CNBJ=re.compile(ur"北京") #北京机房
CNSZ=re.compile(ur"深圳")#深圳机房
CNGZ=re.compile(ur"广州") #广州机房
USWT=re.compile(ur"华盛顿") #华盛顿
INND=re.compile(ur"新德里") #印度新德里
CNHK=re.compile(ur"香港") #中国香港
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
'''
server = "http://zabbix.devops.letv.com/zabbix"
username = "Admin"
password = "Admin@zabbix"
zapi = ZabbixAPI(server=server, path="", log_level=0)
zapi.login(username, password)
'''

def get_InUse_ip(filename):
    jerkens_ip_list=[]
    with open(filename) as f:
        hosts=f.readlines()
    for host in hosts:
        jerkens_ip_list.append(u'%s'%host.strip("\n"))
    return jerkens_ip_list


def http_get():
    url="http://ump.letv.cn/api/cmdb/servicetree/androidDevice?token=fc87fcc85afcbb9bc0585ef1154143ea"
    response = urllib2.urlopen(url)
    #result_js=json.loads(b)
    result_js=json.loads(response.read())
    #print json.dumps(result_js,indent=4,ensure_ascii=False)
    return result_js
    
def get_tree_list(ump_server_data):
    tree_nodes={}
    for server in ump_server_data['data']:
        a=server['servicetree'][0]['parents']+'_'+server['servicetree'][0]['name']
        if a not in tree_nodes.keys():
            tree_nodes[a]=[]
        else:
            serverip=server["ip_data"][0]["ipaddr"]
            serveridc=server["lingshu_idc"]
            serverinfo={"ip":serverip,"idc":serveridc}
            tree_nodes[a].append(serverinfo)
            
        
            
    
    print json.dumps(tree_nodes,indent=4,ensure_ascii=False)
    '''for node in tree_nodes:
        print node
        print '_'.join(node.split('_')[2:])'''
        
    
            

def get_city_list(IDC,ump_server_data):
    server_list=[]
    for server in ump_server_data['data']:
        if eval(IDC).search(server['lingshu_idc']):#洛杉矶机房
            tmp={}            
            server['lingshu_idc'], server['ip_data'][0]['ipaddr'],server['servicetree'][0]['parents']+'_'+server['servicetree'][0]['name']
            tmp['IDC']=IDC
            tmp['ipaddr']=server['ip_data'][0]['ipaddr']
            a=server['servicetree'][0]['parents']+'_'+server['servicetree'][0]['name']
            server_list.append(tmp)
    print len(server_list),server_list
    return len(server_list),server_list






def match_tree(result):
    CI=re.compile(ur"持续集成")
    Infru=re.compile(ur"基础设施")
    Code=re.compile(ur"代码托管")
    Storage=re.compile(ur"存储服务")
    if CI.search(tree) or Infru.search(tree) or Code.search(tree) or Storage.search(tree):
        if server['assettype']==u"公司实体资产":
            print tree, ip, u"物理机"
        else:
            print tree, ip, u"虚拟机"

def write_json(filename,data):
    f=file(filename,'wb')
    json.dump(data,filename)
    f.close()


def write_file(filename,data):
    f=file(filename,'a+')
    f.write(data)
    f.close()


def check_ip_exist(ip_list,result):
    exist_ip=[]
    servers_tree={}
    for server in result['data']:
         #print json.dumps(server,indent=4,ensure_ascii=False)
         tree=server["servicetree"][0]["parents"]+'_'+server["servicetree"][0]["name"]

         for ip_data in server["ip_data"]:

             ip=ip_data['ipaddr']
             if ip in ip_list:
                 print ip,tree
    
def get_servers_tree_mapping(result):
    exist_ip=[]
    servers_tree={}
    for server in result['data']:
         #print json.dumps(server,indent=4,ensure_ascii=False)
         tree=server["servicetree"][0]["parents"]+'_'+server["servicetree"][0]["name"]
         
         for ip_data in server["ip_data"]:
             
             ip=ip_data['ipaddr']
             if ip_data['type']==u'内网':
                 if server['assettype']==u"公司实体资产":
                     type=u'物理机'
                     print tree,ip,type
                     exist_ip.append(ip)
                     print ip,tree
                     modify_zabbix_info_according_ip(ip,tree)
                 else:
                     type=u'虚拟机'
                     print tree, ip, type
                     exist_ip.append(ip)
                     modify_zabbix_info_according_ip(ip,tree)
                 if tree in servers_tree.keys():
                     servers_tree[tree].append((ip,server['assettype']))
                 else:
                     servers_tree[tree]=[]
                     servers_tree[tree].append((ip,server['assettype']))

             else:
                 modify_zabbix_info_according_ip(ip,tree)
    #json_data=json.dumps(servers_tree,indent=4,ensure_ascii=False)
    #write_file("server.txt","%s,%s,%s"%(tree,ip,type))

def get_idc_list(ump_server_data):
    server_list=[]
    for server in ump_server_data['data']:
        idc=server['idc']
        for ip in server['ip_data']:
            ip=server['ip_data'][0]['ipaddr']
            tree=server['servicetree'][0]['parents']+'_'+server['servicetree'][0]['name']
            if server['assettype']==u"公司实体资产":
                modify_zabbix_info_according_ip(ip,tree,idc)
            else:
                pass


def modify_zabbix_info_according_ip(ip,notes):
    try:
       interfaces=models.Interface.objects.filter(ip=ip)
       interface_items=len(interfaces)
       if interface_items == 0:
           print ip,'not in zabbix'
           return "not in zabbix"
       else:
           interface=interfaces[0]
           hostid=interface.hostid.hostid
           host_inventory=models.HostInventory.objects.get(hostid=hostid)
           host_inventory.tag=notes
           host_inventory.save()
           return hostid
    except ObjectDoesNotExist:
       print ip," not in zabbix"
       return "not in zabbix"

def check_zabbix_ip(ip):
    try:
       interfaces=models.Interface.objects.filter(ip=ip)
       print ip,len(interfaces)
       interface_items=len(interfaces)
       if interface_items == 0:
           print ip,'not in zabbix'
           return "not in zabbix"
       else:
           interface=interfaces[0]
           hostid=interface.hostid.hostid
           return hostid
    except ObjectDoesNotExist:
       print ip," not in zabbix"
       return "not in zabbix"

if __name__=="__main__":
    result = http_get()
    #print result['data']
    #a=json.dumps(result,indent=4,ensure_ascii=False)
    #print a 
    idc=[]
    ip_list=[]
    vm_list=[]
    vm=re.compile(ur"云主机")
    internal_net=re.compile('^10\.')
    retired_idc=[u'中国_北京_北京_海淀_电信通_苏州桥_10_-1_C',u'中国_北京_北京_海淀_电信通_苏州桥_10_1_B01',u'中国_北京_北京_朝阳_电信通_惠普_112_2_4',u'中国_北京_北京_大兴_电信通_亦庄_东配楼_1_X',u'中国_北京_北京_大兴_电信通_亦庄_主楼_1_MD06',u'中国_广东_广州_南沙_天地祥云_平谦_C_2_204']
    for server in result['data']:
        print json.dumps(server,indent=4,ensure_ascii=False) 
        ip=[] 
        for ip_data in server['ip_data']:
            if internal_net.search(ip_data['ipaddr']):
                ip.append(ip_data['ipaddr'])
        
        
        tree='_'.join([server['servicetree'][0]['parents'],server['servicetree'][0]['name']])
        if server['idc'] not in retired_idc and server["assettype"]==u"公司实体资产" and server['servicetree'][0]['name']==u'机房迁移申请机器':
            modify_zabbix_info_according_ip(ip,tree)
            ip_list.append({'host_ips':ip,'host_tree':tree})
        elif server['idc'] not in retired_idc and server["assettype"]==u"公司虚拟资产" and vm.search(tree) is None:
            modify_zabbix_info_according_ip(ip,tree)
            vm_list.append({'host_ips':ip,'host_tree':tree})
    print '*'*20,u'物理机 list'
    for host in ip_list: 
        print json.dumps(host['host_ips'],ensure_ascii=False)
    print '*'*20,u'虚拟机 list'
    for host in vm_list:
        print json.dumps(host['host_ips'],ensure_ascii=False)
        
    #for i in 
    #with open ('/tmp/ump.txt','w') as f:
    #     f.write(a)
    #get_idc_list(result)
    #print json.dumps(result,indent=4,ensure_ascii=False)
    #ip_list=get_InUse_ip(sys.argv[1])
    #check_ip_exist(ip_list,result)
    get_servers_tree_mapping(result)
    #for ip in ip_list:
        #check_zabbix_ip(ip)

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
sys.path.append('/letv/scripts/SCMDB')
sys.path.append('/letv/scripts/mount_space')
sys.path.append('/letv/scripts/ansible/api')
#当使用django作为第三方的脚本调用时必须添加
os.environ['DJANGO_SETTINGS_MODULE'] = 'SCMDB.settings'
import json
import django
import calendar
django.setup()
from servermanage import models
import actions
from django.core.exceptions import ObjectDoesNotExist
from ansible_api_v2 import run_playbook,run_order

issue_link_type="Relates"
InUse_status_id='11'
Unassign_status_id='41'

jira=JIRA(basic_auth=("username","xxxxxxx@"), server="http://jira.letv.cn/")


class VM(object):

    def __init__(self, ipAddress, userName, remoteUser):
        self.ipAddress = [ ipAddress ]
        self.userName = userName
        self.remoteUser = remoteUser

        '''init base info'''
        self.webInventory = ansible.inventory.Inventory(self.ipAddress)
        self.remotePort = 22
        self.timeOut = 10
        self.priKeyFile = '/home/%s/.ssh/id_rsa'%userName



def get_vm_owner_according_ip(ip_list_file):
    ip_list=[]
    with open('%s'%ip_list_file,'r') as f:
        ips=f.readlines()
    for ip in ips:
        ip_list.append(ip.strip('\n'))
        #host_groups=models.HostsGroups.objects.filter(hostid=host.hostid)
        #host_group=host_groups[1]
        #print host_group.groupid,host_group.groupid.name
    return ip_list

def change_request_status_to_TBrecycle(ip):
    to_status_id='21'
    requests=jira.search_issues("project = SEEVM AND status = InUse AND VMIP ~ %s" %ip,maxResults=2)
    if len(requests)==0:
        print ip,"not request"
        return 0
    else:
        request=requests[0]
    if len(request.fields.customfield_13414.split(','))>1:
        print request,"more than 1 ip"
    print request.fields.status,ip
    jira.transition_issue(request, to_status_id)

def change_resource_status_to_abandon(ip):
    request_to_recycle_id=31
    requests=jira.search_issues("project = SEEVM AND VMIP ~ %s" %ip,maxResults=2)
    request=requests[0]
    resource_to_unassign_id=31
    resource_abandon_status_id=21
    print ip,request
    for link in request.fields.issuelinks: 
        if link.raw.has_key('inwardIssue'): 
            resource_id=link.raw['inwardIssue']['key']
        else:
            resource_id=link.outwardIssue.key
        resource=jira.issue(resource_id)
        print ip,request,resource
        jira.delete_issue_link(link.id)
        jira.transition_issue(resource,resource_abandon_status_id)
    jira.transition_issue(request,request_to_recycle_id)
    
def change_resource_status_to_TBassign(ip):
    request_to_recycle_id=31
    requests=jira.search_issues("project = SEEVM AND status = TBRecycled AND VMIP ~ %s" %ip,maxResults=2)
    request=requests[0]
    resource_to_unassign_id=31
    resource_abandon_status_id=21
    print ip,request
    for link in request.fields.issuelinks: 
        if link.raw.has_key('inwardIssue'): 
            resource_id=link.raw['inwardIssue']['key']
        else:
            resource_id=link.outwardIssue.key
        resource=jira.issue(resource_id)
        print ip,request,resource
        jira.delete_issue_link(link.id)
        jira.transition_issue(resource,resource_to_unassign_id)
    jira.transition_issue(request,request_to_recycle_id)

def reset_vm(ip):
    vm = VM(ip, 'letv', 'asdfas')
    vm.recyclePlaybook('/letv/ansible/ci_scripts/devops/rdvm/resetvm/resetvm.yml','/letv/leey/')
    
def clean_vm_zabbix_description(ip):
    hostname='vm-'+ip.replace('.','-')
    host=models.Hosts.objects.get(name=hostname)
    host.description=""
    host.save()
    print "clean zabbix description"

if __name__=='__main__':
    ips=get_vm_owner_according_ip('recycle_ip_list.txt')
    for ip in ips:
        #print ip
        change_request_status_to_TBrecycle(ip)

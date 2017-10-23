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
import ansible.runner
import ansible.inventory
import ansible.playbook
from ansible import callbacks
from ansible import utils
from reset_password import generate_random_password,set_random_passwd

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

    def uptime(self):
        Runner = ansible.runner.Runner(
            module_name='command',
            module_args='uptime',
            inventory = self.webInventory
        )
        self.Output = Runner.run()


    def recyclePlaybook(self,playbook,hostlist): #playbook,用来指定playbook的yaml文件, hostlist 指定hosts文件
        stats = callbacks.AggregateStats() #收集playbook执行期间的状态信息，最后会进行汇总
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY) #callbacks用来输出playbook执行的结果
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats,verbose=utils.VERBOSITY) #用来输出playbook执行期间的结果

        playbook=ansible.playbook.PlayBook(
            playbook=playbook,
            stats=stats,
            callbacks=playbook_cb,
            runner_callbacks=runner_cb,
            inventory = self.webInventory,
        )
        result=playbook.run()
        data = json.dumps(result,indent=4)
        print data


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
    request=requests[0]
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
    print ip
    request_to_recycle_id=31
    requests=jira.search_issues("project = SEEVM AND status = TBRecycled AND VMIP ~ %s" %ip,maxResults=2)
    request=requests[0]
    resource_to_unassign_id=31
    resource_abandon_status_id=21
    #print ip,request
    for link in request.fields.issuelinks: 
        if link.raw.has_key('inwardIssue'): 
            resource_id=link.raw['inwardIssue']['key']
        else:
            resource_id=link.outwardIssue.key
        resource=jira.issue(resource_id)
        print request,resource
        jira.delete_issue_link(link.id)
        jira.transition_issue(resource,resource_to_unassign_id)
    jira.transition_issue(request,request_to_recycle_id)

def reset_vm(ip):
    vm = VM(ip, 'letv', 'asdfas')
    vm.recyclePlaybook('/letv/scripts/ansible/resetvm/resetvm.yml','/letv/leey/')
    vm.recyclePlaybook('/letv/scripts/assign_vm/NFS_restore.yml','/letv/leey')
    
def clean_vm_zabbix_description(ip):
    hostname='vm-'+ip.replace('.','-')
    host=models.Hosts.objects.get(name=hostname)
    host.description=""
    host.save()
    host_inventory=models.HostInventory.objects.get(hostid=host.hostid)
    host_inventory.contact=''
    host_inventory.date_hw_install=''
    host_inventory.date_hw_expiry=''
    host_inventory.save()
    print "clean zabbix description"

if __name__=='__main__':
    requests=jira.search_issues("project = SEEVM AND status = TBRecycled")
    for request in requests:
        ips=request.fields.customfield_13414.split(',')
        change_resource_status_to_TBassign(ips[0])
        print ips
        for ip in ips:
            random_password=generate_random_password()
            set_random_passwd(ip,random_password)
            clean_vm_zabbix_description(ip)
            reset_vm(ip)
            

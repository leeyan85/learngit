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

jira=JIRA(basic_auth=("username","xxxxxxx@"), server="http://jira.letv.cn/")
    
    
if __name__=='__main__':
    No_assigned_request={}
    #requests=jira.search_issues("project = SEERESOURCE AND status = TBAssigned AND Configuration = \"V1 [CPU:8C Memory:16G HD:360G]\" AND \"SEERESOURCE Location\" = CNBJ",maxResults=800) #需要优化减小范围
    requests=jira.search_issues("project = SEERESOURCE AND status = Assigned AND Configuration = \"V1 [CPU:8C Memory:16G HD:360G]\" AND \"SEERESOURCE Location\" = CNBJ",maxResults=800) #需要优化减小范围
    #requests=jira.search_issues("project = SEERESOURCE AND Configuration = \"V1 [CPU:8C Memory:16G HD:360G]\" AND \"SEERESOURCE Location\" = CNBJ",maxResults=800) #需要优化减小范围
    for request in requests:
        print request.fields.customfield_13414
        if request.fields.customfield_13422 in No_assigned_request.keys():
            No_assigned_request[request.fields.customfield_13422].append(request.fields.customfield_13414)
        else: 
            No_assigned_request[request.fields.customfield_13422]=[]
            No_assigned_request[request.fields.customfield_13422].append(request.fields.customfield_13414)
    for key,value in No_assigned_request.items():
        if len(value)>0:
            print key,len(value),value

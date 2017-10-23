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
    
from jira_recycle_vm import get_vm_owner_according_ip
    
if __name__=='__main__':
    file_name=sys.argv[1]
    ips=get_vm_owner_according_ip(file_name)
    for ip in ips:
        requests=jira.search_issues("project = SEERESOURCE AND VMIP ~ %s"%ip) #需要优化减小范围
        for request in requests:
            #print request.fields.customfield_15600
            department=file_name.split('.')[0]
            print ip,department
            request.update(fields={"customfield_15600":department})

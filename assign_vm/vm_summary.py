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
import json
jira=JIRA(basic_auth=("username","xxxxxxx@"), server="http://jira.letv.cn/")



V1_config="V1 [CPU:8C Memory:16G HD:360G]"
V2_config="V2 [CPU:8C Memory:24G HD:560G]"

def change_data(config,city,type,region):
    assigned=jira.search_issues("project = SEERESOURCE AND status = Assigned AND Configuration = \"%s\" AND \"SEERESOURCE Location\" = %s"%(config,city), maxResults=800)
    noassigned=jira.search_issues("project = SEERESOURCE AND status = TBAssigned AND Configuration = \"%s\" AND \"SEERESOURCE Location\" = %s"%(config,city), maxResults=800)
    a=models.VmSummary.objects.get(vm_type=type,region=region)
    a.noassigned=len(noassigned)
    a.assigned=len(assigned)
    a.save()
    print a.region,a.noassigned,a.assigned


change_data(V1_config,"CNBJ","V1","CHN")
change_data(V2_config,"CNBJ","V2","CHN")
change_data(V2_config,"USLA","V2","USA")

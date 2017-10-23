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

issue_link_type="Relates"
to_status_id='11'

jira=JIRA(basic_auth=("username","xxxxxxx@"), server="http://jira.letv.cn/")

No_assigned_request=[]
print "begin"

#requests=jira.search_issues("project = SEEVM AND status = InUse ",maxResults=200) #需要优化减小范围    

requests=jira.search_issues("project = SEEVM AND status = InUse",maxResults=800)
print len(requests)

for request in requests:
    assigned_date=request.fields.created.split('T')[0]
    #print assigned_date
    #print request
    if request.fields.customfield_13414 is not None:
        hostname='vm-'+request.fields.customfield_13414.replace('.','-')
        print hostname
        try:
            owner=request.fields.reporter.emailAddress.lower()
            if owner=="":
                owner=request.fields.reporter.name+'@le.com'
            if owner=="svn@le.com":
                owner=request.fields.reporter.name.replace('@ff.com','').replace('_w','').lower()+'@ff.com'
            biz=request.fields.customfield_13425.child.value
            #print request,hostname,biz,owner
        except AttributeError, e:
            biz=""
        except NameError,e:
            biz=""
            
        try:
            host=models.Hosts.objects.get(name=hostname)
            host.description="owner:%s\nserviceline:%s" %(owner,biz)
            host.save()
            host_inventory=models.HostInventory.objects.get(hostid=host.hostid)
            host_inventory.contact=owner
            host_inventory.tag=biz
            host_inventory.date_hw_install=assigned_date
            host_inventory.save()            
            print request,host.name,biz,owner,host_inventory.date_hw_install
        except ObjectDoesNotExist:
            print "*****************host %s is not in zabbix"%hostname
    else:
        continue

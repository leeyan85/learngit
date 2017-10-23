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
from util import *
django.setup()

import xlsxwriter
from servermanage import models
from django.core.exceptions import ObjectDoesNotExist
import re

def get_items():
    assigned_hosts=[]
    with open('/tmp/2.txt') as f:
        hosts=f.readlines()
    for host in hosts:
        print host
        item=models.Items.objects.filter(key_field='check.vm.util.trapper',
                                  hostid__name=host.strip('\n'))
        assigned_hosts.append(item[0])
    print assigned_hosts
    return assigned_hosts,len(assigned_hosts)

def generate_30_days_list(today): #最近30天的日期，及linux timestamp
    first_day=today-datetime.timedelta(days=30)
    yesterday=today-datetime.timedelta(days=1)
    begintime='%d-%d-%d 00:00:00'%(first_day.year,first_day.month,first_day.day)
    begin_timestamp=time.mktime(time.strptime(begintime,"%Y-%m-%d %H:%M:%S"))
    endtime='%d-%d-%d 23:59:59'%(today.year,today.month,today.day)
    end_timestamp=time.mktime(time.strptime(endtime,"%Y-%m-%d %H:%M:%S"))
    month_day_list=[]
    i=30
    #print begintime,endtime
    while i > 0:
        day=today-datetime.timedelta(days=i)
        month_day_list.append('%d-%d-%d'%(day.year,day.month,day.day))
        i=i-1
    #print month_day_list,begin_timestamp,end_timestamp
    return month_day_list,int(begin_timestamp),int(end_timestamp)

 
 
if __name__=='__main__':
    today=datetime.datetime.now()
    items_info,total_hosts_count=get_items()
    month_day_list,begin_timestamp,end_timestamp=generate_30_days_list(today)
    month_data_summary=analyze_hisotry_data(items_info,begin_timestamp,end_timestamp,total_hosts_count)
    print json.dumps(month_data_summary,indent=4)

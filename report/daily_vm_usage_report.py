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
from django.core.exceptions import ObjectDoesNotExist
import util

def write_daily_usage_data():
    now=datetime.datetime.now() #-datetime.timedelta(days=1)

    date_list=[str(now.year),str(now.month),str(now.day)]

    today_date='-'.join(date_list)

    begin_time,end_time=util.generate_begin_end_time(today_date)

    print begin_time,end_time

    US_assigned_items,total_US_hosts,ZH_assigned_items,total_ZH_hosts=util.get_Region_items()
    
    data_summary=util.analyze_hisotry_data(US_assigned_items,begin_time,end_time,total_US_hosts)
    US_server_total=data_summary['ServerTotal']
    US_assigned_servercount=data_summary['AssignedServerCount']
    US_server_notinusecount=data_summary['ServerNoInUseCount']
    item=models.ScmDailyServerUsageSeparate(date=datetime.date(now.year,now.month,now.day),region='USA',servertotalcount=data_summary['ServerTotal'],assignedservercount=data_summary['AssignedServerCount'],servernotinusecount=data_summary['ServerNoInUseCount'],usedratio=data_summary['UsedRatio'])
    item.save()
    
    data_summary=util.analyze_hisotry_data(ZH_assigned_items,begin_time,end_time,total_ZH_hosts)
    CN_server_total=data_summary['ServerTotal']
    CN_assigned_servercount=data_summary['AssignedServerCount']
    CN_server_notinusecount=data_summary['ServerNoInUseCount']
    item=models.ScmDailyServerUsageSeparate(date=datetime.date(now.year,now.month,now.day),region='CHN',servertotalcount=data_summary['ServerTotal'],assignedservercount=data_summary['AssignedServerCount'],servernotinusecount=data_summary['ServerNoInUseCount'],usedratio=data_summary['UsedRatio'])
    item.save()
    
    ServerTotal=US_server_total+CN_server_total
    AssignedServerCount=US_assigned_servercount+CN_assigned_servercount
    ServerNoInUseCount=US_server_notinusecount+CN_server_notinusecount
    try:
        UsedTatio=float('%0.3f'%(float((AssignedServerCount-ServerNoInUseCount))/float(AssignedServerCount)))
    except ZeroDivisionError:
        UsedTatio=0
    item=models.ScmDailyServerUsageSeparate(date=datetime.date(now.year,now.month,now.day),region='All',servertotalcount=ServerTotal,assignedservercount=AssignedServerCount,servernotinusecount=ServerNoInUseCount,usedratio=UsedTatio)
    item.save()

if __name__=='__main__':
    write_daily_usage_data()

#!/usr/bin/python
#-*- coding:utf-8 -*-  
#from db_connect import db
import os,sys
import datetime
import time
pro_dir=os.getcwd()
sys.path.append(pro_dir)
sys.path.append('/letv/leey/SCMDB')
sys.path.append('/letv/scripts/report')
#当使用django作为第三方的脚本调用时必须添加
os.environ['DJANGO_SETTINGS_MODULE'] = 'SCMDB.settings'
import json
import django 
django.setup()

from servermanage import models
import util

def write_daily_usage_data():
    now=datetime.datetime.now()

    date_list=[str(now.year),str(now.month),str(now.day)]

    today_date='-'.join(date_list)

    begin_time,end_time=util.generate_begin_end_time(today_date)

    print begin_time,end_time

    items_info,total_hosts_count=util.get_items()

    data_summary=util.analyze_hisotry_data(items_info,begin_time,end_time,total_hosts_count)

    item=models.ScmDailyServerUsage(date=datetime.date(now.year,now.month,now.day),servertotalcount=data_summary['ServerTotal'],assignedservercount=data_summary['AssignedServerCount'],servernotinusecount=data_summary['ServerNoInUseCount'],usedratio=data_summary['UsedRatio'])
    item.save()


if __name__=='__main__':
    write_daily_usage_data()

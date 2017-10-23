#!/usr/bin/python
#coding: utf-8
import os,sys
import datetime
import time
pro_dir=os.getcwd()
sys.path.append(pro_dir)
sys.path.append('/letv/leey/SCMDB')
#当使用django作为第三方的脚本调用时必须添加
os.environ['DJANGO_SETTINGS_MODULE'] = 'SCMDB.settings'
import json
import django
from django.core.exceptions import ObjectDoesNotExist
django.setup()

import xlsxwriter
from servermanage import models


with file(sys.argv[1],'r') as f:
    info=f.readlines()
    
for line in info:
    a=line.split(',')
    try:
        ip='vm-' + a[3].replace('.','-')
        owner=a[4].split('<')[1].split('>')[0]
        biz=a[5].strip('\n')
    except IndexError:
        owner=''
        biz=''
        print ip+' info is not enough'
    try:
        host=models.Hosts.objects.get(name=ip)
    except ObjectDoesNotExist:
        continue
    else:
        if len(owner)<>0:
            host.description="owner:%s\nserviceline:%s" %(owner,biz)
            host.save()
        else:
            host.description=''
            host.save()

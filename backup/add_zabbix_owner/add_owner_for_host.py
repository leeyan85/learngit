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

from servermanage import models

hosts=models.Hosts.objects.filter(name__startswith='CP')

owner='scm-bp@le.com'
serviceline='compile'

for line in hosts:
    line.description='owner:%s\nserviceline:%s'%(owner,serviceline)
    line.save()

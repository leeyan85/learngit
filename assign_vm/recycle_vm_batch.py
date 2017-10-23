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
sys.path.append('/letv/scripts/SCMDB')
sys.path.append('/letv/scripts/mount_space')
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

from jira_recycle_vm import generate_random_password,reset_vm,clean_vm_zabbix_description,set_random_passwd

if __name__=='__main__':
    ip=sys.argv[1]
    print ip
    random_password=generate_random_password()
    clean_vm_zabbix_description(ip)
    set_random_passwd(ip,random_password)
    print "ehllo"
    reset_vm(ip)

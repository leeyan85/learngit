#!/usr/bin/python
from jira.client import JIRA
import json
jira=JIRA(basic_auth=("yangaofeng","ygf.1217"), server="http://jira.letv.cn/")
from zabbix_util import modify_zabbix_info_according_ip


if __name__=='__main__':
    resources=jira.search_issues("project = SEERESOURCE", maxResults=800)
    for resource in resources:
        if resource.fields.customfield_15600 is not None:
            if resource.fields.customfield_15600=='LeEco':
                 tag='US'
            elif resource.fields.customfield_15600=='FF':
                 tag='FF'
            else:
                 tag=resource.fields.customfield_15600

            pool=resource.fields.customfield_15600
            ip=resource.fields.customfield_13414
            modify_zabbix_info_according_ip(ip,pool)
        else:
            print resource.fields.customfield_13414

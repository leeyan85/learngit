#!/usr/bin/python

from jira.client import JIRA
jira=JIRA(basic_auth=("username","xxxxxxx@"), server="http://jira.letv.cn/")

issue_link_type="Relates"
InUse_status_id='11'
Unassign_status_id='41'

a='''"10.75.30.30":"huanghonglin",
"10.75.30.62": "cangpeng",
"10.75.30.43": "cangpeng",
"10.75.30.61": "cangpeng",
"10.75.30.56": "cangpeng",
"10.75.30.51": "cangpeng",
"10.75.30.58": "cangpeng",
"10.75.30.36":"lijin5",
"10.75.30.38":"longjinfeng",
"10.75.30.40":"yinjinpeng",
"10.75.30.42":"wangxinfeng",
"10.75.30.45":"longli",
"10.75.30.47":"xiezhiming1",
"10.75.30.49":"wangyin3",
"10.75.30.50":"wangjunxian",
"10.75.30.34":"yanyajie",
"10.75.30.33":"zhangguoliang",
"10.75.30.44":"cuiyongqiang",
"10.75.30.32":"wangxuyu",
"10.75.30.41":"zhangmingyuan",
'''
mapping={
        "10.75.30.29":"yangaofeng",
        "10.75.30.67":"mufeng",
        "10.75.30.69":"liukang",
        "10.75.30.60":"zhangkui",
         }


def init_resource_dict(reporter,ip):
    issue_dict = {
        "project": {
            "id": "14207"
        },
        "reporter": {
            "name": "%s" %reporter,
        },
        "customfield_13501": "18600010001",
        "issuetype": {
            "id": "11101"
        },
        "customfield_13417": {
            "id": "18001"
        },
        "customfield_13425": {
            "self": "http://jira.letv.cn/rest/api/2/customFieldOption/13826",
            "id": "13826",
            "value": "CN",
            "child": {
                "self": "http://jira.letv.cn/rest/api/2/customFieldOption/17758",
                "id": "17758",
                "value": "TV"
            }
        },
        "summary": "%s apply vm"%reporter,
        "customfield_13427": "compile",
        "customfield_13426": {
            "name": "leitao"
        },
        "customfield_13414": '%s' % ip
    }
    return issue_dict



if __name__=="__main__":
    for ip,reporter in mapping.items():    
        issue_dict=init_resource_dict(ip, reporter)
        request = jira.create_issue(fields=issue_dict)
        resources = jira.search_issues("project = SEERESOURCE AND issuetype = RDVM AND status = TBAssigned AND VMIP ~ %s"%ip)
        resource=resources[0]
        print request,resource
        jira.transition_issue(resource, InUse_status_id)
        jira.transition_issue(request, InUse_status_id)
        jira.create_issue_link(issue_link_type, resource, request, comment=None)

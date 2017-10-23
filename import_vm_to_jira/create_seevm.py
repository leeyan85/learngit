#!/usr/bin/python

from jira.client import JIRA
jira=JIRA(basic_auth=("username","xxxxxxx@"), server="http://jira.letv.cn/")


users=["lihuaqiang",]


def init_resource_dict(reporter):
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
    }
    return issue_dict



if __name__=="__main__":
    for reporter in users:
        issue_dict=init_resource_dict(reporter)
        request = jira.create_issue(fields=issue_dict)

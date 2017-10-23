#!/usr/bin/python
from jira.client import JIRA
import json
jira=JIRA(basic_auth=("yangaofeng","ygf.1218"), server="http://jira.letv.cn/")

#mapping={u'10.75.30.76': '10.75.30.119', u'10.75.30.77': '10.75.30.118', u'10.75.30.75': '10.75.30.123', u'10.75.30.73': '10.75.30.122', u'10.75.30.70': '10.75.30.129', u'10.75.30.71': '10.75.30.118', u'10.75.30.54': '10.75.30.130', u'10.75.30.55': '10.75.30.115', u'10.75.30.39': '10.75.30.121', u'10.75.30.59': '10.75.30.115', u'10.75.30.91': '10.75.30.120', u'10.75.30.63': '10.75.30.130', u'10.75.30.48': '10.75.30.117', u'10.75.30.68': '10.75.30.123', u'10.75.30.89': '10.75.30.121', u'10.75.30.88': '10.75.30.122', u'10.75.30.83': '10.75.30.124', u'10.75.30.82': '10.75.30.128', u'10.75.30.81': '10.75.30.129', u'10.75.30.80': '10.75.30.120', u'10.75.30.87': '10.75.30.116', u'10.75.30.85': '10.75.30.119'}

mapping={
    "10.75.30.76": "10.75.30.119", 
    "10.75.30.77": "10.75.30.118", 
    "10.75.30.63": "10.75.30.130", 
    "10.75.30.75": "10.75.30.123", 
    "10.75.30.59": "10.75.30.115", 
    "10.75.30.70": "10.75.30.129", 
    "10.75.30.71": "10.75.30.118", 
    "10.75.30.54": "10.75.30.130", 
    "10.75.30.82": "10.75.30.128", 
    "10.75.30.81": "10.75.30.129", 
    "10.75.30.48": "10.75.30.117", 
    "10.75.30.89": "10.75.30.121", 
    "10.75.30.85": "10.75.30.119", 
    "10.75.30.83": "10.75.30.124", 
    "10.75.30.88": "10.75.30.122", 
    "10.75.30.80": "10.75.30.120", 
    "10.75.30.55": "10.75.30.115", 
    "10.75.30.68": "10.75.30.123", 
    "10.75.30.39": "10.75.30.121", 
    "10.75.30.91": "10.75.30.120", 
    "10.75.30.73": "10.75.30.122"
}

DepartmentPool="TV"

def init_issue_dict(vmip,hostip):
    resource_dict={
        "project": {
            "id": "14206",
            "name": "SEERESOURCE"
        },
        "issuetype": {
            "name": "RDVM",
            "id": "11100",
        },
        "summary": "%s_V3 [CPU:4C Memory:16G HD:800G]"%vmip,
        "customfield_13414": "%s"%vmip,
        "customfield_13415": "%s"%vmip,
        "customfield_13417": {
            "self": "http://jira.letv.cn/rest/api/2/customFieldOption/18001", 
            "id": "18001", 
            "value": "V3 [CPU:8C Memory:16G HD:800G]"
        },
        "customfield_13616": {
            "id": "18000",
            "value": "BJDT"
        },

        "customfield_13421": {
            "id": "13825",
            "value": "KVM"
        },
        "customfield_13422": "%s"%hostip,
        "customfield_13416": {
            "id": "13815",
            "value": "Ubuntu_14.04",
        },
        "customfield_15600": "%s"%DepartmentPool,
    }
    return resource_dict



if __name__=='__main__':
    for vmip,hostip in mapping.items():
        resource_dict=init_issue_dict(vmip,hostip)
        print json.dumps(resource_dict,indent=4)
        request = jira.create_issue(fields=resource_dict)
        #search_sql="project = SEERESOURCE AND \"Department Pool\" ~ Platform AND \"SEERESOURCE Location\" = BJDT AND VMIP ~ %s" %vmip
        #resource = jira.search_issues(search_sql)
        #print resource
        #resource[0].delete()

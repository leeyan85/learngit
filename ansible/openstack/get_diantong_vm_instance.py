#!/usr/bin/env python 
def get_vm_host_mapping():
    host_ip_mapping={}
    import json 
    with open('diantong_openstack.json','r') as f:
        instance_dict=json.load(f)
    
    with open('host_ip_mapping','r') as f:
        for line in f:
            temp=line.split(' ')
            hostname=temp[1].strip('\n')
            ip=temp[0]
            host_ip_mapping[hostname]=ip
    
    with open ('imported.txt','r') as f:
        imported_vms=[]
        for line in f:
            temp=line.strip('\n')
            imported_vms.append(temp)
    
    a={}
    for key,value in instance_dict['_meta'].items():
        for key_depth2,value_depth2 in value.items():
            try:
                if value_depth2['ansible_ssh_host'] not in imported_vms and value_depth2['ansible_ssh_host']!="10.75.30.72":
                    a[value_depth2['ansible_ssh_host']]=host_ip_mapping[value_depth2['openstack']['OS-EXT-SRV-ATTR:host']]
                
            except  KeyError:
                continue
    print json.dumps(a,indent=4)

if __name__=='__main__':
    get_vm_host_mapping()

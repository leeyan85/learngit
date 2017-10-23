#!/usr/bin/python
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
from util import generate_begin_end_time
from mail import send_mail

def get_cpu_usage_items():
    items=models.Items.objects.filter(key_field='system.cpu.load[percpu,avg15]',hostid__name__startswith='vm-',hostid__status=0)
    return items

def get_cpu_items():
    items=models.Items.objects.filter(key_field='system.hw.cpu[all,model]',hostid__name__startswith='vm-',hostid__status=0)
    return items

def get_memory_items():
    items=models.Items.objects.filter(key_field='vm.memory.size[total]',hostid__name__startswith='vm-',hostid__status=0)
    print items
    return items

def get_disk_items():
    assigned_hosts=[]
    items=[]
    used_items=models.Items.objects.filter(key_field__contains='used',
                                           name__contains='disk',
                                  hostid__name__startswith='vm-',hostid__status=0).exclude(key_field__contains='#')
                                  
                                  
    total_items=models.Items.objects.filter(key_field__contains='total',
                                            name__contains='disk',
                                  hostid__name__startswith='vm-',hostid__status=0).exclude(key_field__contains='#')
    
    
    
    item_info=[]
    for total_item in total_items:
        hostname=total_item.hostid.name
        interface=models.Interface.objects.filter(hostid=total_item.hostid.hostid)[0]
        total_itemid=total_item.itemid
        mount_point=total_item.key_field.split('[')[1].split(',')[0]
        for used_item in used_items:
            if used_item.key_field.split('[')[1].split(',')[0]==mount_point and used_item.hostid.name==hostname:
                used_itemid=used_item.itemid        
        item_info.append((hostname,interface.ip,mount_point,total_itemid,used_itemid)) #
    return item_info



def analyze_cpu_usage_history_data(items,begintimestamp,endtimestamp,threashold):
    no_usage=0
    low_usage=0
    high_usage=0
    very_high_usage=0
    server_CPU_usage_dict={}
    high_useage_servers=[]
    for item in items:
        historys=models.History.objects.filter( itemid=item.itemid,
                                                clock__gte=begintimestamp,
                                                clock__lte=endtimestamp,
                                                value__gte=threashold
                                                )
        time_list_high_usage=[]  
        hostid=item.hostid.hostid
        interface=models.Interface.objects.filter(hostid=hostid)[0] 
        if len(item.hostid.description)==0:
            owner=''
        else:
            owner=item.hostid.description.split('\n')[0].split(':')[1].strip('\r')      
        if len(historys)==0: #cpu_load_gt_20的次数等于0
            no_usage=no_usage+1
        elif len(historys)>0 and len(historys) <=300:
            low_usage=low_usage+1
            print owner,interface.ip
        elif len(historys)>300 and len(historys)<=500:  #cpu_load_gt_20的次数大于300
            high_usage=high_usage+1
            high_useage_servers.append(owner,interface.ip)
        elif len(historys)>500:
            very_high_usage=very_high_usage+1
            high_useage_servers.append(owner,interface.ip)
            
        server_CPU_usage_dict[item.hostid.name]=[owner,interface.ip,len(historys)]
    server_CPU_usage_summary={'high_usage_server_count':very_high_usage,'nearly_no_usage_server_count':no_usage,'normal_usage_server_count':high_usage,'low_usage_server_count':low_usage}
    return server_CPU_usage_dict,server_CPU_usage_summary,high_useage_servers
 

def analyze_disk_history_data(items):
    info={}      
    for item in items:
        hostname=item[0]
        ipaddress=item[1]
        mount_point=item[2]
        total_space_itemid=item[3]
        used_space_itemid=item[4]
        try:
            total_diskspace=list(models.HistoryUint.objects.filter(itemid=total_space_itemid))[-1].value
            used_diskspace=list(models.HistoryUint.objects.filter(itemid=used_space_itemid))[-1].value
        except IndexError:
            total_diskspace=0
            used_diskspace=0
        #print info
        if total_diskspace<>0 and used_diskspace<>0:
            if info.has_key(hostname):
                if info[hostname]['total_diskspace']<total_diskspace:
                    info[hostname]={'mount_point':mount_point,'total_diskspace':total_diskspace,
                                   'used_diskspace':used_diskspace,
                                   'used_ratio':float('%0.3f'%(float(used_diskspace)/float(total_diskspace)))
                                }
                else:
                    continue
            else:
                info[hostname]={'mount_point':mount_point,'total_diskspace':total_diskspace,
                                   'used_diskspace':used_diskspace,
                                   'used_ratio':float('%0.3f'%(float(used_diskspace)/float(total_diskspace)))
                                }
    for key in info.keys():
        info[key]['total_diskspace']=str(int(float(info[key]['total_diskspace'])/1024/1024/1024))+'G'
        info[key]['used_diskspace']=str(int(float(info[key]['used_diskspace'])/1024/1024/1024))+'G'
    print info
    return info


def analyze_memory_history_data(items): 
    memory_info_summary={}
    for item in items:
        memory_history=list(models.HistoryUint.objects.filter(itemid=item.itemid))
        if len(memory_history)<>0:
            human_memory=int(float(memory_history[-1].value)/1024/1024/1024)
            memory_info_summary[item.hostid.name]=str(human_memory)+'G'
    return memory_info_summary
            

def analyze_CPU_data(items):
    cpu_info_summary={}
    for item in items:
        CPU_history= list(models.HistoryText.objects.filter(itemid=item.itemid))
        if len(CPU_history)<>0:
            cpu_count=len(CPU_history[-1].value.split('\n'))
            cpu_info_summary[item.hostid.name]=cpu_count
    return cpu_info_summary


if __name__=='__main__':
    now=datetime.datetime.now()-datetime.timedelta(days=1)
    date='-'.join([str(now.year),str(now.month),str(now.day)])
    #CPU 使用情况分析
    begintimestamp,endtimestamp=generate_begin_end_time(date)
    print date,begintimestamp,endtimestamp
    cpu_usage_items=get_cpu_usage_items()
    server_CPU_usage_dict,server_CPU_usage_summary,high_useage_servers=analyze_cpu_usage_history_data(cpu_usage_items, begintimestamp, endtimestamp,0.2)

    print server_CPU_usage_dict
    print server_CPU_usage_summary
    print high_useage_servers

    '''#memory 信息汇总
    memory_items=get_memory_items()
    print memory_items
    memory_info_summary=analyze_memory_history_data(memory_items)
    #CPU信息汇总
    #cpu_items=get_cpu_items()
    #cpu_info_summary=analyze_CPU_data(cpu_items)
    #print server_CPU_usage_dict '''

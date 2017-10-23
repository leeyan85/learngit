#!/usr/bin/python
#-*- coding:utf-8 -*-  
from util import *
from mail import send_mail
import re

def get_items(today): #用于统计所有分配天数大于30天的VM
    assigned_hosts=[]
    items=models.Items.objects.filter(key_field='check.vm.util.trapper',
                                  hostid__name__startswith='vm')
    total_hosts=len(items)
    now=today
    today_date=datetime.date(now.year,now.month,now.day)
    for item in items:
        if len(item.hostid.description)!=0:
            host_inventory=models.HostInventory.objects.get(hostid=item.hostid.hostid)
            assign_date_list=host_inventory.date_hw_install.split('-')
            #print item.hostid.host,assign_date_list
            assign_date=datetime.date(int(assign_date_list[0]),int(assign_date_list[1]),int(assign_date_list[2]))
#            print item.hostid.host,host_inventory.date_hw_install,today_date,(today_date-assign_date).days
            if (today_date-assign_date).days > 30:
                assigned_hosts.append(item)
    return assigned_hosts,total_hosts


def generate_30_days_list(today):
    first_day=today-datetime.timedelta(days=60)
    yesterday=today-datetime.timedelta(days=1)
    begintime='%d-%d-%d 00:00:00'%(first_day.year,first_day.month,first_day.day)
    begin_timestamp=time.mktime(time.strptime(begintime,"%Y-%m-%d %H:%M:%S"))
    endtime='%d-%d-%d 23:59:59'%(today.year,today.month,today.day)
    end_timestamp=time.mktime(time.strptime(endtime,"%Y-%m-%d %H:%M:%S"))
    month_day_list=[]
    i=30
    #print begintime,endtime
    while i > 0:
        day=today-datetime.timedelta(days=i)
        month_day_list.append('%d-%d-%d'%(day.year,day.month,day.day))
        i=i-1
    #print month_day_list,begin_timestamp,end_timestamp
    return month_day_list,int(begin_timestamp),int(end_timestamp)

if __name__=='__main__':
    today=datetime.datetime.now()
    items_info,total_hosts_count=get_items(today)
    month_day_list,begin_timestamp,end_timestamp=generate_30_days_list(today)
    each_day_summary=each_day_summary(month_day_list,items_info,'All')
    #print each_day_summary
    month_data_summary=analyze_hisotry_data(items_info,begin_timestamp,end_timestamp,total_hosts_count)
    month_data_summary['begin_date']=month_day_list[0]
    month_data_summary['end_date']=month_day_list[-1]
    print len(month_data_summary['ServerInUseHigh']), month_data_summary['ServerInUseHigh']
    more_than_one_vm_user={}
    keep_server=['vm-10-142-128-107']
    for server_info in  month_data_summary['ServerNoInUseList']:
        hostname=server_info[0]
        if re.search('vm-10-78',server_info[0]):
            continue
        if server_info[0] in keep_server:
            continue
        vm=server_info[0].replace('vm-','').replace('-','.')
        user=server_info[1]
        subject="your vm %s is not used for 30 days, we will recycle it"%vm
        keep_info='http://10.142.128.97:9090/devself/keepserver/%s/'%vm
        content="your vm %s is not used for 30 days, we will recycle it, if you need keep it, please click below URL, we will send such email 3 times, if you do not reply, your vm will be recycled\n %s"%(vm,keep_info)
        
        #send_mail(subject,content=content,sender='SEE@le.com',receiver=[user],cc_receiver=["yangaofeng@le.com"])
        
        host_inventory=models.HostInventory.objects.get(hostid__name=hostname)
        print type(host_inventory.date_hw_expiry)
        
        if host_inventory.date_hw_expiry== '':
            host_inventory.date_hw_expiry=1
            host_inventory.save()
            send_mail(subject,content=content,sender='SEE@le.com',receiver=['yangaofeng@le.com'],cc_receiver=["yangaofeng@le.com"])
        elif int(host_inventory.date_hw_expiry)<2:
            host_inventory.date_hw_expiry=int(host_inventory.date_hw_expiry)+1
            host_inventory.save()
            send_mail(subject,content=content,sender='SEE@le.com',receiver=['yangaofeng@le.com'],cc_receiver=["yangaofeng@le.com"])
        else:
            print 'recycle your VMs'
            
    report_file_name='monthly_server_usage_report.xlsx'
    write_monthly_report(report_file_name,each_day_summary,month_data_summary,total_hosts_count)
    send_mail("monthly VM server usage report",attachment=report_file_name,sender='SEE@le.com',receiver=['yangaofeng@le.com'])
    #send_mail("monthly VM server usage report",attachment=report_file_name,sender='SEE@le.com',receiver=['SEE@le.com'])

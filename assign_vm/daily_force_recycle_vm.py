#!/usr/bin/python
#-*- coding:utf-8 -*-
import sys
sys.path.append('E:\workspace\SCMDB')
sys.path.append('/letv/scripts/report')
reload(sys)
sys.setdefaultencoding('utf-8')
from util import *
from mail import send_mail
from change_jira_to_TBrecycle import change_request_status_to_TBrecycle 
import re
def send_alert_info(vm,url):
    #china_vm_prefix='10.142'
    apply_vm_instruction=u"http://wiki.letv.cn/display/LETVINNO/LeEco+Research+and+Developing+Virtual+Environment+Service++Application"
    content='''亲，你申请的高性能虚机%s已经30天没有用了，我们要收回了哦~~
- 无需操作，提醒3次后自动收回, 也可以自己申请回收，http://wiki.letv.cn/display/LETVINNO/How+to+apply+recycle+VM
- 如需保留，请在这里登录确认%s
- 如果今后需要使用虚机，可以在这里重新申请哈：申请虚机 %s
谢谢大伙儿配合~~

Your high performance VM %s has not been used for 30 days, we regret to inform you that we have to recycle and reassign it to others who need it urgently, according to the VM general usage agreement.
Your VM will be recycled directly if we don't receive any action from you after 3 email reminder like such, you can apply for recycle.http://wiki.letv.cn/display/LETVINNO/How+to+apply+recycle+VM
If you want to keep on taking your VM, please click URL %s to retain it.
Please re-apply one as below when you are in need. Thanks for your cooperation.
%s

Best Regards,
LeEco SCM Engineering Efficiency - We stand for maximum engineering efficiency.'''%(vm,url,apply_vm_instruction,vm,url,apply_vm_instruction)

        
    return content

def send_reminder_info(vm,url):
    print vm, url
    content=u'''亲,最近发现你虚机%s的使用率特别高，根据后台大数据分析，我们严重怀疑你可能迫切需要一台更高配置的虚拟机, 性能提升50%%，点击这里申请V2虚机%s
此提醒邮件会发送3次，如果已经申请，请忽略
欢迎给我们发送任何虚机相关的建议和意见: SEE@le.com

Your current VM in using %s is V1 (HW spec: [CPU:8C Memory:16G HD:360GB]).Based on your daily usage record, we believe you need a higher performance VM to get work done more efficiently. 
Here are the steps to apply a higher performance VM V2 (HW spec: [CPU:8C Memory:24G HD:560GB]) %s
We will reminder you 3 times until you apply a V2, and please ignore this email if you have already have one.
Please feel free to contact SEE@le.com if you have any comments.

Best Regards,
LeEco SCM Engineering Efficiency - We stand for maximum engineering efficiency.
'''%(vm,url,vm,url)
        
    return content

def get_items(today): #用于统计所有分配天数大于30天的VM
    assigned_hosts=[]
    items=[]
    all_items=models.Items.objects.filter(key_field='check.vm.util.trapper',
                                  hostid__name__startswith='vm')
    special_group=models.Groups.objects.get(groupid=14)
    total_hosts=len(all_items)
    
    for item in all_items:
        hostid=item.hostid
        special=models.HostsGroups.objects.filter(hostid=hostid,groupid=special_group)
        if len(special)==0:
            items.append(item)
        else:
            continue
    now=today
    today_date=datetime.date(now.year,now.month,now.day)
    print total_hosts,len(items)

    for item in items:
        if len(item.hostid.description)!=0:
            host_inventory=models.HostInventory.objects.get(hostid=item.hostid.hostid)
            print host_inventory.hostid.name
            assign_date_list=host_inventory.date_hw_install.split('-')
            print assign_date_list
            assign_date=datetime.date(int(assign_date_list[0]),int(assign_date_list[1]),int(assign_date_list[2]))
            if (today_date-assign_date).days > 30:
                assigned_hosts.append(item)
    return assigned_hosts,total_hosts


def generate_30_days_list(today): #最近30天的日期，及linux timestamp
    first_day=today-datetime.timedelta(days=30)
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


def send_alert_to_no_use_owner(month_data_summary): #通知30天没有使用的机器的owner
    for server_info in  month_data_summary['ServerNoInUseList']:
        hostname=server_info[0]
        if re.search('vm-10-78',server_info[0]):
            continue
        if server_info[0] in keep_server:
            continue
        vm=server_info[0].replace('vm-','').replace('-','.')
        user=server_info[1]
        keep_info='http://ci.le.com/webapp/devself/keepserver/%s/'%vm
        content=send_alert_info(vm,keep_info)
        
        host_inventory=models.HostInventory.objects.get(hostid__name=hostname)
        
        if host_inventory.date_hw_expiry== '':
            host_inventory.date_hw_expiry=1
            host_inventory.save()
            subject="%s alert:  [VM Recycle] Your vm %s has not been used for 30 days"%(mapping[str(host_inventory.date_hw_expiry)],vm)
            send_mail(subject,content=content,sender='cm_monitor@le.com',receiver=[user],cc_receiver=cc_receiver)
            print subject,content
        elif int(host_inventory.date_hw_expiry)<3:
            host_inventory.date_hw_expiry=int(host_inventory.date_hw_expiry)+1
            host_inventory.save()
            subject="%s alert:  [VM Recycle] Your vm %s has not been used for 30 days"%(mapping[str(host_inventory.date_hw_expiry)],vm)
            send_mail(subject,content=content,sender='cm_monitor@le.com',receiver=[user],cc_receiver=cc_receiver)
            print subject,content
        else: #修改30天没有使用而且3次告警都没有回应的用户的JIRA状态
            change_request_status_to_TBrecycle(vm) #修改jira状态为TBrecycle而且
            print vm

def change_status_server_in_use(month_data_summary): #当虚拟机正在使用时,修改zabbix中的信息的保留日期为空
    for hostname in  month_data_summary['ServerInUse']:
        host_inventory=models.HostInventory.objects.get(hostid__name=hostname)
        host_inventory.date_hw_expiry=''
        host_inventory.save()
       

def send_suggestion_to_high_usage_user(month_data_summary): #给V1版本的虚拟机用户发送提醒升级到V2
    V2_prefixs=['10.212','10.142.132','10.142.131','10.78.134']
    apply_vm_instruction=u"http://wiki.letv.cn/display/LETVINNO/LeEco+Research+and+Developing+Virtual+Environment+Service++Application"
    for server_info in  month_data_summary['ServerInUseHigh']:
         hostname=server_info[0]
         user=server_info[1]
         hosts=models.HostInventory.objects.filter(contact=user)
         vm=hostname.replace('vm-','').replace('-','.')
         tmp=[]
         if len(hosts)>=2: #用户有两台虚拟机机
             for host in hosts:
                 tmp.append(host.hostid.name)
                 hostInventory=models.HostInventory.objects.get(hostid__name=host.hostid.name)
                 hostInventory.date_hw_decomm=""
                 hostInventory.save()
                 
         else: #用户只有1台虚拟机
             host=models.Hosts.objects.get(name=hostname)
             item=models.Items.objects.get(key_field="vfs.fs.size[/letv,pfree]",hostid=host)
             history_items=models.History.objects.filter(itemid=item.itemid,clock__gte=begin_timestamp,clock__lte=end_timestamp).order_by('-clock')[0]
             if history_items.value<25: #磁盘可用率小于25%
                 V2_yes=0
                 for v2_prefix in V2_prefixs:
                     if re.search(v2_prefix,vm):
                         V2_yes=1
                         break
                 if V2_yes==1:
                     continue

                 else: #虚拟机为V1版本
                     hostInventory=models.HostInventory.objects.get(hostid__name=hostname)
                     if hostInventory.date_hw_decomm=="":
                         hostInventory.date_hw_decomm=1
                         hostInventory.save()
                         subject=u"%s kind reminder: [High Performance VM] You are strongly recommended to apply one "%(mapping[str(hostInventory.date_hw_decomm)])
                         content=send_reminder_info(vm,apply_vm_instruction)
                         send_mail(subject,content=content,sender='cm_monitor@le.com',receiver=[user],cc_receiver=cc_receiver)
                     elif int(hostInventory.date_hw_decomm)<3:
                         hostInventory.date_hw_decomm=int(hostInventory.date_hw_decomm)+1
                         hostInventory.save()
                         subject=u"%s kind reminder: [High Performance VM] You are strongly recommended to apply one "%(mapping[str(hostInventory.date_hw_decomm)])
                         content=send_reminder_info(vm,apply_vm_instruction)
                         send_mail(subject,content=content,sender='cm_monitor@le.com',receiver=[user],cc_receiver=cc_receiver)
                     else:
                         continue


if __name__=='__main__':
    today=datetime.datetime.now()
    items_info,total_hosts_count=get_items(today)
    print items_info
    month_day_list,begin_timestamp,end_timestamp=generate_30_days_list(today)
    each_day_summary=each_day_summary(month_day_list,items_info,'All')
    #print each_day_summary
    month_data_summary=analyze_hisotry_data(items_info,begin_timestamp,end_timestamp,total_hosts_count)
    month_data_summary['begin_date']=month_day_list[0]
    month_data_summary['end_date']=month_day_list[-1]
    print len(month_data_summary['ServerInUseHigh']), month_data_summary['ServerInUseHigh']
    keep_server=['vm-10-142-128-107']
    mapping={'1':'1st','2':'2nd','3':'3rd'}
    cc_receiver=["devops@le.com"]
    send_suggestion_to_high_usage_user(month_data_summary)
    change_status_server_in_use(month_data_summary)
    send_alert_to_no_use_owner(month_data_summary)

    report_file_name='monthly_server_usage_report.xlsx'
    write_monthly_report(report_file_name,each_day_summary,month_data_summary,total_hosts_count)
    send_mail("monthly VM server usage report",attachment=report_file_name,sender='SEE@le.com',receiver=['yangaofeng@le.com'])
    #send_mail("monthly VM server usage report",attachment=report_file_name,sender='SEE@le.com',receiver=['SEE@le.com'])

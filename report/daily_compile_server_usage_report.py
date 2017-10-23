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
    items=models.Items.objects.filter(key_field='system.cpu.load[percpu,avg15]',hostid__name__startswith='pcnbj-cp',hostid__status=0)
    return items

def get_cpu_items():
    items=models.Items.objects.filter(key_field='system.hw.cpu[all,model]',hostid__name__startswith='pcnbj-cp',hostid__status=0)
    return items

def get_memory_items():
    items=models.Items.objects.filter(key_field='vm.memory.size[total]',hostid__name__startswith='pcnbj-cp',hostid__status=0)
    return items

def get_disk_items():
    assigned_hosts=[]
    items=[]
    used_items=models.Items.objects.filter(key_field__contains='used',
                                           name__contains='disk',
                                  hostid__name__startswith='pcnbj-cp',hostid__status=0).exclude(key_field__contains='#')
                                  
                                  
    total_items=models.Items.objects.filter(key_field__contains='total',
                                            name__contains='disk',
                                  hostid__name__startswith='pcnbj-cp',hostid__status=0).exclude(key_field__contains='#')
    
    
    
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
        elif len(historys)>300 and len(historys)<=500:  #cpu_load_gt_20的次数大于300
            high_usage=high_usage+1
        elif len(historys)>500:
            very_high_usage=very_high_usage+1
        
        server_CPU_usage_dict[item.hostid.name]=[owner,interface.ip,len(historys)]
    server_CPU_usage_summary={'high_usage_server_count':very_high_usage,'nearly_no_usage_server_count':no_usage,'normal_usage_server_count':high_usage,'low_usage_server_count':low_usage}
    return server_CPU_usage_dict,server_CPU_usage_summary
 

def analyze_disk_history_data(items):
    info={}      
    for item in items:
        print item
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

def write_daily_report(filename,server_CPU_usage_dict,server_CPU_usage_summary):
    write_data=[]   
    workbook = xlsxwriter.Workbook(filename)
    #写title format
    format_title=workbook.add_format()    #定义format_title格式对象
    format_title.set_border(1)   #定义format_title对象单元格边框加粗(1像素)的格式
    format_title.set_bg_color('#cccccc')   #定义format_title对象单元格背景颜色为'#cccccc'的格式    
    format_title.set_align('center')    #定义format_title对象单元格居中对齐的格式
    format_title.set_bold()    #定义format_title对象单元格内容加粗的格式    
    format_title.set_text_justlast()
    
    #定义数据format
    format=workbook.add_format()    #定义format格式对象
    format.set_border(1)    #定义format对象单元格边框加粗(1像素)的格式
    format.set_text_justlast()
    
    sheetname='compile_server_usage'
    daily_worksheet = workbook.add_worksheet(sheetname)
    daily_worksheet.set_column('A:J',19)
    title=['compile server','owner','ip address','cpu_load_gt_50_count','total_memory','total_CPU_cores','largest_disk_mount_point','total_diskspace','used_diskspace','disk_used_ratio']
    daily_worksheet.write_row('A1',title,format_title)
    title=['High_usage_server_count','Low_usage_server_count','Nearly_no_usage_server_count','normal_usage_server_count']  
    daily_worksheet.write_row('G72',title,format_title)
    begin_line=2
    for key in server_CPU_usage_dict.keys():
        print key
        data=server_CPU_usage_dict[key]
        data.insert(0,key)
        daily_worksheet.write_row('A%d'%begin_line,data,format)
        begin_line=begin_line+1
    

    daily_worksheet.write('G73',server_CPU_usage_summary['high_usage_server_count'])
    daily_worksheet.write('H73',server_CPU_usage_summary['low_usage_server_count'])
    daily_worksheet.write('I73',server_CPU_usage_summary['nearly_no_usage_server_count'])
    daily_worksheet.write('J73',server_CPU_usage_summary['normal_usage_server_count'])
    daily_worksheet.write('C73',u'cpu_load_gt_50_count表示24小时内，每5分钟cpu load大于20%的次数')
    daily_worksheet.write('C74',u'当500=>cpu_load_gt_50_count>=300时，表示CPU使用率正常')
    daily_worksheet.write('C75',u'当cpu_load_gt_50_count<300时，表示CPU使用率较低')
    daily_worksheet.write('C76',u'当cpu_load_gt_50_count=0时，表示CPU使用率极低')
    daily_worksheet.write('C77',u'当cpu_load_gt_50_count>500时，表示CPU使用率较高')

    #画图
    chart = workbook.add_chart({'type': 'pie'})    #创建一个图表对象
    chart.set_size({'width': 450, 'height': 350})    #设置图表大小
    chart.set_title ({'name': u'编译服务器CPU使用率分布图'})    #设置图表（上方）大标题
    chart.set_y_axis({'name': 'count'})    #设置y轴（左侧）小标题 
    chart.set_x_axis({'text_axis': True})
           
    chart.add_series({
                      'categories':'=%s!$G$72:$J$72'%(sheetname),
                      'values':'=%s!$G$73:$J$73'%(sheetname),
                      'data_labels': {'percentage': True,'value':True},
                      'line': {'color': 'black'},
                      'name':'server count',
                      'points': [
                        {'fill': {'color': 'red'}},
                        {'fill': {'color': 'blue'}},
                        {'fill': {'color': 'yellow'}},
                        {'fill': {'color': 'green'}},
                        ],
                      })
    daily_worksheet.insert_chart('C79', chart)

    
    #写入磁盘report         
    workbook.close()

def write_daily_usage_to_db(server_CPU_usage_summary):
    tmp=models.CompileDailyServerUsage(date=datetime.date(now.year,now.month,now.day),region='CHN',
                                   normal_usage_server_count=server_CPU_usage_summary['normal_usage_server_count'],
                                   low_usage_server_count=server_CPU_usage_summary['low_usage_server_count'],
                                   nearly_no_usage_server_count=server_CPU_usage_summary['nearly_no_usage_server_count'],
                                   high_usage_server_count=server_CPU_usage_summary['high_usage_server_count']
                                   )
    tmp.save()   

def write_server_info_to_db(server_CPU_usage_dict):
    print 'asdfasdf', server_CPU_usage_dict
    for key,value in server_CPU_usage_dict.items():
        print key,value
        owner=value[0].strip('\r')
        ipaddress=value[1]
        cpu_load_gt_50_coun=value[2]
        total_memory=value[3]
        total_cpu_cores=value[4]
        largest_disk_mount_point=value[5]
        total_diskspace=value[6]
        used_diskspace=value[7]
        disk_used_ratio=value[8]
        print owner,ipaddress,cpu_load_gt_50_coun,total_memory,total_cpu_cores,largest_disk_mount_point,total_diskspace,used_diskspace,disk_used_ratio
        tmp=models.CompileServerUsageInfo(date=datetime.date(now.year,now.month,now.day),
                                          hostname=key,
                                          owner=owner,
                                          ipaddress=ipaddress,
                                          cpu_load_gt_50_coun=cpu_load_gt_50_coun,
                                          total_memory=total_memory,
                                          total_cpu_cores=total_cpu_cores,
                                          largest_disk_mount_point=largest_disk_mount_point,
                                          total_diskspace=total_diskspace,
                                          used_diskspace=used_diskspace,
                                          disk_used_ratio=disk_used_ratio,
                                          )
        tmp.save()


def write_file(file,info):
    with open(file,'a') as f:
        f.write(info)
        f.write('\n')

def clear_log(file):
    os.remove(file)
        
        
def write_to_filebeat_log(server_CPU_usage_dict):
    filebeat_log="log/server_usage_info.log"
    clear_log(filebeat_log)
    for key,value in server_CPU_usage_dict.items():
        print key, value
        tmp={}
        tmp['hostname']=key
        tmp['owner']=value[0].strip('\r')
        tmp['ipaddress']=value[1]
        tmp['cpu_load_gt_50_coun']=value[2]
        tmp['total_memory']=int(value[3].replace('G',''))
        tmp['total_cpu_cores']=value[4]
        tmp['largest_disk_mount_point']=value[5]
        tmp['total_diskspace']=int(value[6].replace('G',''))
        tmp['used_diskspace']=int(value[7].replace('G',''))
        tmp['disk_used_ratio']=value[8]
        a=json.dumps(tmp)
        write_file(filebeat_log,a)
        

if __name__=='__main__':
    now=datetime.datetime.now()-datetime.timedelta(days=1)
    date='-'.join([str(now.year),str(now.month),str(now.day)])
    #CPU 使用情况分析
    begintimestamp,endtimestamp=generate_begin_end_time(date)
    print date,begintimestamp,endtimestamp
    cpu_usage_items=get_cpu_usage_items()
    server_CPU_usage_dict,server_CPU_usage_summary=analyze_cpu_usage_history_data(cpu_usage_items, begintimestamp, endtimestamp,0.2)
    write_daily_usage_to_db(server_CPU_usage_summary)
    print "cpu done"
    #磁盘使用情况分析
    print "disk begin"
    disk_items=get_disk_items()
    print "get_disk items done"
    print disk_items
    diskspace_usage=analyze_disk_history_data(disk_items)
    #memory 信息汇总
    memory_items=get_memory_items()
    memory_info_summary=analyze_memory_history_data(memory_items)
    print "memory begin"
    #CPU信息汇总
    cpu_items=get_cpu_items()
    cpu_info_summary=analyze_CPU_data(cpu_items)
    print server_CPU_usage_dict
    for hostname in server_CPU_usage_dict.keys():
        if memory_info_summary.has_key(hostname):
            server_CPU_usage_dict[hostname].append(memory_info_summary[hostname])
        if cpu_info_summary.has_key(hostname):
            server_CPU_usage_dict[hostname].append(cpu_info_summary[hostname])
        if diskspace_usage.has_key(hostname):
            server_CPU_usage_dict[hostname].append(diskspace_usage[hostname]['mount_point'])
            server_CPU_usage_dict[hostname].append(diskspace_usage[hostname]['total_diskspace'])
            server_CPU_usage_dict[hostname].append(diskspace_usage[hostname]['used_diskspace'])
            server_CPU_usage_dict[hostname].append(diskspace_usage[hostname]['used_ratio'])
    print server_CPU_usage_dict
    write_to_filebeat_log(server_CPU_usage_dict)
    write_server_info_to_db(server_CPU_usage_dict)
    write_daily_report('%s compile_server_usage_report.xlsx' %date,server_CPU_usage_dict,server_CPU_usage_summary)

    
    send_mail(u"编译服务器使用率分布情况， 及每台编译服务器的磁盘大小及磁盘使用率",attachment='%s compile_server_usage_report.xlsx'%date,sender='SEE@le.com',receiver=['supertv_cm@le.com'])
    #send_mail(u"编译服务器使用率分布情况， 及每台编译服务器的磁盘大小及磁盘使用率",attachment='%s compile_server_usage_report.xlsx'%date,sender='SEE@le.com',receiver=['yangaofeng@le.com','leitao@le.com'])
    




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
from django.core.exceptions import ObjectDoesNotExist
import re

def get_items():
    assigned_hosts_item=[]
    group=models.Groups.objects.get(name='diantong vms')
    hosts=models.HostsGroups.objects.filter(groupid=group)
    items=[]
    for host in hosts:
        print host.hostid
        item=models.Items.objects.get(key_field='check.vm.util.trapper',
                                  hostid=host.hostid)
    
        items.append(item)
    total_hosts=len(items)
    for item in items:
        if len(item.hostid.description)!=0:
            assigned_hosts_item.append(item)
    print assigned_hosts_item,total_hosts
    return assigned_hosts_item,total_hosts

def get_Region_items():
    US_assigned_hosts=[]
    ZH_assigned_hosts=[]
    total_US_hosts=0
    total_ZH_hosts=0
    group=models.Groups.objects.get(name='diantong vms')
    hosts=models.HostsGroups.objects.filter(groupid=group)
    items=[]
    for host in hosts:
        item=models.Items.objects.get(key_field='check.vm.util.trapper',
                                  hostid=host.hostid)
    
        items.append(item)
    for item in items:
        us_server=re.search("vm-10-120|vm-10-212",item.hostid.name)
        host_inventory=models.HostInventory.objects.get(hostid=item.hostid)
        
        if us_server:
            total_US_hosts=total_US_hosts+1
            if len(host_inventory.date_hw_install)!=0:
                US_assigned_hosts.append(item)
        else:
            total_ZH_hosts=total_ZH_hosts+1
            if len(host_inventory.date_hw_install)!=0: #date_hw_install means the assigned date
                ZH_assigned_hosts.append(item)
    print len(US_assigned_hosts),total_US_hosts,len(ZH_assigned_hosts),total_ZH_hosts
    return US_assigned_hosts,total_US_hosts,ZH_assigned_hosts,total_ZH_hosts
    
    
def get_Region_ws_items():
    US_assigned_hosts=[]
    ZH_assigned_hosts=[]
    total_US_hosts=0
    total_ZH_hosts=0
    items=models.Items.objects.filter(key_field='check.vm.util.ws.trapper',
                                  hostid__name__startswith='vm')
    for item in items:
        us_server=re.search("vm-10-120|vm-10-212",item.hostid.name)
        if us_server:
            total_US_hosts=total_US_hosts+1
            if len(item.hostid.description)!=0:
                US_assigned_hosts.append(item)
        else:
            total_ZH_hosts=total_ZH_hosts+1
            if len(item.hostid.description)!=0:
                ZH_assigned_hosts.append(item)
    print len(US_assigned_hosts),total_US_hosts,len(ZH_assigned_hosts),total_ZH_hosts
    return US_assigned_hosts,total_US_hosts,ZH_assigned_hosts,total_ZH_hosts

def generate_begin_end_time(date):
    data_array=date.split('-')
    year=int(data_array[0])
    month=int(data_array[1])
    day=int(data_array[2])
    dateC=datetime.datetime(year,month,day,0,0,0)
    #date那天00:00:00 分的时间戳
    today_timestamp=time.mktime(dateC.timetuple())
    
    #一天后00:00:00分的时间戳
    oneDayafter = dateC + datetime.timedelta(days = 1)
    oneDayafter_timestamp=time.mktime(oneDayafter.timetuple())   
    return int(today_timestamp),int(oneDayafter_timestamp)

def analyze_hisotry_data(items,begin_time,end_time,total_hosts_count):
    server_not_in_use=[]
    server_in_use=[]
    server_in_use_high=[]
    data_summary={}
    
    for item in items:
        historys=models.HistoryUint.objects.filter(value=1,
                                           itemid=item.itemid,
                                            clock__gte=begin_time,
                                            clock__lte=end_time,
                                            )
        print item.hostid.name
        host_inventory=models.HostInventory.objects.get(hostid=item.hostid)
        if len(historys)==0:
            server_not_in_use.append((item.hostid.name,host_inventory.contact))
        elif len(historys)>20: #30天当中，有18天都有使用的虚拟机
            server_in_use.append(item.hostid.name)
            server_in_use_high.append((item.hostid.name,host_inventory.contact))
        else:
            server_in_use.append(item.hostid.name)
            
            
    server_not_in_use_count=len(server_not_in_use)
    server_in_use_count=len(server_in_use)
    assigned_server_count=len(items)
    try:
        data_summary['UsedRatio']=float('%0.3f'%(float(server_in_use_count)/float(assigned_server_count)))
    except ZeroDivisionError:
        data_summary['UsedRatio']=0
    try:
        data_summary['NoUseRatio']=float('%0.3f'%(float(server_not_in_use_count)/float(assigned_server_count)))
    except ZeroDivisionError:
        data_summary['NoUseRatio']=0
    data_summary['ServerTotal']=total_hosts_count
    data_summary['AssignedServerCount']=assigned_server_count
    data_summary['ServerInUseCount']=server_in_use_count
    data_summary['ServerNoInUseList']=server_not_in_use
    data_summary['ServerNoInUseCount']=server_not_in_use_count
    data_summary['ServerInUse']=server_in_use
    data_summary['ServerInUseHigh']=server_in_use_high
    return data_summary


def each_day_summary(week_day_list,items_info,region):
    each_day_report=[]
    data_summary={}
    import copy
    for date in week_day_list:
        date_list=date.split('-')
        year=int(date_list[0])
        month=int(date_list[1])
        day=int(date_list[2])
        try:
            item=models.ScmDailyServerUsageSeparate.objects.get(date=datetime.date(year,month,day),region=region)
            data_summary['date']=str(item.date)
            data_summary['ServerTotal']=item.servertotalcount
            data_summary['AssignedServerCount']=item.assignedservercount
            data_summary['ServerNoInUseCount']=item.servernotinusecount
            data_summary['UsedRatio']=item.usedratio
            data_summary['Region']=item.region
        except ObjectDoesNotExist:
            continue
        each_day_report.append(copy.deepcopy(data_summary))
    return each_day_report




def generate_week_date_list(today):
    n=7
    week_day_list=[]
    dayfrom = today - datetime.timedelta(days=n)
    dayend = today - datetime.timedelta(days=1)
    time_from = str(datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0))
    time_end = str(datetime.datetime(dayend.year, dayend.month, dayend.day, 23, 59, 59))    
    begin_timestamp=time.mktime(time.strptime(time_from,"%Y-%m-%d %H:%M:%S"))
    end_timestamp=time.mktime(time.strptime(time_end,"%Y-%m-%d %H:%M:%S"))
    
    while n>0:
        servenday = datetime.timedelta(days=n)
        dayfrom = today - servenday
        date_from = datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day,0,0,0).strftime('%Y-%m-%d')
        week_day_list.append(str(date_from))
        n=n-1
    return week_day_list,int(begin_timestamp),int(end_timestamp)




    
def write_weekly_report(filename,each_day_data,weekly_data_summary):
    write_daily_data=[]
    write_weekly_data=[]
    workbook = xlsxwriter.Workbook(filename)
    daily_sheetname='daily_report'
    daily_worksheet = workbook.add_worksheet(daily_sheetname)
    daily_worksheet.set_column('A:F',27)
    weekly_sheetname='weekly_report'    
    weekly_worksheet = workbook.add_worksheet(weekly_sheetname)
    weekly_worksheet.set_column('A:F',27)
    no_use_server_sheetname='weekly_no_use_assigned_server'
    no_use_server_sheet=workbook.add_worksheet(no_use_server_sheetname)
    no_use_server_sheet.set_column('A:B',34)
    format_title=workbook.add_format()    #定义format_title格式对象
    format_title.set_border(1)   #定义format_title对象单元格边框加粗(1像素)的格式
    format_title.set_bg_color('#cccccc')   #定义format_title对象单元格背景颜色为'#cccccc'的格式    
    format_title.set_align('center')    #定义format_title对象单元格居中对齐的格式
    format_title.set_bold()    #定义format_title对象单元格内容加粗的格式  
    #定义数据format
    format=workbook.add_format()    #定义format格式对象
    format.set_border(1)    #定义format对象单元格边框加粗(1像素)的格式
    
    #写daily 数据
    title=['date','region','ServerTotal','AssignedServerCount','AssignServerNoInUseCount','AssignedUsedRatio']
    write_line=1
    for region_data in each_day_data:
        daily_worksheet.write_row('A%d'%write_line,title,format_title)
        write_line=write_line+1
        for data in region_data:
            a=[data['date'],data['Region'],data['ServerTotal'],data['AssignedServerCount'],data['ServerNoInUseCount'],data['UsedRatio']]
            daily_worksheet.write_row('A%d'%write_line,a,format)
            write_line=write_line+1
        write_line=write_line+1
        days=len(region_data) #统计几天的数据

    daily_chart = workbook.add_chart({'type': 'column'})    #创建一个图表对象
    daily_chart.set_size({'width': 600, 'height': 387})    #设置图表大小
    daily_chart.set_title ({'name': u'被分配的VM的日活跃率'})    #设置图表（上方）大标题
    daily_chart.set_y_axis({'name': 'Ratio','num_format': '0%'})  #设置y轴（左侧）小标题 
    
    daily_chart.add_series({'values':'=%s!$F$2:$F$%d' %(daily_sheetname,1+days),
                      'categories':'=%s!$A$2:$A$%d' %(daily_sheetname,1+days),
                      'name': '=%s!$B$2' %daily_sheetname,
                      'line': {'color': 'black'},
                      })
    
    
    end_line=write_line-2
    begin_line=write_line-1-days
        
    daily_chart.add_series({'values':'=%s!$F$%d:$F$%d' %(daily_sheetname,begin_line,end_line),
                      'categories':'=%s!$A$2:$A$%d' %(daily_sheetname,1+days),
                      'name': '=%s!$B$%d' %(daily_sheetname,begin_line),
                      'line': {'color': 'black'},
                      })
   
    daily_worksheet.insert_chart('B10', daily_chart)

    #写weekly数据
    title=['date','region','ServerTotal','AssignedServerCount','AssignServerNoInUseCount','AssignedUsedRatio']
    weekly_worksheet.write_row('A1',title,format_title) 
    write_line=2
    for region_data in weekly_data_summary:
        print region_data
        data=['weekly%s---%s' %(region_data['begin_date'],region_data['end_date']),
                    region_data['Region'],
                    region_data['total_server_count'], 
                       region_data['AssignedServerCount'],
                       region_data['ServerNoInUseCount'],                
                       region_data['UsedRatio'],
                       ]
        weekly_worksheet.write_row('A%d'%write_line,data,format)
        write_line=write_line+1 
    
    weekly_worksheet.write('K1',0,format)
    weekly_chart=workbook.add_chart({'type': 'column',}) 
    weekly_chart.set_size({'width': 364, 'height': 234})    #设置图表大小
    weekly_chart.set_title ({'name': u'被分配的VM的周活跃率'})    #设置图表（上方）大标题
    weekly_chart.set_y_axis({'name': 'Ratio','num_format': '0%'})    #设置y轴（左侧）小标题   
     
    weekly_chart.add_series({'values':'=%s!$F$2' %weekly_sheetname,
                      'categories':'=%s!$A$2' %weekly_sheetname,
                      'name': '=%s!$B$2' %weekly_sheetname,
                      'line': {'color': 'black'},
                      })
    
    
    weekly_chart.add_series({'values':'=%s!$F$3' %weekly_sheetname,
                      'categories':'=%s!$A$2' %weekly_sheetname,
                      'name': '=%s!$B$3' %weekly_sheetname,
                      'line': {'color': 'black'},
                      })


    weekly_chart.add_series({'values':'=%s!$K$1' %weekly_sheetname,
                      'categories':'=%s!$A$2' %weekly_sheetname,
                      'name': '',
                      'line': {'color': 'black'},
                      })
    
    weekly_chart.set_legend({'delete_series': [2]})
    weekly_worksheet.insert_chart('B4',weekly_chart)
    
    #写weekly_no_use_assigned_server数据
    title=['hostname','hostowner']
    no_use_server_sheet.write_row('A1',title,format_title)
    write_line=2
    for region_data in weekly_data_summary:
        for hostinfo in region_data['ServerNoInUseList']:
            no_use_server_sheet.write_row('A%d'%write_line,hostinfo,format)
            write_line=write_line+1    
    workbook.close()


def write_monthly_report(filename,each_day_data,weekly_data_summary,total_hosts_count):
    write_data=[]
    workbook = xlsxwriter.Workbook(filename)
    daily_sheetname='daily_report'
    daily_worksheet = workbook.add_worksheet(daily_sheetname)
    daily_worksheet.set_column('A:E',27)
    weekly_sheetname='monthly_report'    
    weekly_worksheet = workbook.add_worksheet(weekly_sheetname)
    weekly_worksheet.set_column('A:E',27)
    no_use_server_sheetname='monthly_no_use_assigned_server'
    no_use_server_sheet=workbook.add_worksheet(no_use_server_sheetname)
    no_use_server_sheet.set_column('A:B',34)
    
    title=['date','ServerTotal','AssignedServerCount','AssignServerNoInUseCount','AssignedUsedRatio']

    for data in each_day_data:
        a=[data['date'],data['ServerTotal'],data['AssignedServerCount'],data['ServerNoInUseCount'],data['UsedRatio']]
        write_data.append(a)
    
    weekly_write_data=['weekly%s---%s' %(weekly_data_summary['begin_date'],weekly_data_summary['end_date']),
                       total_hosts_count,
                       weekly_data_summary['AssignedServerCount'],
                       weekly_data_summary['ServerNoInUseCount'],                
                       weekly_data_summary['UsedRatio'],
                       ]

    
    #server_not_in_uselist=weekly_data_summary['ServerNoInUseList']
    
    #写title format
    format_title=workbook.add_format()    #定义format_title格式对象
    format_title.set_border(1)   #定义format_title对象单元格边框加粗(1像素)的格式
    format_title.set_bg_color('#cccccc')   #定义format_title对象单元格背景颜色为'#cccccc'的格式    
    format_title.set_align('center')    #定义format_title对象单元格居中对齐的格式
    format_title.set_bold()    #定义format_title对象单元格内容加粗的格式
    
    
    #定义数据format
    format=workbook.add_format()    #定义format格式对象
    format.set_border(1)    #定义format对象单元格边框加粗(1像素)的格式
    #写入total
    no_use_server_sheet_title=[weekly_write_data[0],'hostowner']
    daily_worksheet.write_row('A1',title,format_title)
    weekly_worksheet.write_row('A1',title,format_title)
    no_use_server_sheet.write_row('A1',no_use_server_sheet_title,format_title)
    
    #写入数据
    #weekly_worksheet.write_row('A2',weekly_write_data,format)

    
    write_line=2
    for data in write_data:
        daily_worksheet.write_row('A%d'%write_line,data,format)
        write_line=write_line+1  
        
    weekly_worksheet.write_row('A2',weekly_write_data,format)
    


    #画图
    chart = workbook.add_chart({'type': 'column'})    #创建一个图表对象
    chart.set_size({'width': 600, 'height': 387})    #设置图表大小
    chart.set_title ({'name': u'被分配的VM的日活跃率'})    #设置图表（上方）大标题
    chart.set_y_axis({'name': 'Ratio','num_format': '0%'})    #设置y轴（左侧）小标题 
           
    chart.add_series({'values':'=%s!$E$2:$E$%d' %(daily_sheetname,write_line),
                      'categories':'=%s!$A$2:$A$%d' %(daily_sheetname,write_line),
                      'name': '=%s!$E$1' %daily_sheetname,
                      'line': {'color': 'black'},
                      })
    daily_worksheet.insert_chart('B10', chart)
    
    
    weekly_chart=workbook.add_chart({'type': 'column'}) 
    weekly_chart.set_size({'width': 364, 'height': 234})    #设置图表大小
    weekly_chart.set_title ({'name': u'被分配的VM的月活跃率'})    #设置图表（上方）大标题
    weekly_chart.set_y_axis({'name': 'Ratio','num_format': '0%'})    #设置y轴（左侧）小标题    
    weekly_chart.add_series({'values':'=%s!$E$2' %weekly_sheetname,
                      'categories':'=%s!$A$2' %weekly_sheetname,
                      'name': '=%s!$E$1' %weekly_sheetname,
                      'line': {'color': 'black'},
                      })
       
    weekly_worksheet.insert_chart('B4',weekly_chart)
    
    write_line=2
    for hostinfo in weekly_data_summary['ServerNoInUseList']:
        no_use_server_sheet.write_row('A%d'%write_line,hostinfo,format)
        write_line=write_line+1  
    
    workbook.close()



def generate_month_day_list(today):
    print today.year,today.month-1
    wday, monthRange=calendar.monthrange(today.year, today.month-1)
    print monthRange
    begintime='%d-%d-01 00:00:00'%(today.year,today.month-1)
    begin_timestamp=time.mktime(time.strptime(begintime,"%Y-%m-%d %H:%M:%S"))
    endtime='%d-%d-%d 23:59:59'%(today.year,today.month-1,monthRange)
    end_timestamp=time.mktime(time.strptime(endtime,"%Y-%m-%d %H:%M:%S"))    
    month_day_list=[]
    for i in range(1,monthRange+1):
        month_day_list.append('%d-%d-%d'%(today.year,today.month-1,i))
    print month_day_list,begin_timestamp,end_timestamp
    return month_day_list,int(begin_timestamp),int(end_timestamp)

    
if __name__=='__main__':
    get_items()
    get_Region_items()

#!/usr/bin/python
#-*- coding:utf-8 -*-  
from util import *
from mail import send_mail
from daily_force_recycle_vm import generate_30_days_list

def write_daily_usage(date):
    data=models.CompileDailyServerUsage.objects.get(date=date)
    workbook = xlsxwriter.Workbook(filename)
    daily_sheetname='daily_report'
    daily_worksheet = workbook.add_worksheet(daily_sheetname)
    format_title=workbook.add_format()    #定义format_title格式对象
    format_title.set_border(1)   #定义format_title对象单元格边框加粗(1像素)的格式
    format_title.set_bg_color('#cccccc')   #定义format_title对象单元格背景颜色为'#cccccc'的格式    
    format_title.set_align('center')    #定义format_title对象单元格居中对齐的格式
    format_title.set_bold()    #定义format_title对象单元格内容加粗的格式  
    #定义数据format
    format=workbook.add_format()    #定义format格式对象
    format.set_border(1)    #定义format对象单元格边框加粗(1像素)的格式
    
def each_day_summary(week_day_list,region):
    each_day_report=[]
    data_summary={}
    import copy
    for date in week_day_list:
        date_list=date.split('-')
        year=int(date_list[0])
        month=int(date_list[1])
        day=int(date_list[2])
        try:
            item=models.CompileDailyServerUsage.objects.get(date=datetime.date(year,month,day),region=region)
            
            data_summary['date']=str(item.date)
            data_summary['normal_usage_server_count']=item.normal_usage_server_count
            data_summary['low_usage_server_count']=item.low_usage_server_count
            data_summary['nearly_no_usage_server_count']=item.nearly_no_usage_server_count
            data_summary['high_usage_server_count']=item.high_usage_server_count
        except ObjectDoesNotExist:
            continue
        each_day_report.append(copy.deepcopy(data_summary))
    return each_day_report


def write_weekly_report(filename,each_day_data,weekly_cpu_nearly_no_usage):
    write_daily_data=[]
    write_weekly_data=[]
    workbook = xlsxwriter.Workbook(filename)
    daily_sheetname='daily_report'
    daily_worksheet = workbook.add_worksheet(daily_sheetname)
    daily_worksheet.set_column('A:F',27)
    no_use_server_sheetname='weekly_CPU_no_use_server'
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
    write_line=1
    title=['date','normal_usage_server_count','low_usage_server_count','nearly_no_usage_server_count','high_usage_server_count']
    daily_worksheet.write_row('A%d'%write_line,title,format_title)
    write_line=write_line+1
    for data in each_day_data:
        a=[data['date'],data['normal_usage_server_count'],data['low_usage_server_count'],data['nearly_no_usage_server_count'],data['high_usage_server_count']]
        daily_worksheet.write_row('A%d'%write_line,a,format)
        write_line=write_line+1
    
    #daily 画图
    daily_chart = workbook.add_chart({'type': 'line'})    #创建一个图表对象
    daily_chart.set_size({'width': 600, 'height': 387})    #设置图表大小
    daily_chart.set_title ({'name': u'编译服务器一周使用趋势'})    #设置图表（上方）大标题
    daily_chart.set_y_axis({'name': 'Number'})  #设置y轴（左侧）小标题 
    
    daily_chart.add_series({'values':'=%s!$E$2:$E$%d' %(daily_sheetname,write_line),
                        'marker': {'type': 'diamond'},
                      'categories':'=%s!$A$2:$A$%d' %(daily_sheetname,write_line),
                      'name': '=%s!$E$1' %daily_sheetname,
                      'line': {'color': 'red'},
                      'fill': {'color': 'red'},
                      })
    
    daily_chart.add_series({'values':'=%s!$C$2:$C$%d' %(daily_sheetname,write_line),
                      'categories':'=%s!$A$2:$A$%d' %(daily_sheetname,write_line),
                      'name': '=%s!$C$1' %daily_sheetname,
                      'line': {'color': 'blue'},
                      'fill': {'color': 'blue'},
                      'marker': {'type': 'diamond'},
                      })   
     
    daily_chart.add_series({'values':'=%s!$B$2:$B$%d' %(daily_sheetname,write_line),
                      'categories':'=%s!$A$2:$A$%d' %(daily_sheetname,write_line),
                      'name': '=%s!$B$1' %daily_sheetname,
                      'line': {'color': 'green'},
                      'fill': {'color': 'green'},
                      'marker': {'type': 'diamond'},
                      }) 
    
    daily_chart.add_series({'values':'=%s!$D$2:$D$%d' %(daily_sheetname,write_line),
                      'categories':'=%s!$A$2:$A$%d' %(daily_sheetname,write_line),
                      'name': '=%s!$D$1' %daily_sheetname,
                      'line': {'color': 'yellow'},
                     'fill': {'color': 'yellow'},
                     'marker': {'type': 'diamond'},

                      })       
   
    daily_worksheet.insert_chart('B10', daily_chart)
    
    #写入一周不使用的server数据
    no_use_server_sheet.write_row('A1',['hostname','ipaddress','owner'],format_title)
    write_line=2
    for data in weekly_cpu_nearly_no_usage:
        no_use_server_sheet.write_row('A%d'%write_line,data,format)
        write_line=write_line+1
    
    workbook.close()

def analyze_weekly_nearly_no_usage(host,beign_date,end_date):

    historys=models.CompileServerUsageInfo.objects.filter(hostname=host,date__gte=beign_date,date__lte=end_date)
    i=0
    for history in historys:
        i=i+history.cpu_load_gt_50_coun
        ipaddress=history.ipaddress
        owner=history.owner
    if i==0:
        return [host,ipaddress,owner]
    
def generate_weekly_no_usage():
    now=datetime.datetime.now()-datetime.timedelta(days=1)
    begin_date=datetime.date(now.year,now.month,now.day)-datetime.timedelta(days=8)
    end_date=datetime.date(now.year,now.month,now.day)
    hosts=models.Hosts.objects.filter(name__startswith='pcnbj-cp')  
    weekly_cpu_nearly_no_usage=[]
    for host in hosts:
        tmp=analyze_weekly_nearly_no_usage(host.name,begin_date,end_date)
        if tmp:
            weekly_cpu_nearly_no_usage.append(tmp)
    
    return weekly_cpu_nearly_no_usage
    
    
if __name__=='__main__':
    yesterday=datetime.datetime.now()-datetime.timedelta(days=1)   
    
    #一周内每天的使用情况
    day_list,begin_timestamp,end_timestamp=generate_week_date_list(yesterday)
    region='CHN'
    each_day_summary=each_day_summary(day_list,region)
    print each_day_summary
    
    #一周都没有使用的server
    weekly_cpu_nearly_no_usage=generate_weekly_no_usage()
    filename='weekly_compile_server_usage_report.xlsx'
    write_weekly_report(filename,each_day_summary,weekly_cpu_nearly_no_usage)
        
    
    
    #send_mail("weekly compile server usage report",attachment=report_file_name,sender='SEE@le.com',receiver=['SEE@le.com'])
    send_mail("weekly compile server usage report",attachment=filename,sender='SEE@le.com',receiver=['yangaofeng@le.com'])

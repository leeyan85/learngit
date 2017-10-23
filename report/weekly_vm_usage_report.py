#!/usr/bin/python
#-*- coding:utf-8 -*-  
from util import *
from mail import send_mail

if __name__=='__main__':
    today=datetime.datetime.now()
    
    #获取被分配的机器监控item列表，总过哪个有多少台机器
    US_assigned_items,total_US_hosts,ZH_assigned_items,total_ZH_hosts=get_Region_items()  
    #一周内每天的使用情况
    day_list,begin_timestamp,end_timestamp=generate_week_date_list(today)
    USA_each_day_summary=each_day_summary(day_list,US_assigned_items,"USA")
    USA_week_data_summary=analyze_hisotry_data(US_assigned_items,begin_timestamp,end_timestamp,total_US_hosts)
    USA_week_data_summary['begin_date']=day_list[0]
    USA_week_data_summary['end_date']=day_list[-1]
    USA_week_data_summary['total_server_count']=total_US_hosts
    USA_week_data_summary['Region']="USA"
    
    
    CHN_each_day_summary=each_day_summary(day_list,ZH_assigned_items,"CHN")
    CHN_week_data_summary=analyze_hisotry_data(ZH_assigned_items,begin_timestamp,end_timestamp,total_ZH_hosts)
    CHN_week_data_summary['begin_date']=day_list[0]
    CHN_week_data_summary['end_date']=day_list[-1]
    CHN_week_data_summary['total_server_count']=total_ZH_hosts
    CHN_week_data_summary['Region']="CHN"
    
    report_file_name='weekly_server_usage_report.xlsx'
    ##print each_day_summary,data_summary
    regions_each_day_summary=[]
    regions_each_day_summary.append(USA_each_day_summary)
    regions_each_day_summary.append(CHN_each_day_summary)
    regions_weekly_summary=[]
    regions_weekly_summary.append(USA_week_data_summary)
    regions_weekly_summary.append(CHN_week_data_summary)
    
    write_weekly_report(report_file_name,regions_each_day_summary,regions_weekly_summary)
    
    #send_mail("weekly VM server usage report",attachment=report_file_name,sender='SEE@le.com',receiver=['SEE@le.com'])
    send_mail("weekly VM server usage report",attachment=report_file_name,sender='SEE@le.com',receiver=['SEE@le.com'])

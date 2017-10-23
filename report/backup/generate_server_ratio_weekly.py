#!/usr/bin/python
#-*- coding:utf-8 -*-  
from util import *
from mail import send_mail

if __name__=='__main__':
    today=datetime.datetime.now()
    
    #获取被分配的机器监控item列表，总过哪个有多少台机器
    items_info,total_hosts_count=get_items()

    
    #一周内每天的使用情况

    day_list,begin_timestamp,end_timestamp=generate_week_date_list(today)
    each_day_summary=each_day_summary(day_list,items_info)  
    data_summary=analyze_hisotry_data(items_info,begin_timestamp,end_timestamp,total_hosts_count)
    data_summary['begin_date']=day_list[0]
    data_summary['end_date']=day_list[-1]    
    print data_summary
    report_file_name='weekly_server_usage_report.xlsx'
    write_weekly_report(report_file_name,each_day_summary,data_summary,total_hosts_count)
    send_mail("weekly VM server usage report",attachment=report_file_name,sender='yangaofeng@le.com',receiver=['SEE@le.com'])
    #send_mail("weekly VM server usage report",attachment=report_file_name,sender='yangaofeng@le.com',receiver=['yangaofeng@le.com'])

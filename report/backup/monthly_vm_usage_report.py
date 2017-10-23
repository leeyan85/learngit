#!/usr/bin/python
#-*- coding:utf-8 -*-  
from util import *
from mail import send_mail

if __name__=='__main__':
    today=datetime.datetime.now()+datetime.timedelta(7)
    
    #获取被分配的机器监控item列表，总过哪个有多少台机器
    items_info,total_hosts_count=get_items()

    
    #一周内每天的使用情况

    month_day_list,begin_timestamp,end_timestamp=generate_month_day_list(today)
    each_day_summary=each_day_summary(month_day_list,items_info,'All')  
    month_data_summary=analyze_hisotry_data(items_info,begin_timestamp,end_timestamp,total_hosts_count)
    month_data_summary['begin_date']=month_day_list[0]
    month_data_summary['end_date']=month_day_list[-1]    
    print month_data_summary
    report_file_name='monthly_server_usage_report.xlsx'
    write_monthly_report(report_file_name,each_day_summary,month_data_summary,total_hosts_count)
    #send_mail("monthly VM server usage report",attachment=report_file_name,sender='yangaofeng@le.com',receiver=['yangaofeng@le.com'])
    send_mail("monthly VM server usage report",attachment=report_file_name,sender='yangaofeng@le.com',receiver=['SEE@le.com'])

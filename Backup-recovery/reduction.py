#!/usr/bin/env python
# -*- coding:utf-8 -*-

import paramiko
import time
import os
import re
import sys

def log(content):
    '''
    xie ru  ri  zhi
    '''
    with open('reduction.log',"a+") as directory_log:
         directory_log.write(content)

def error():
    print "\033[31mError,Please see the reduction.log \033[0m"

def ipFormatChk(ip_str):
   '''
   pan duan ip he fa xing
   '''
   addr=ip_str.strip().split('.')
   if len(addr) != 4:
      return False
   else:
      for i in addr:
         if not i.strip():
            return False
      if int(addr[0]) <= 0:
         return False
      elif (int(addr[3])>=255) or (int(addr[3])<=0):
         return False
      pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
      if re.match(pattern, ip_str):
         return True
      else:
         return False

class server(object):
    def __init__(self,user_origin,user_target):
        self.user_origin = user_origin
        self.user_target = user_target

    def serveror_scp(self):
         '''
         scp andbase.tar.gz
         '''
         try:
            scp = paramiko.Transport(self.user_target,22)
            scp.connect(username = "letv", password = "leshiVM1404")
            sftp = paramiko.SFTPClient.from_transport(scp)
            localpath='/letv/workspace/cfg_backup/%s/tmp/andbase/andbase.tar.gz'%(self.user_origin)
            remotepath='/tmp/andbase.tar.gz'
            sftp.put(localpath,remotepath)
            scp.close()
            self.tar_cp()
         except:
            ip_error.append(self.user_origin)
            log_str_scp = "%s The %s line of the ip_list,Please check the IP %s link failure\n"%(times,counter,self.user_target)
            log(log_str_scp)
            error()

    def tar_cp(self):
        try:
            instruction = paramiko.SSHClient()
            instruction .set_missing_host_key_policy(paramiko.AutoAddPolicy())
            instruction .connect(self.user_target,22,"letv", "leshiVM1404")
            instruction_list = ["sudo su - andbase -c \'tar zxf /tmp/andbase.tar.gz -C /tmp\'","sudo su - andbase -c \'cp -rf /tmp/home/andbase  /home \'","sudo su - andbase -c \'rm -rf /tmp/andbase.tar.gz\'","sudo su - andbase -c \'rm -rf /tmp/home/\'"]
            for user_ins in instruction_list:
                stdin,stdout, stderr = instruction .exec_command(user_ins)
                if len(stderr.readlines()) != 0:
                   ip_error.append(self.user_origin)
                   log_str_command = "%s The %s line of the ip_list,IP:%s Run the command:%s failure\n"%(times,counter,self.user_target,user_ins)
                   log(log_str_command)
                   error()
                   break
                time.sleep(1)
            instruction .close()

        except:
           ip_error.append(self.user_origin)
           log_str_command_1 = "%s The %s line of the ip_list,IP:%s Abnormal running\n"%(times,counter,self.user_target)
           log(log_str_command_1)
           #bu  zheng  chang  yun  xing
           error()



def Directory_judge(dorigin,dtarget):
        '''
        cha kan  shi  fou  you  bei  fen  shu  ju
        '''
        route = "/letv/workspace/cfg_backup/%s"%(dorigin)
        if os.path.isdir(route):
            Directory_server = server(dorigin,dtarget)
            Directory_server.serveror_scp()
        else:
            Directory_content = "%s The %s line of the ip_list,IP:%s  Backup restore failure Backup does not exist\n"%(times,counter,dorigin)
            log(Directory_content)
            ip_error.append(dorigin)
            error()

#zhi  xing  qian  que ren
# user_affirm = raw_input("Please make sure that the ip_list is correct!!(y/n):")

user_affirm = "y"
if user_affirm == 'y':
   #du  qu  ip_list
            counter = 0
            ip_error= []
            ip_on = sys.argv
            counter +=1
            times = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
            if len(ip_on) == 3:
                origin = ip_on[1]
                target = ip_on[2]
                print "\033[32mIP: %s Began to recover\033[0m"%(target)
                judge_1 = ipFormatChk(origin)
                judge_2 = ipFormatChk(target)
                if judge_1 and judge_2:
                    Directory_judge(origin,target)
                else:
                    log_str_1 = ("%s The %s line of the ip_list,The IP address error\n"%(times,counter))
                    log(log_str_1)
                    ip_error.append(origin)
                    error()
            elif len(ip_on) == 1:
                origin_error = ip_on[0]
                log_str_2 = ("%s The %s line of the ip_list,The IP address error(There is only one IP)\n"%(times,counter))
                log(log_str_2)
                ip_error.append(origin_error)
                error()
            else:
                log_str_3 = ("%s The %s line of the ip_list,The IP address error(There is only one IP)\n"%(times,counter))
                log(log_str_3)
                error()
            #cuo  wu  ip shu chu
            if len(ip_error) == 0:
                pass
            else:
                print
                print "Restore failure of IP(Please see the reduction.log)"
                for i in ip_error:
                    print i
else:
    os._exit(0)






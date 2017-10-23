#!/usr/bin/python
#-*- coding:utf-8 -*-  
import os,sys
import datetime
import time
from jira.client import JIRA
from jira.exceptions import JIRAError
import random
reload(sys)
sys.setdefaultencoding('UTF-8')
import json
sys.path.append('E:\workspace\SCMDB')
sys.path.append('/letv/scripts/SCMDB')
sys.path.append('/letv/scripts/mount_space')
sys.path.append('E:\workspace\central2')
#当使用django作为第三方的脚本调用时必须添加
os.environ['DJANGO_SETTINGS_MODULE'] = 'SCMDB.settings'
import json
import django
import calendar
django.setup()
from servermanage import models
import actions
from django.core.exceptions import ObjectDoesNotExist
from ssh_key import *

issue_link_type="Relates"
InUse_status_id='11'
Unassign_status_id='41'

jira=JIRA(basic_auth=("username","xxxxxxx@"), server="http://jira.letv.cn/")
#request=jira.issue('SEEVM-59')
#print request.fields.customfield_13417.value,request.fields.customfield_13428.value


#resource=jira.issue('SEERESOURCE-155')
#print resource.fields.customfield_13417.value

def generate_random_password():
    random_string=''.join(random.sample('zyxwvutsrqponmlkjihgfedcba123456789',6))
    return random_string

random_password=generate_random_password()

CN_user_notice=u'''
1.    虚拟机已经配置了gerrit sshkey以及.gitconfig文件, 无需再次配置
2.    考虑到目前虚拟机数量有限，如发现长时间(30天)没有使用（虚拟机磁盘连续30天没有发生变化),将会回收虚拟机；
3.    请不要修改VM的主机名，否则会造成监控系统的数据错误，从而影响到VM是否被使用的监控项，可能错误的回收您的虚拟机
4.    虚拟机里都创建了公共账号：andbase, 密码：%s
5.    Samba 访问用户名：andbase  密码：%s   访问方式： \\\\你的虚机IP\workspace, 你的虚拟机IP是VMIP字段
6.    如果要使用VNC连接，下载vncviewer软件, VNC的连接密码是：%s
7.    可以通过运行命令vmcfg来统一修改4,5,6的密码
8.    虚拟化研发环境使用FAQ：http://wiki.letv.cn/pages/viewpage.action?pageId=52078163 
9.    请使用“/letv/workspace”作为你的工作目录，这个目录下的磁盘空间较大
10.   如果遇到VNC问题请看http://wiki.letv.cn/pages/viewpage.action?pageId=63071871
11.   提供一个web工具处理大家日常遇到的虚拟机问题,地址http://ci.le.com/devself
12.    建议编译的时候指定 –j8，首次编译大概80分钟，之后使用ccache缓存后，效果更加明显；
13.   如果碰到不能解决的问题，请联系SEE@le.com
'''%(random_password,random_password,random_password)


US_user_notice=u'''
1. we have configured the gerrit sshkey and .gitconfig, don't need you configure it again
2. we will recycle the your VM, if your VM is not used for 30 days(we monitor the VM usage everyday)
3. Please don’t modify your VM hostname, or it will cause the monitor system data corruption, then impact VM utilization monitor items, may trigger your VM is recycled wrongly
4. default user is "andbase"  default password is "%s"
5. VNC password is "%s", you need install VNCviewer software.
6. samba username is "andbase", password is "%s",  access method: \\\\your VM IP\workspace,  get your VM IP from VMIP fields
7. You can run command "vmcfg" to modify the password in 4,5,6 steps unified
8. Please use "/letv/workspace" as your work directory, it has big disk space
9. if you got VM issues, please read below URL to see if the issue can be fixed
   http://wiki.letv.cn/pages/viewpage.action?pageId=52078163
10. a webtool to fix common VM issues,http://ci.le.com/devself
11. if you can't solve VM issues, you can contact SCM-us@le.com 
'''%(random_password,random_password,random_password)

IN_user_notice=u'''
1. we have configured the gerrit sshkey and .gitconfig, don't need you configure it again
2. we will recycle the your VM, if your VM is not used for 30 days(we monitor the VM usage everyday)
3. Please don’t modify your VM hostname, or it will cause the monitor system data corruption, then impact VM utilization monitor items, may trigger your VM is recycled wrongly
4. default user is "andbase"  default password is "%s"
5. VNC  password is "%s",  you need install VNCviewer software
6. samba username is "andbase", password is "%s",  access method: \\\\your VM IP\workspace, get your VM IP from VMIP fields
7. You can run command "vmcfg" to modify the password in 4,5,6 steps unified 
8. Please use "/letv/workspace" as your work directory, it has big disk space
9. if you got VM issues, please read below URL to see if the issue can be fixed
   http://wiki.letv.cn/pages/viewpage.action?pageId=52078163
10. a webtool to fix common VM issues,http://ci.le.com/devself
11. if you can't solve VM issues, you can contact SCM-india@le.com 
'''%(random_password,random_password,random_password)

def vnc_passwd(ip):
    server=actions.Server(ip,username='letv')
    server.remote_command="(echo %s;echo %s) |sudo su - andbase -c vncpasswd"%(random_password,random_password)
    server.connect()
    server.exec_remote_command()    
    

def smb_passwd(ip):
    server=actions.Server(ip,username='letv')
    server.remote_command="(echo %s;echo %s) |sudo smbpasswd andbase"%(random_password,random_password)
    server.connect()
    server.exec_remote_command()

def account_passwd(ip):
    server=actions.Server(ip,username='letv')
    server.remote_command="echo 'andbase:%s' | sudo chpasswd"%(random_password)
    server.connect()
    server.exec_remote_command()

def write_random_passwd(ip):
    server=actions.Server(ip,username='letv')
    configfile='/home/andbase/.ssh/vmsetup/vm_setup.conf'
    server.remote_command="sudo chmod 777 /home/andbase/.ssh;sudo chmod 777 %s; echo '[pass]' >> %s; echo \"pas = %s\" >> %s;sudo chmod 766 %s;sudo chmod 700 /home/andbase/.ssh"%(configfile,configfile,random_password,configfile,configfile)
    #print server.remote_command
    server.connect()
    server.exec_remote_command()

def init_gitconfig(ip,name,emailaddress):
    server=actions.Server(ip,username='letv')
    server.remote_command='''sudo su - andbase -c "cd /home/andbase/bin;./env_vm_setup -m %s -n %s"''' %(emailaddress,name)
    print ip,server.remote_command
    server.connect()
    server.exec_remote_command()
    
    
def set_random_passwd(ip):
    write_random_passwd(ip)
    vnc_passwd(ip)
    smb_passwd(ip)
    account_passwd(ip)

No_assigned_request=[]

requests=jira.search_issues("project=SEEVM and status=InUse",maxResults=700) #需要优化减小范围
print requests
for request in requests:
    comments="Please do not modify your VM hostname, or it will cause the monitor system data corruption, then impact VM utilization monitor items, may trigger your VM is recycled wrongly."
    jira.add_comment(request,comments)
    

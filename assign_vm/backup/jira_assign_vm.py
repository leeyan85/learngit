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
from jira_recycle_vm import VM

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

def init_message(random_password):
    CN_user_notice=u'''
1.    虚拟机已经配置了gerrit sshkey以及.gitconfig文件, 无需再次配置
2.    考虑到目前虚拟机数量有限，如发现长时间(30天)没有使用（虚拟机磁盘连续30天没有发生变化),将会回收虚拟机；
3.    请不要修改VM的主机名，否则会造成监控系统的数据错误，从而影响到VM是否被使用的监控项，可能错误的回收您的虚拟机
4.    虚拟机里都创建了公共账号：andbase, 密码：%s
5.    Samba 访问用户名：andbase  密码：%s   访问方式： \\\\你的虚机IP\workspace, 你的虚拟机IP是VMIP字段
6.    如果要使用VNC连接，下载vncviewer软件, VNC的连接密码是：%s, VNC 使用说明请看http://wiki.letv.cn/pages/viewpage.action?pageId=63071871
7.    可以通过运行命令vmcfg来统一修改4,5,6的密码
8.    虚拟化研发环境使用FAQ：http://wiki.letv.cn/pages/viewpage.action?pageId=52078163 
9.    请使用“/letv/workspace”作为你的工作目录，这个目录下的磁盘空间较大
10.   提供一个web工具处理大家日常遇到的虚拟机问题,地址http://ci.le.com/devself,使用说明 http://wiki.letv.cn/display/LETVINNO/VM+web+service+system
11.    建议编译的时候指定 –j8，首次编译大概80分钟，之后使用ccache缓存后，效果更加明显；
12.   如果碰到不能解决的问题，请联系SEE@le.com
    '''%(random_password,random_password,random_password)


    US_user_notice=u'''
1. we have configured the gerrit sshkey and .gitconfig, don't need you configure it again
2. we will recycle the your VM, if your VM is not used for 30 days(we monitor the VM usage everyday)
3. Please don’t modify your VM hostname, or it will cause the monitor system data corruption, then impact VM utilization monitor items, may trigger your VM is recycled wrongly
4. default user is "andbase"  default password is "%s"
5. VNC  password is "%s",  you need install VNCviewer software, you can get the VNC usage from URL,http://wiki.letv.cn/pages/viewpage.action?pageId=63071871
6. samba username is "andbase", password is "%s",  access method: \\\\your VM IP\workspace,  get your VM IP from VMIP fields
7. You can run command "vmcfg" to modify the password in 4,5,6 steps unified
8. Please use "/letv/workspace" as your work directory, it has big disk space
9. if you got VM issues, please read below URL to see if the issue can be fixed
   http://wiki.letv.cn/pages/viewpage.action?pageId=52078163
10. a webtool to fix common VM issues,http://ci.le.com/devself, details, see http://wiki.letv.cn/display/LETVINNO/VM+web+service+system
11. if you can't solve VM issues, you can contact SCM-us@le.com 
    '''%(random_password,random_password,random_password)

    IN_user_notice=u'''
1. we have configured the gerrit sshkey and .gitconfig, don't need you configure it again
2. we will recycle the your VM, if your VM is not used for 30 days(we monitor the VM usage everyday)
3. Please don’t modify your VM hostname, or it will cause the monitor system data corruption, then impact VM utilization monitor items, may trigger your VM is recycled wrongly
4. default user is "andbase"  default password is "%s"
5. VNC  password is "%s",  you need install VNCviewer software, you can get the VNC usage from URL,http://wiki.letv.cn/pages/viewpage.action?pageId=63071871
6. samba username is "andbase", password is "%s",  access method: \\\\your VM IP\workspace, get your VM IP from VMIP fields
7. You can run command "vmcfg" to modify the password in 4,5,6 steps unified 
8. Please use "/letv/workspace" as your work directory, it has big disk space
9. if you got VM issues, please read below URL to see if the issue can be fixed
   http://wiki.letv.cn/pages/viewpage.action?pageId=52078163
10. a webtool to fix common VM issues,http://ci.le.com/devself, details, see http://wiki.letv.cn/display/LETVINNO/VM+web+service+system
11. if you can't solve VM issues, you can contact SCM-india@le.com 
    '''%(random_password,random_password,random_password)
    return CN_user_notice,US_user_notice,IN_user_notice


def vnc_passwd(ip):
    server=actions.Server(ip,username='letv')
    server.remote_command="(echo %s;echo %s) |sudo su - andbase -c vncpasswd"%(random_password,random_password)
    server.connect()
    server.exec_remote_command()    
    #restart VNC 
    #vm=VM(ip, 'letv', 'asdfas') 
    #vm.recyclePlaybook("/letv/scripts/ansible/restartvnc.yml",'/letv/leey')
    

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

def restart_vnc(ip):
    vm=VM(ip, 'letv', 'asdfas')
    vm.recyclePlaybook("/letv/scripts/ansible/restartvnc/restartvnc.yml",'/letv/leey')

    
    
if __name__=='__main__':
    No_assigned_request=[]

    requests=jira.search_issues("project=SEEVM and status=InUse AND VMIP is EMPTY ") #需要优化减小范围
    print requests
    for request in requests:
        assignee='yangaofeng'
        request.update(assignee={'name':assignee})
        request_VM_number=int(request.fields.customfield_13428.value)
        random_password=generate_random_password()
        print random_password
        CN_user_notice,US_user_notice,IN_user_notice=init_message(random_password)
        department_pool=request.fields.customfield_13425.child.value
        if request.fields.customfield_13414 is None:
            No_assigned_request.append(request)
            if request.fields.customfield_13425.value=='CN':
                SEERESOURCE_location='CNBJ'
                user_notice=CN_user_notice
            elif request.fields.customfield_13425.value=='US':
                SEERESOURCE_location='USLA'
                user_notice=US_user_notice
            elif request.fields.customfield_13425.value=='IN':
                SEERESOURCE_location='INBLR'
                user_notice=IN_user_notice
            assigned_vm=0
            print user_notice
            print u"申请%s台虚拟机"%request_VM_number
            assigned_date=request.fields.created.split('T')[0]
            while assigned_vm<request_VM_number:
                configuration=request.fields.customfield_13417.value
                resources=jira.search_issues("project = SEERESOURCE AND issuetype = RDVM AND status = TBAssigned AND 'Department Pool' ~ %s AND 'SEERESOURCE Location' = %s and  Configuration = \"%s\""%(department_pool,SEERESOURCE_location,configuration),maxResults=5)
                if len(resources)==0:
                    comment='lack of %s server, please select other configure server'%configuration
                    print comment
                    jira.add_comment(request, comment)
                    jira.transition_issue(request, Unassign_status_id)
                    break
                resource=resources[0]
                resource_ip=resource.fields.customfield_13414
                hostname='vm-'+resource_ip.replace('.','-')
                print hostname
                set_random_passwd(resource_ip)
                restart_vnc(resource_ip)
                if resource.fields.customfield_13417.value==request.fields.customfield_13417.value:
                    print request,resource,SEERESOURCE_location
                    jira.transition_issue(resource,InUse_status_id)
                    jira.create_issue_link(issue_link_type,resource,request,comment=None)
                    time.sleep(5)
                    if assigned_vm==0:
                        ips=resource_ip
                    else:
                        ips=request.fields.customfield_13414+','+resource_ip    
                    request.update(fields={"customfield_13414":ips,"customfield_13429":user_notice})
                    assigned_vm=assigned_vm+1
                    
                else:
                    continue
                try:
                    owner=request.fields.reporter.emailAddress
                    name=request.fields.reporter.name
                    if owner=="":
                        owner=request.fields.reporter.name+'@le.com'
                    if owner=="svn@le.com":
                        owner=request.fields.reporter.name.replace('@ff.com','').replace('_w','').lower()+'@ff.com'
                    if name=="wyan":
                        owner=request.fields.customfield_13427
                    biz=request.fields.customfield_13425.child.value
                    if biz=="LeEco":
                        biz="US"
                except AttributeError:
                    biz=''
                link=request.fields.issuelinks[0]
                resource=jira.issue(link.inwardIssue.key)
                key=generate_ssh_keys(owner.split('@')[0],resource_ip)
                init_gitconfig(resource_ip,owner.split('@')[0],owner)
                print add_ssh_key('diana',owner.split('@')[0],key)
                print add_ssh_key('athena',owner.split('@')[0],key)
                print add_ssh_key('minerva',owner.split('@')[0],key)
                try:
                    host=models.Hosts.objects.get(name=hostname)
                    host_inventory=models.HostInventory.objects.get(hostid=host.hostid)
                    host_inventory.contact=owner
                    host_inventory.tag=biz
                    host_inventory.date_hw_install=assigned_date
                    host_inventory.save()
                    if name=="wyan":
                        owner=request.fields.customfield_13427 + ';' + name+'@le.com'
                    host.description="owner:%s\nserviceline:%s" %(owner,biz)
                    host.save()
                except ObjectDoesNotExist:
                    print "host is not in zabbix"

        else:
            continue

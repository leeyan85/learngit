#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import pexpect
import subprocess
import time
import re

yes_no = "\033[0m[\033[32my\033[0m/\033[31mn\033[0m]"
yes = "[\033[32mOK\033[0m]"
no = "[\033[31merror\033[0m]"
file_url = '/home/andbase/.ssh/vmsetup/vm_setup.conf'

##############################
def checklen(pwd):
    return len(pwd) >= 6 and len(pwd) <= 12
def checkContainUpper(pwd):
    pattern = re.compile('[A-Z]+')
    match = pattern.findall(pwd)
    if match:
        return True
    else:
        return False
def checkContainNum(pwd):
    pattern = re.compile('[0-9]+')
    match = pattern.findall(pwd)
    if match:
        return True
    else:
        return False
def checkContainLower(pwd):
    pattern = re.compile('[a-z]+')
    match = pattern.findall(pwd)
    if match:
        return True
    else:
       return False
def checkPassword(pwd):
    #len
    lenOK=checklen(pwd)
    #Lowercase letters
    lowerOK=checkContainLower(pwd)
    #digital
    numOK=checkContainNum(pwd)
    return (lenOK  and lowerOK and numOK)
##############################

def login(vmsetup_log):
    times = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    new_vmsetup_log = '\n'+times+" "+vmsetup_log
    with open('vm_setup.log',"a+") as vm_setup_log:
         vm_setup_log.write(new_vmsetup_log)

def prin_error(judge,error_content):
    #Output information
    if judge == "1":
        space_len = 30-len(error_content)
        print("%s%s%s"%(error_content,' '*space_len,yes))
    else:
        space_len = 30-len(error_content)
        print("%s%s%s"%(error_content,' '*space_len,no))

def vnc_pas(uservnc_pas):
    try:
        cmd = 'vncpasswd'
        child = pexpect.spawn(cmd)
        child.expect("Password:")
        child.sendline(uservnc_pas)
        child.expect("Verify:")
        child.sendline(uservnc_pas)
        time.sleep(0.5)
        child.sendcontrol('c')
        prin_error("1","VNC Password is changed")
    except:
        prin_error("0","VNC Password is changed")
        login("VNC Password is changed   error")

def andbase_pas(user_inpas):
    '''
    andbase password
    '''
    try:
        time.sleep(0.5)
        cmd = "echo 'andbase:%s' | sudo chpasswd"%(user_inpas)
        os.system(cmd)
        prin_error("1","Andbase Password is changed")
    except:
        prin_error("0","Andbase Password is changed")
        login("Andbase Password is changed  error")

def smb_passwd(samba_passwd):
    try:
        fnull = open(os.devnull, 'w')
        cmd="(echo %s;echo %s) |sudo smbpasswd andbase"%(samba_passwd,samba_passwd)
        result = subprocess.call(cmd, shell = True, stdout = fnull, stderr = fnull)
        time.sleep(1)
        prin_error("1","Samba Password is changed")
    except:
        prin_error("0","Samba Password is changed")
        login("Samba Password is changed  error")

def prompt():
#    times = time.strftime("%H:%M:%S",time.localtime(time.time()))
    result = raw_input("\033[1;29mNew Password:\033[0m")
    return result

def output(content):
    print("\033[1;35m%s\033[0m"%(content))

def userin_affirm(affirm_data):
    print("The password is:%s"%(affirm_data))
    a = raw_input("please confirm[y/n]:")
    if a == "y":
        print("==================start==================")
        vnc_pas(affirm_data)#vncpas
        andbase_pas(affirm_data)#andbase password
        smb_passwd(affirm_data)#samba password
        print("================accomplish===============")
        os._exit(0)
    else:
        pass

def userin():
    '''
    Get the user data
    '''
    output("Plese input new password")
    print '''\033[35mThe password is 6 to 12 letters and Numbers mixing is mandatory.
VNC, samba and andbase login password are same with your input\033[0m'''
    while True:
        vncpas = prompt()
        if vncpas == "exit":
            print("exit ok")
            os._exit(0)
        if checkPassword(vncpas):
            break
        else:
            print("\033[1;31mThe password does NOT meet complexity requirements, please enter 6 to 8 mixed cases and numbers.\033[0m")
        # 0=user mail   1=vnc password  2=git url  3=andbase password
    userin_affirm(vncpas)

print('''
------------------------------------------------------
|          \033[1;30m Welcome to use virtual machine \033[0m          |
|         \033[1;30mSCM team provide technical support\033[0m         |
|          \033[1;30m   \(^o^)/  Email:see@le.com\033[0m              |
------------------------------------------------------
''')

if __name__== "__main__":
    while True:
        userin()


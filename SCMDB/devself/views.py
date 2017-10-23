#-*- coding:utf-8 -*- 
from django.shortcuts import render_to_response,render,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect  
from django.contrib.auth.models import User  
from django.contrib import auth 
from django.contrib import messages
from django.template.context import RequestContext
from django.forms.formsets import formset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from bootstrap_toolkit.widgets import BootstrapUneditableInput
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import LoginForm
from django import forms
import models
import json
import os,sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('/letv/scripts/SCMDB')
sys.path.append('/letv/scripts/mount_space')
sys.path.append('/letv/scripts/assign_vm')
sys.path.append('/letv/scripts/report')
sys.path.append('/letv/scripts/ansible/')
import reset_password
from mail import send_mail
import ansible_api


@csrf_exempt
def login(request):
    if request.method=='GET':
        return render_to_response('test.html')
    elif request.method == 'POST':
        #print request.POST
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            ret={'status':'success'}
            return HttpResponse(json.dumps(ret))
        else:
            ret = {'status': 'failed'}
            return HttpResponse(json.dumps(ret))
        
@csrf_exempt
def login2(request):
    if request.user.is_authenticated():
        return redirect('/home/')
    if request.method == 'GET':
        form = LoginForm()
        return render_to_response('devself/sign-in.html', RequestContext(request, {'loginform': form,}))
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                #print request.session
                return redirect('/home/')
            else:
                return render_to_response('devself/sign-in.html', RequestContext(request, {'loginform': form,'LoginStatus':'username/password is wrong'}))
        else:
            return render_to_response('devself/sign-in.html', RequestContext(request, {'loginform': form,})) 


def CheckOwnerIP(request,ipaddr):   
    email_suffix=u'@le.com'
    user = getattr(request, 'user', None)
    useremail=user.username+email_suffix
    hosts_inventory=models.HostInventory.objects.filter(contact=useremail)
    hosts={}
    for host in hosts_inventory:
        ip=models.Interface.objects.get(hostid=host.hostid)
        hosts[host]=ip
        if ip.ip==ipaddr:
            ownerright=True
            break
        else:
            ownerright=False
            continue
    return ownerright

def GetOwnerIP(request): 
    email_suffix=u'@le.com'
    user = getattr(request, 'user', None)
    useremail=user.username+email_suffix
    hosts_inventory=models.HostInventory.objects.filter(contact=useremail)
    hosts={}
    for host in hosts_inventory:
        ip=models.Interface.objects.get(hostid=host.hostid)
        hosts[host]=ip
    return hosts,user
    
                
@login_required
@csrf_exempt
def home(request):
    hosts,user=GetOwnerIP(request)
    return render_to_response('devself/home.html',RequestContext(request, {'username': user,'vms':hosts}))



@login_required
@csrf_exempt
def ModifyVmPassword(request,ipaddress):
    class RegularForm(forms.Form):    
        ipaddr = forms.CharField(
                required=True,
                label="IP Address",
                error_messages={'required': 'please input the ipaddress'},
                widget=forms.TextInput(
                    attrs={
                        'placeholder':"",
                        'class':"form-control span12",
                        'value': ipaddress,
                    }
                ),
        ) 
        def clean(self):
            if not self.is_valid():
                raise forms.ValidationError("IP and password are required")
            else:
                cleaned_data = super(RegularForm, self).clean()
                
    user = getattr(request, 'user', None)
    button_value='Reset'
    if request.method=="GET":
        #RegularForm.ipaddr.widget.update({'value': ipaddress })
        info="Click Reset button, the password of VNC,samba,system account will be reset unified, you will recive a random password through email, the sender is SEE@le.com, you can run command \"vmcfg\" to modify the password by yourself."
        form = RegularForm()
        ret_dic={'changpasswd':form,'function_name':'Modify VM password','username': user,'info':info,'button_value':button_value}
        return render_to_response('devself/function.html',RequestContext(request,ret_dic))
    else:
        form = RegularForm(request.POST)
        if form.is_valid():
            ipaddr=request.POST.get('ipaddr')
            user = getattr(request, 'user', None)
            ownerright=CheckOwnerIP(request,ipaddr)            
            if ownerright:
                random_password=reset_password.generate_random_password()
                print random_password
                password=reset_password.set_random_passwd(ipaddr,random_password)
                email_suffix=u'@le.com'
                print user.username
                useremail=user.username+email_suffix
                subject='VM random password of %s'%ipaddr
                content='the random password of VNC,samba,system account is \"%s\", you can run command \"vmcfg\" to modify the password unified'%random_password
                send_mail(subject,receiver=[useremail],content=content)
                info="Reset vm %s password sucessfully, please get the passowrd through email, sender is SEE@le.com" %ipaddr
                title="Reset password successfully"
                return render_to_response('devself/functionOK.html', RequestContext(request,{'username':user,'ipaddress':ipaddr,'info':info,'title':title}))
            else:
                return render_to_response('devself/vmOwnerWrong.html', RequestContext(request,{'username':'user','ipaddress':ipaddr}))
            
        else:
            ret_dic={'username':'user','function_name':'Modify VM password','changpasswd':form,'button_value':button_value}
            return render_to_response('devself/function.html', RequestContext(request, ret_dic)) 



def ModifyVmPassword2(request,ipaddress):    
    if request.method=="GET":
        ret_dic={'ipaddr':ipaddress,'function_name':'Modify VM password'}
        return render_to_response('devself/function2.html',RequestContext(request,ret_dic))
    else:
        form = RegularForm(request.POST)
        if form.is_valid():
            print "hello,world"
        else:
            ret_dic={'function_name':'Modify VM password','changpasswd':form}
            return render_to_response('devself/function2.html', RequestContext(request, ret_dic))
           

           
def restartvnc(request,ipaddress):
    class RegularForm(forms.Form):    
        ipaddr = forms.CharField(
                required=True,
                label="IP Address",
                error_messages={'required': 'please input the ipaddress'},
                widget=forms.TextInput(
                    attrs={
                        'placeholder':"",
                        'class':"form-control span12",
                        'value': ipaddress,
                    }
                ),
        ) 
        def clean(self):
            if not self.is_valid():
                raise forms.ValidationError("IP and password are required")
            else:
                cleaned_data = super(RegularForm, self).clean()
                
    user = getattr(request, 'user', None)
    button_value='Restart'
    if request.method=="GET":
        #RegularForm.ipaddr.widget.update({'value': ipaddress })
        info="Click Restart button, VNC service will be restarted to fix the issue that you can't input anything when you use VNC"
        form = RegularForm()
        ret_dic={'changpasswd':form,'function_name':'Modify VM password','username': user,'info':info,'button_value':button_value}
        return render_to_response('devself/function.html',RequestContext(request,ret_dic))
    else:
        form = RegularForm(request.POST)
        if form.is_valid():
            ipaddr=request.POST.get('ipaddr')
            user = getattr(request, 'user', None)
            ownerright=CheckOwnerIP(request,ipaddr)            
            if ownerright:
                info="VM %s restart VNC service successfully"%ipaddr
                title="Restart VNC successfully"
                vm = ansible_api.VM(ipaddr, 'letv', 'asdfas')
                result=json.loads(vm.RunPlaybook('/letv/scripts/ansible/restartvnc.yml','/letv/leey/'))
                print result[ipaddr]['failures']
                return render_to_response('devself/functionOK.html', RequestContext(request,{'username':user,'ipaddress':ipaddr,'info':info,'title':title}))
            else:
                return render_to_response('devself/vmOwnerWrong.html', RequestContext(request,{'username':'user','ipaddress':ipaddr}))
            
        else:
            ret_dic={'username':'user','function_name':'Modify VM password','changpasswd':form,'button_value':button_value}
            return render_to_response('devself/function.html', RequestContext(request, ret_dic)) 


def mountnfs(request,ipaddress):
    class RegularForm(forms.Form):    
        ipaddr = forms.CharField(
                required=True,
                label="IP Address",
                error_messages={'required': 'please input the ipaddress'},
                widget=forms.TextInput(
                    attrs={
                        'placeholder':"",
                        'class':"form-control span12",
                        'value': ipaddress,
                    }
                ),
        ) 
        def clean(self):
            if not self.is_valid():
                raise forms.ValidationError("IP and password are required")
            else:
                cleaned_data = super(RegularForm, self).clean()
                
    user = getattr(request, 'user', None)
    button_value='Mount'
    if request.method=="GET":
        #RegularForm.ipaddr.widget.update({'value': ipaddress })
        info="Click Mount button, NFS disk will be mounted under /le_data"
        form = RegularForm()
        ret_dic={'changpasswd':form,'function_name':'Modify VM password','username': user,'info':info,'button_value':button_value}
        return render_to_response('devself/function.html',RequestContext(request,ret_dic))
    else:
        form = RegularForm(request.POST)
        if form.is_valid():
            ipaddr=request.POST.get('ipaddr')
            user = getattr(request, 'user', None)
            ownerright=CheckOwnerIP(request,ipaddr)            
            if ownerright:
                command="cd /letv/scripts/mount_space;python remote_mount_space.py %s"%ipaddr
                print command
                os.system(command)
                info="VM %s mount NFS successfully on"  %ipaddr
                title="Mount NFS successfully"                
                return render_to_response('devself/functionOK.html', RequestContext(request,{'username':user,'ipaddress':ipaddr,'info':info,'title':title}))
            else:
                return render_to_response('devself/vmOwnerWrong.html', RequestContext(request,{'username':'user','ipaddress':ipaddr}))
            
        else:
            ret_dic={'username':'user','function_name':'Modify VM password','changpasswd':form,'button_value':button_value}
            return render_to_response('devself/function.html', RequestContext(request, ret_dic))   


def logout(request):
    auth.logout(request)
    return redirect('/accounts/login2')

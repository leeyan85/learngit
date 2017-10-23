
#!/bin/env python
# -*- coding:utf8 -*-
import os
import sys
import json
import git
reload(sys)
sys.setdefaultencoding('UTF-8')

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible import constants as C
from ansible.plugins.callback import CallbackBase
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor



class ResultCallback(CallbackBase):
    def __init__(self, *args, **kwargs):  
        super(ResultCallback, self).__init__(*args, **kwargs)  
        self.host_ok = {}  
        self.host_unreachable = {}  
        self.host_failed = {}  

    def v2_runner_on_unreachable(self, result):  
        self.host_unreachable[result._host.get_name()] = result  

    def v2_runner_on_ok(self, result,  *args, **kwargs):  
        self.host_ok[result._host.get_name()] = result  

    def v2_runner_on_failed(self, result,  *args, **kwargs):  
        self.host_failed[result._host.get_name()] = result


def run_order(hosts, module_name, module_args):
    variable_manager = VariableManager()
    loader = DataLoader()
    print "#"*10
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=[hosts]) 
    print '#'*10
    Options = namedtuple('Options',
                        ['listtags', 
                        'listtasks', 
                        'listhosts', 
                        'syntax', 
                        'connection',
                        'module_path', 
                        'forks',
                        'remote_user',
                        'private_key_file', 
                        'ssh_common_args',
                        'ssh_extra_args',
                        'sftp_extra_args', 
                        'scp_extra_args', 
                        'become', 
                        'become_method', 
                        'become_user', 
                        'verbosity', 
                        'check'])
    options = Options(
                    listtags=False, 
                    listtasks=False,
                    listhosts=False, 
                    syntax=False, 
                    connection='ssh', 
                    module_path=None, 
                    forks=100, 
                    remote_user='letv', 
                    private_key_file=None, 
                    ssh_common_args=None, 
                    ssh_extra_args=None, 
                    sftp_extra_args=None, 
                    scp_extra_args=None, 
                    become=True, 
                    become_method='sudo', 
                    become_user='root',
                    verbosity=None, 
                    check=False)
    
    passwords = dict(become_pass='leshiVM1404')
    play_source = dict(
                    name="test ansible tasks",
                    hosts='all',
                    gather_facts='no',
                    become=True,
                    become_user='root',
                    become_method='sudo', 
                    #modify_user='andabse',
                    tasks=[
                        dict(action=dict(module=module_name, args=module_args)),
                        #dict(action=dict(module='command', args='id'))
                    ]
                    )
    print json.dumps(play_source,indent=4)
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    tqm = None
    callback = ResultCallback()
    try:
        tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                options=options,
                passwords=passwords,
                stdout_callback=callback,
                run_additional_callbacks=C.DEFAULT_LOAD_CALLBACK_PLUGINS,
                run_tree=False,
                )
        
        result = tqm.run(play)
        print result
    finally:
        if tqm is not None:
            tqm.cleanup()
            
    results_raw = {}
    results_raw['success'] = {}
    results_raw['failed'] = {}
    results_raw['unreachable'] = {}

    for host, result in callback.host_ok.items(): 
        results_raw['success'][host] = result._result
  
    for host, result in callback.host_failed.items():
        results_raw['failed'][host] = result._result['msg']  
  
    for host, result in callback.host_unreachable.items():
        results_raw['unreachable'][host]= result._result['msg']  
    
    return results_raw
    

def run_playbook(hosts,playbook,extra_vars={}):
    loader = DataLoader()
    variable_manager = VariableManager()
    variable_manager.extra_vars=extra_vars
    inventory = Inventory(loader=loader, variable_manager=variable_manager,host_list=[hosts])
    variable_manager.extra_vars=extra_vars
    variable_manager.set_inventory(inventory)
    passwords = dict(become_pass='leshiVM1404')
    print inventory
    Options = namedtuple('Options',
                         ['connection',
                          'forks', 
                          'remote_user',
                          'ack_pass', 
                          'sudo_user',
                          'sudo',
                          'ask_sudo_pass',
                          'verbosity',
                          'module_path', 
                          'become', 
                          'become_method', 
                          'become_user', 
                          'check',
                          'listhosts', 
                          'listtasks', 
                          'listtags',
                          'syntax',
                          ])
    options = Options(connection='smart', 
                           forks=100,
                           remote_user='letv',
                           ack_pass=None,
                           sudo_user='root',
                           sudo='yes',
                           ask_sudo_pass=True,
                           verbosity=5,
                           module_path=None,  
                           become=True, 
                           become_method='sudo', 
                           become_user='root', 
                           check=None,
                           listhosts=None,
                           listtasks=None, 
                           listtags=None, 
                           syntax=None
                      )
    playbook = PlaybookExecutor(playbooks=[playbook,],inventory=inventory,
                  variable_manager=variable_manager,
                  loader=loader,options=options,passwords=passwords)
                  
    result = playbook.run()
    print result

def run_order_inventory_file(hosts, module_name, module_args):
    variable_manager = VariableManager()
    loader = DataLoader()
    print "#"*10
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=hosts) 
    print '#'*10
    Options = namedtuple('Options',
                        ['listtags', 
                        'listtasks', 
                        'listhosts', 
                        'syntax', 
                        'connection',
                        'module_path', 
                        'forks',
                        'remote_user',
                        'private_key_file', 
                        'ssh_common_args',
                        'ssh_extra_args',
                        'sftp_extra_args', 
                        'scp_extra_args', 
                        'become', 
                        'become_method', 
                        'become_user', 
                        'verbosity', 
                        'check'])
    options = Options(
                    listtags=False, 
                    listtasks=False,
                    listhosts=False, 
                    syntax=False, 
                    connection='ssh', 
                    module_path=None, 
                    forks=100, 
                    remote_user='letv', 
                    private_key_file=None, 
                    ssh_common_args=None, 
                    ssh_extra_args=None, 
                    sftp_extra_args=None, 
                    scp_extra_args=None, 
                    become=True, 
                    become_method='sudo', 
                    become_user='root',
                    verbosity=None, 
                    check=False)
    
    passwords = dict(become_pass='leshiVM1404')
    play_source = dict(
                    name="test ansible tasks",
                    hosts='all',
                    gather_facts='no',
                    become=True,
                    become_user='root',
                    become_method='sudo', 
                    #modify_user='andabse',
                    tasks=[
                        dict(action=dict(module=module_name, args=module_args)),
                        #dict(action=dict(module='command', args='id'))
                    ]
                    )
    print json.dumps(play_source,indent=4)
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    tqm = None
    callback = ResultCallback()
    try:
        tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                options=options,
                passwords=passwords,
                stdout_callback=callback,
                run_additional_callbacks=C.DEFAULT_LOAD_CALLBACK_PLUGINS,
                run_tree=False,
                )
        
        result = tqm.run(play)
        print result
    finally:
        if tqm is not None:
            tqm.cleanup()
            
    results_raw = {}
    results_raw['success'] = {}
    results_raw['failed'] = {}
    results_raw['unreachable'] = {}

    for host, result in callback.host_ok.items(): 
        results_raw['success'][host] = result._result
  
    for host, result in callback.host_failed.items():
        results_raw['failed'][host] = result._result['msg']  
  
    for host, result in callback.host_unreachable.items():
        results_raw['unreachable'][host]= result._result['msg']  
    
    return results_raw

if __name__=='__main__':    
   ip=sys.argv[1] 
   run_playbook(ip,"/letv/scripts/ansible/restartvnc/restartvnc.yml",)

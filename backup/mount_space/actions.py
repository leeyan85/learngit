#!/usr/bin/python
import paramiko
from paramiko import SSHClient, AutoAddPolicy
from threading import Thread
from Queue import Queue
#from configparser import ConfigParser
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import ntpath
import re


current_dir = ntpath.dirname(os.path.abspath(__file__))
current_module = sys.modules[__name__]

target_servers_queue = Queue()
umount_servers_queue = Queue()
mounted_servers_queue = Queue()

servers_with_output_queue = Queue()
servers_with_stdout = {}
servers_with_stderr = {}
servers_with_error = {}
servers_without_output = []
#Nfs_serverip='10.148.16.47'

class Server:

    def __init__(self, server, username=None, password=None, port=22, group=None, type=None):
        self.server = server
        self.username = username
        self.password = password
        self.port = 22
        self.group = group
        self.type = type
        self.remote_stderr = None
        self.remote_stdout = None
        self.key=paramiko.RSAKey.from_private_key_file('/home/letv/.ssh/id_rsa')

    def connect(self):
        #try:
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.server, self.port, self.username, pkey=self.key, timeout=20)
        #except Exception as X:
        #    send_mail('Got Error While Executing %s' % ' '.join(sys.argv), '%s: %s' % (self.server, str(X)))

    def exec_remote_command(self):
        stdin, stdout, stderr = self.ssh.exec_command(self.remote_command)
        self.remote_stderr = stderr.read()
        self.remote_stdout = stdout.read()

    def disconnect(self):
        self.ssh.close()


    
def create_nfs_directory(ips,Nfs_serverip):
    server_ips=ips.split(',')
    Nfs_serverip=Nfs_serverip
    Nfs_username='root'
    Nfs_server=Server(Nfs_serverip,Nfs_username)
    Nfs_server.connect()
    Nfs_server.remote_command='cd /root; > ip'
    Nfs_server.exec_remote_command()
    for ip in server_ips:
        Nfs_server.remote_command='cd /root;echo %s >> ip' %ip
        Nfs_server.exec_remote_command()
    Nfs_server.remote_command='cd /root;bash add.sh'
    Nfs_server.exec_remote_command()
    Nfs_server.disconnect()

    
    
def enqueue_servers_output(server, remote_stdout=None, remote_stderr=None, error=None):
    servers_with_output_queue.put({server: {'stdout': remote_stdout, 'stderr': remote_stderr, 'error': error}})    


def remote_mount_space(queue_name,Nfs_serverip):
    Nfs_directory_prefix='vm-'
    while True:
        try:
            serverip = queue_name.get()
            server_instance = Server(serverip, username='letv')
            Nfs_directory=Nfs_directory_prefix+serverip.replace('.','-')
            mount_point='/le_data'
            group='andbase'
            owner='andbase'
            server_instance.remote_command='sudo mkdir -p %s;sudo mount %s:/data/%s %s;sudo chmod 777 %s;sudo chown -R %s:%s %s;df -h;sudo chmod 777 /etc/rc.local;echo source /etc/environment >> /etc/rc.local; echo sudo /bin/mount %s:/data/%s %s >> /etc/rc.local;sudo chmod 755 /etc/rc.local;sudo chmod 777 /etc/profile; echo sudo /bin/mount %s:/data/%s %s >> /etc/profile;sudo chmod 644 /etc/profile;' %(mount_point,Nfs_serverip,Nfs_directory,mount_point,mount_point,owner,group,mount_point,Nfs_serverip,Nfs_directory,mount_point,Nfs_serverip,Nfs_directory,mount_point)
            print server_instance.remote_command
            server_instance.connect()
            server_instance.exec_remote_command()
            enqueue_servers_output(server_instance.server, remote_stdout=server_instance.remote_stdout, remote_stderr=server_instance.remote_stderr)
        except Exception:
            error = str(sys.exc_info()[:2])
            enqueue_servers_output(serverip, error=(error.encode()))
        finally:
            queue_name.task_done()
        server_instance.disconnect()

def remote_mount_space2(queue_name):
    Nfs_directory_prefix='vm-'
    while True:
        try:
            serverip = queue_name.get()
            server_instance = Server(serverip, username='letv')
            Nfs_directory=Nfs_directory_prefix+serverip.replace('.','-')
            mount_point='/le_data'
            group='andbase'
            owner='andbase'
            server_instance.remote_command='sudo chmod 777 /etc/profile; echo sudo /bin/mount %s:/data/%s %s >> /etc/profile;sudo chmod 644 /etc/profile' %(Nfs_serverip,Nfs_directory,mount_point)
            print server_instance.remote_command
            server_instance.connect()
            server_instance.exec_remote_command()
            enqueue_servers_output(server_instance.server, remote_stdout=server_instance.remote_stdout, remote_stderr=server_instance.remote_stderr)
        except Exception:
            error = str(sys.exc_info()[:2])
            enqueue_servers_output(serverip, error=(error.encode()))
        finally:
            queue_name.task_done()
        server_instance.disconnect()

def generate_servers_queue(ips):#
    server_count = 0
    for server in ips:
        server_count += 1
        target_servers_queue.put(server)
    return server_count



def get_servers_with_output():
    while True:
        server_with_output = servers_with_output_queue.get()
        for server, remote_result in server_with_output.items():
            remote_stdout = remote_result['stdout']
            remote_stderr = remote_result['stderr']
            remote_error = remote_result['error']
            if remote_stdout:
                servers_with_stdout.update({server: remote_stdout})
            if remote_stderr:
                servers_with_stderr.update({server: remote_stderr}) 
            if remote_error:
                servers_with_error.update({server: remote_error})
            if not remote_stdout and not remote_stderr:
                servers_without_output.append(server)
        servers_with_output_queue.task_done()


def get_output_options(output_options):
    output_way = output_options.get('output_way')
    output_file = output_options.get('output_file')
    text_output_way = ['stdout', 'file']
    html_output_way = ['mail']
    if output_way in text_output_way:
        output_format = 'text'
    elif output_way in html_output_way:
        output_format = 'html'
    return output_way, output_file, output_format


def generate_output_report(server_output, format):
    if server_output:
        content = ''
        if isinstance(server_output, dict):
            for server in sorted(server_output):
                output = server_output[server]
                content += '%s:\n%s\n%s\n' % (server, output.decode().rstrip(), '-'*50)
        elif isinstance(server_output, list):
            content += '\n'.join(sorted(server_output)) + '\n'
        if format == 'text':
            return content
        elif format == 'html':
            return content.replace('\n', '<br>').replace(' ', '&nbsp')
        
def generate_header(header_char, header_char_count, header_string, format):
    header_border = header_char * header_char_count
    header_content = '%s%s%s\n' % (header_border, header_string, header_border)
    if format == 'text':
        return header_content
    elif format == 'html':
        return header_content.replace('\n', '<br>').replace(' ', '&nbsp')



def threads_run_mount(queue_name):
    server_count = queue_name.qsize()
    print server_count
    if server_count <= 300:
        thread_number = server_count
    else:
        thread_number = 300
    for i in range(thread_number):
        thread = Thread(target=remote_mount_space, args=(queue_name,))
        thread.setDaemon(True)
        thread.start()
    queue_name.join()
    thread = Thread(target=get_servers_with_output, args=())
    thread.setDaemon(True)
    thread.start()
    servers_with_output_queue.join()
    


def get_result():
    output_options={}
    output_options.update({'output_way': 'stdout'})
    output_options.update({'output_file': '/tmp/output.log'})
    output_options.update({'output_format': 'stdout'})
    output_way, output_file,  output_format = get_output_options(output_options)
    
    if servers_with_stdout:
        content_stdout = generate_header('=', 15, 'server with stdout', output_format) + generate_output_report(servers_with_stdout, output_format)
    else:
        content_stdout = ''
    if servers_with_stderr:
        content_stderr = generate_header('=', 15, 'server with stderr', output_format) + generate_output_report(servers_with_stderr, output_format)
    else:
        content_stderr = ''
        
    if servers_with_error:
        content_error = generate_header('=', 15, 'server with error', output_format) + generate_output_report(servers_with_error, output_format)
    else:
        content_error = ''
        
    content = content_stdout + content_stderr + content_error
    if output_way == 'stdout':
        print(content)


def precheck(queue_name,Nfs_serverip):
    while True:
        try:
            serverip = queue_name.get()
            server_instance=Server(serverip,username='letv')
            server_instance.remote_command='df -h'
            server_instance.connect()
            server_instance.exec_remote_command()
            m=re.search('le_data',server_instance.remote_stdout)
            if m:
               mounted_servers_queue.put(serverip)
            else:
               umount_servers_queue.put(serverip)
        except Exception:
            error = str(sys.exc_info()[:2])
            enqueue_servers_output(serverip, error=(error.encode()))
        finally:
            queue_name.task_done()
        server_instance.disconnect()


def thread_run(function_name,queue_name,Nfs_serverip):
    thread_number=2
    for i in range(thread_number):
        thread = Thread(target=function_name, args=(queue_name,Nfs_serverip))
        thread.setDaemon(True)
        thread.start()
    queue_name.join()


def aftercheck(ips):
    pass
    


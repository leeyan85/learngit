import json
import sys
sys.path.append('/letv/scripts/ansible/api')
import requests
from requests.auth import HTTPDigestAuth

# AUTHENTICATION TOKEN of Gerrit account
# DON'T MODITFY IT
AUTHENTICATION_TOKEN = {
    'diana': 'BNGmHvjiKRvxsRQhjut0mOf8F2ZNTLgTsP+NN3njPA',
    'athena': 'jlxiBuLQBYjiHKCWM6GDgqyk3bctqdcTqLlHJx+0dg',
    'minerva': 'JTBa4LmQf8L5lQkhppThSrsfMkGcX3r76ycByrbOWA',
    'athena-test': '',
    'diana-test': 'BNGmHvjiKRvxsRQhjut0mOf8F2ZNTLgTsP+NN3njPA'
}

# Path to VM host list
#VM_HOSTS = '/home/andbase/workspace/see/gerrit/staging'
from ansible_api_v2 import run_order
def generate_ssh_keys(vm_ip,username,  local_user='andbase'):
    """Generate ssh keys on remote VM by calling Ansible API
    and Ansible user module.

    Args:
    username: VM user
    vm_ip: VM IP address
    local_user: local user account on VM

    see: http://stackoverflow.com/a/27597987
    reference: http://docs.ansible.com/ansible/user_module.html
    """
    module_name='user'
    module_args="name=%s generate_ssh_key=yes ssh_key_comment='%s@%s'" %(local_user, username, vm_ip)
    print vm_ip,module_name,module_args
    ssh_keys_result = run_order(vm_ip,module_name,module_args)
    return str(ssh_keys_result['success'][vm_ip]['ssh_public_key']) 

def get_ssh_keys(gerrit, username):
    """
    Get user's all ssh public keys by Gerrit REST API
    """
    res = requests.get(
        'http://%s.devops.letv.com/a/accounts/%s/sshkeys' % (gerrit, username),
        headers={'Content-Type': 'application/json; charset=UTF-8'},
        auth=HTTPDigestAuth('robotam', AUTHENTICATION_TOKEN[gerrit]))
    # Remove magic prefix before parse json
    ssh_keys = [(r['seq'], r['ssh_public_key'], r['comment'])
                for r in json.loads(res.text[5:]) if r['valid']]
    return ssh_keys


def add_ssh_key(gerrit, username, key):
    """
    Add a new ssh public key by Gerrit REST API
    """
    r = requests.post(
        'http://%s.devops.letv.com/a/accounts/%s/sshkeys' % (gerrit, username),
        headers={'Content-Type': 'plain/text'},
        data=key,
        auth=HTTPDigestAuth('robotam', AUTHENTICATION_TOKEN[gerrit]))
    print r.text
    return r.status_code == 201


def delete_ssh_keys(gerrit, username, ssh_key_comment):
    """
    Delete the ssh key with the given ssh_key_comment
    """
    all_ssh_keys = get_ssh_keys(gerrit, username)
    deleted_key = filter(lambda key: key[2] == ssh_key_comment,
                         all_ssh_keys).pop()
    r = requests.delete(
        'http://%s.devops.letv.com/a/accounts/%s/sshkeys/%i' %
        (gerrit, username, deleted_key[0]),
        auth=HTTPDigestAuth('robotam', AUTHENTICATION_TOKEN[gerrit]))
    return r.status_code == 204

if __name__ == '__main__':
    ip=sys.argv[1]
    user=sys.argv[2]
    key = generate_ssh_keys(ip,user )
    print key
    #add_ssh_key('diana', user, key)
    print add_ssh_key('minerva',user,key)
    print add_ssh_key('athena',user,key)

import os
import paramiko
import requests
import json
from datetime import datetime, timezone, timedelta

def ssh_multiple_connections(hosts_info, command):
    users = []
    hostnames = []
    commandps = 'pgrep -x node | wc -l'
    commandpm2 = '~/.npm-global/bin/pm2 resurrect'
    for host_info in hosts_info:
        hostname = host_info['hostname']
        username = host_info['username']
        password = host_info['password']
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=hostname, port=22, username=username, password=password)
            stdin, stdout, stderr = ssh.exec_command(commandps)
            output = stdout.read().decode().strip()
            if output ==  '0':
                stdin, stdout, stderr = ssh.exec_command(commandpm2)
                err = stderr.read().decode().strip()
                if err:
                    print(f'start pm2 thread:{err}')
                else:
                    print(f'start pm2 thread successful')
            else:
                print('pm2 thread is running')
            stdin, stdout, stderr = ssh.exec_command(command)
            user = stdout.read().decode().strip()
            users.append(user)
            hostnames.append(hostname)
            
        except Exception as e:
            print(f"用户：{username}，连接 {hostname} 时出错: {str(e)}")
        finally:
            ssh.close()
    return users, hostnames

ssh_info_str = os.getenv('SSH_INFO', '[]')
hosts_info = json.loads(ssh_info_str)

command = 'whoami'
user_list, hostname_list = ssh_multiple_connections(hosts_info, command)
user_num = len(user_list)
content = "SSH服务器登录信息：\n"
for user, hostname in zip(user_list, hostname_list):
    content += f"用户名：{user}，服务器：{hostname}\n"
beijing_timezone = timezone(timedelta(hours=8))
time = datetime.now(beijing_timezone).strftime('%Y-%m-%d %H:%M:%S')

loginip = requests.get('https://api.ipify.org?format=json').json()['ip']
content += f"本次登录用户共： {user_num} 个\n登录时间：{time}\n登录IP：{loginip}"
print(content)



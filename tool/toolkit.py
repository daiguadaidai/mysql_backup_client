# -*- coding: utf-8 -*-

import os
import sys
path = os.path.split(os.path.realpath(sys.argv[0]))[0]
sys.path.append("{path}/..".format(path=path))

import socket
import struct
import subprocess
from tool_log import ToolLog
from tool_ssh import ToolSSH

class Toolkit(object):
    """这是以个工具类
    """
    # 类方法, 命令的前缀. 在每个名前都要添加这一个前缀
    CMD_PREFIX = 'source ~/.bash_profile && '

    def __init__(self):
       pass

    @classmethod
    def num2ip(self, num):
        """将一个10位数转化成一个IP
        Args:
            num: 一个整数
        Return:
            返回一个 字符串 IP
            如: 10.10.10.11
        Raise: None
        """

        return socket.inet_ntoa(struct.pack('I', socket.htonl(num)))

    @classmethod
    def ip2num(self, ip):
        """将一个IP转化为整数
        Args:
            ip: 一个ip: 10.10.10.11
        Return: 
            返回一个 Long 类型的数字
            如: 123456789
        Raise: None
        """

        return socket.ntohl(struct.unpack('I', socket.inet_aton(str(ip)))[0])

    @classmethod
    def md5_for_file(self, file_name):
        """计算文件的md5值
        通过获得文件的路径和文件名, 执行操作系统命令获得文件的md5值
        
        Args:
            file_name: 文件的路径和名称
        Return: 
            str(md5) 返回一个md5值
        Raise: None
        """
        # 构造并执行操作系统命令:
        # md5sum xxx.sql
        cmd = "md5sum {file_name}".format(
                                   file_name = file_name)

        # 执行命令返回结果
        is_ok, stdout, stderr = self.exec_cmd_get_info(cmd)

        if not is_ok:
            return None
        else:
            return stdout.split()[0]

    @classmethod
    def md5_for_file_remote(self, host='127.0.0.1', username=None, 
                                  password=None, file_name=None):
        """计算文件的md5值
        通过获得文件的路径和文件名, 执行操作系统命令获得文件的md5值
        
        Args:
            file_name: 文件的路径和名称
        Return: 
            str(md5) 返回一个md5值
        Raise: None
        """
        # 构造并执行操作系统命令:
        # md5sum xxx.sql
        cmd = "md5sum {file_name}".format(
                                   file_name = file_name)

        # 执行命令返回结果
        is_ok, stdout, stderr = ToolSSH.ssh_exec_cmd(cmd,
                                                     host,
                                                     username,
                                                     password)
        if not is_ok:
            return None
        else:
            return stdout[0].split()[0]

    @classmethod
    def get_file_size(self, file_name):
        """获得文件的大小
        通过获得文件的路径和文件名, 获得文件的大小
        
        Args:
            file_name: 文件的路径和名称
        Return: 
            int/long 返回一个文件大小 (单位 Byte)
        Raise: None
        """
        if not os.path.exists(file_name):
            return 0
            
        if os.path.isfile(file_name):
            return os.path.getsize(file_name)
            
        size = 0    
        for root, dirs, files in os.walk(file_name):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])  
        return size

    @classmethod
    def exec_cmd(self, cmd):
        """执行命令
        执行通过给与的命令
        
        Args:
            cmd: 需要执行的操作系统命令
        Return: 
            True/False 返回这个命令是否执行成功了
        Raise: None
        """
        cmd = '{prefix} {cmd}'.format(
              prefix = self.CMD_PREFIX,
              cmd = cmd)
        
        ToolLog.log_info(cmd)
        child = subprocess.Popen(cmd, 
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        child.wait()
        err_code = child.poll()
        stdout = child.stdout.read()
        stderr = child.stderr.read()
        
        if err_code != 0:
            ToolLog.log_error(stdout)
            ToolLog.log_error(stderr)
            return False
        else:
            ToolLog.log_info(stdout)
            ToolLog.log_info(stderr)
            return True

    @classmethod
    def exec_cmd_get_info(self, cmd):
        """执行命令并获得返回的值
        执行通过给与的命令
        
        Args:
            cmd: 需要执行的操作系统命令
        Return: 
            True/False, stdout, stderr
            返回是否执行成功, 已经相关输出
        Raise: None
        """
        cmd = '{prefix} {cmd}'.format(
              prefix = self.CMD_PREFIX,
              cmd = cmd)
        child = subprocess.Popen(cmd, 
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        child.wait()
        err_code = child.poll()
        stdout = child.stdout.read()
        stderr = child.stderr.read()
        
        if err_code != 0:
            ToolLog.log_error(cmd)
            ToolLog.log_error(stdout)
            ToolLog.log_error(stderr)
            return False, stdout, stderr
        else:
            ToolLog.log_info(cmd)
            ToolLog.log_info(stdout)
            ToolLog.log_info(stderr)
            return True, stdout, stderr

    @classmethod
    def send_mail(self, msg=''):
        pass


def main():
    print Toolkit.CMD_PREFIX


if __name__ == '__main__':
    main()

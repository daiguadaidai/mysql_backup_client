# -*- coding: utf-8 -*-

# 导入项目路径
import os
import sys
path = os.path.split(os.path.realpath(sys.argv[0]))[0]
home = "{path}/..".format(path=path)
sys.path.append(home)

# import subprocess 
# from model.models import *
from tool.toolkit import Toolkit
from tool.tool_log import ToolLog
from tool.tool_compress import ToolCompress
from tool.tool_ssh import ToolSSH


class BackupBase(object):
    """备份的父类
    此类中定义了备份中需要使用的一些方法:
    function:
        backup_data: 用于执行命令
        valid: 用于验证备份在 (本地) 是否可用
        valid_remode: 用于验证备份在 (远程) 是否可用
        compress: 压缩备份文件
        send_backup: 将备份发送到远程
        back_binlog: 备份binlog文件
        send_binlog: 将binlog文件发送到远端
        checksum: 对 (本地) 备份集进行chechsum
        checksum_remote: 对 (远程) 备份集进行chechsum
        backup_size: 获得备份文件的大小
    """

    def __init__(self, name, dir):
        """构造方法
        Attribute:
            _name: 备份集的名称
            _dir: 备份集存放的路径
            _backup_file: 完整的备份文件路径
            _compress_file: 压缩后的备份文件路径和名称
            _remote_backup_file: 在远程备份文件的路径和名称
            _md5sum: 备份文件或压缩备份文件的 md5 值
            _remote_md5sum: 远程备份文件或压缩备份文件的 md5 值
            _binlog_dir: 本地binlog生成目录
            _backup_binlog_dir: 本地备份binlog目录
            _remote_binlog_dir: 远程binlog目录
        """
        self._name = name
        self._dir = dir
        self._backup_file = '{dir}/{name}'.format(
            dir = self._dir,
            name = self._name,
        )
        self._compress_file = None
        self._md5sum = None
        self._remote_md5sum = None
        self._backup_file_size = None
        self._remote_backup_file = None
        self._binlog_dir = None
        self._backup_binlog_dir = None

    def backup_data(self, cmd):
        """执行备份
        将给与的命令在操作系统上运行
        
        Args:
            cmd: 需要执行的命令
        Return:
            True/False 返回命令执行成功还是失败
        """

        is_ok = Toolkit.exec_cmd(cmd)

        return is_ok

    def backup_binlog(self, from_dir=None, to_dir=None, cmin=86400):
        """备份 BINLOG
        根据时间所给的时间和目录来备份binllog
 
        Args:
            from_dir: binlog生成
            to_dir: binlog备份存放
            cmin: 备份几分钟前的binlog (默认86400分钟/24小时)
        return:
            True/False 备份是否成功
        Raise: None
        """
        # 判断复制给实例的binlog原路径和备份路劲
        if from_dir:
            self.binlog_dir = from_dir
        if to_dir:
            self.backup_binlog_dir = to_dir

        # binlog相关路径记录日志
        ToolLog.log_info('binlog dir: {dir}'.format(dir = self.binlog_dir))
        ToolLog.log_info('binlog backup dir: {dir}'.format(
                                             dir = self.backup_binlog_dir))

        is_ok = False
        if self.binlog_dir and self.backup_binlog_dir:
            cmd = (
                'mkdir -p {to_dir} && '
                'find {from_dir} -maxdepth 1 -cmin -{cmin} -print | '
                'sed "1d" | xargs -i cp -r {brace} {to_dir}'.format(
                    to_dir = self.backup_binlog_dir,
                    from_dir = self.binlog_dir,
                    cmin = cmin,
                    brace = '{}'
                )
            )
             
            is_ok = Toolkit.exec_cmd(cmd)
        return is_ok

    def valid(self):
        print 'valiting backup set'

    def valid_remode(self, host, user, password, dir):
        print 'valiting backup set remote ...'

    def compress(self, compress_type='gzip', file_type='file'):
        """压缩文件
        根据给定的压缩类型对文件进行压缩
        Args:
            type: 需要压缩的文件类型
        Return:
            compress_file_name 返回一个压缩的文件路径和名称
        """
        is_ok = False
        if compress_type == 'gzip': # gzip压缩
            is_ok, self.compress_file, cmd = ToolCompress.targz(
                self.backup_file, 
                from_file_type = file_type
            )
        elif compress_type == 'bzip2':# bzip2压缩
            is_ok, self.compress_file, cmd = ToolCompress.tarbz2(
                self.backup_file, 
                from_file_type = file_type
            )
        elif compress_type == 'zip':# zip压缩
            is_ok, self.compress_file, cmd = ToolCompress.ziper(
                self.backup_file, 
                from_file_type = file_type
            )
        elif compress_type == 'xz':# xz压缩
            is_ok, self.compress_file, cmd = ToolCompress.tarxz(
                self.backup_file, 
                from_file_type = file_type
            )
        elif compress_type == 'lzma':# lzma压缩
            is_ok, self.compress_file, cmd = ToolCompress.tarlzma(
                self.backup_file, 
                from_file_type = file_type
            )
        else: # 默认 gzip 压缩
            is_ok, self.compress_file, cmd = ToolCompress.tar(
                self.backup_file, 
                from_file_type = file_type
            )

        return is_ok

    def send_backup(self, host='127.0.0.1', username='', 
                          password='', remote_file=None):
        """将备份文件传输到远程
        将备份文件传输到远程文件

        Args:
            host: IP
            username: 远程OS用户名
            password: 对应user密码
            remote_file: 传输到远程的备份文件名称
        Return:
            True/False, remote_backup_file 
            代表传输是否成功, 和远程备份文件名称
        Raise: None
        """
        is_ok = False
        
        # 判断是要传输什么文件到远程
        local_file = None
        if self.compress_file:
            local_file = self.compress_file
        elif self.backup_file:
            local_file = self.backup_file

        if not local_file:
            return is_ok

        # 传输文件
        if remote_file:
            is_ok = ToolSSH.ssh_trans(host = host,
                                      username = username, 
                                      password = password,
                                      local_file = local_file,
                                      remote_file = remote_file)
        elif self.remote_backup_file:
            is_ok = ToolSSH.ssh_trans(host = host,
                                      username = username,
                                      password = password,
                                      local_file = local_file,
                                      remote_file = self.remote_backup_file)

        if is_ok:
            self.remote_backup_file = remote_file

        return is_ok, self.remote_backup_file

    def send_binlog(self, host, username, password, remote_dir=None):
        """将binlog备份文件传输到远程
        将binlog备份文件传输到远程文件

        Args:
            host: IP
            username: 远程OS用户名
            password: 对应user密码
            remote_dir: 传输到远程的目录
        Return:
            True/False, remote_binlog_dir 
            代表传输是否成功, 和远程备份文件名称
        Raise: None
        """
        # 设置实例变量remote_binlog_dir
        if remote_dir:
            self.remote_binlog_dir = remote_dir
        
        ToolLog.log_info('remote binlog dir: {dir}'.format(
                                     dir = self.remote_binlog_dir))

        is_ok = False
        # 如果有设置远程的binlog备份目录
        if self.remote_binlog_dir and self.backup_binlog_dir:
            is_ok = ToolSSH.ssh_trans(host,
                                      username,
                                      password,
                                      self.backup_binlog_dir,
                                      self.remote_binlog_dir)
        else:
            ToolLog.log_error('remote binlog dir: {dir}'.format(
                                         dir = self.remote_binlog_dir))
            ToolLog.log_error('local backup binlog dir: {dir}'.format(
                                         dir = self.backup_binlog_dir))


        return is_ok, self.remote_binlog_dir

    def checksum(self, file=None):
        """给备份文件做checksum
        给备份完的文件做一个checksum. 如果备份文件压缩了, 则是checksum压缩文件
        Args: None
        Return:
            str 返回一个字符串, 该字符串是文件的checksum值
        Raise: None
        """
        if file:
            self.md5sum = Toolkit.md5_for_file(file)
        elif self.compress_file:
            self.md5sum = Toolkit.md5_for_file(self.compress_file)
        elif self.backup_file:
            self.md5sum = Toolkit.md5_for_file(self.backup_file)

        return self.md5sum

    def checksum_remote(self, host = '127.0.0.1', username = '',
                              password = '', file_name = None):
        """对远程文件进行checksum
        对远程文件进行md5sum并放回md5 值,已经执行远程命令的输出
        Args:
            host: ip
            username: 远程OS用户名
            password: 远程OS密码
            file: 需要进行checksum的文件
        Return
            md5(str) 返回一个md5值或者 None
        Raise: None
        """
        # 构造执行shell命令
        if file_name:
            self.remote_md5sum = Toolkit.md5_for_file_remote(
                                 host = host,
                                 username = username,
                                 password = password,
                                 file_name = file_name)
        elif self.remote_backup_file:
            self.remote_md5sum = Toolkit.md5_for_file_remote(
                                 host = host,
                                 username = username,
                                 password = password,
                                 file_name = self.remote_backup_file)

        return self.remote_md5sum

    def backup_size(self, file=None):
        """计算备份文件的大小
        通过文件路径和名称, 获得该文件的大小. 如果有压缩的备份文件,
        则计算压缩的备份文件
        Args: None
        Return:
            str 返回一个字符串, 表示了文件的大小(单位 byte)
        Raise: None
        """
        if file:
            self.backup_file_size = Toolkit.get_file_size(file)
        elif self.compress_file:
            self.backup_file_size = Toolkit.get_file_size(self.compress_file)
        elif self.backup_file:
            self.backup_file_size = Toolkit.get_file_size(self.backup_file)

        return self.backup_file_size

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
    
    @property
    def dir(self):
        return self._dir
    
    @dir.setter
    def dir(self):
        self._dir = dir
    
    @property
    def backup_file(self):
        return self._backup_file
    
    @backup_file.setter
    def backup_file(self, backup_file):
        self._backup_file = backup_file
    
    @property
    def compress_file(self):
        return self._compress_file
    
    @compress_file.setter
    def compress_file(self, compress_file):
        self._compress_file = compress_file
    
    @property
    def md5sum(self):
        return self._md5sum
    
    @md5sum.setter
    def md5sum(self, md5sum):
        self._md5sum = md5sum
    
    @property
    def remote_md5sum(self):
        return self._remote_md5sum
    
    @remote_md5sum.setter
    def remote_md5sum(self, remote_md5sum):
        self._remote_md5sum = remote_md5sum
    
    @property
    def backup_file_size(self):
        return self._backup_file_size
    
    @backup_file_size.setter
    def backup_file_size(self, backup_file_size):
        self._backup_file_size = backup_file_size
    
    @property
    def remote_backup_file(self):
        return self._remote_backup_file
    
    @remote_backup_file.setter
    def remote_backup_file(self, remote_backup_file):
        self._remote_backup_file = remote_backup_file
    
    @property
    def binlog_dir(self):
        return self._binlog_dir
    
    @binlog_dir.setter
    def binlog_dir(self, binlog_dir):
        self._binlog_dir = binlog_dir
    
    @property
    def backup_binlog_dir(self):
        return self._backup_binlog_dir
    
    @backup_binlog_dir.setter
    def backup_binlog_dir(self, backup_binlog_dir):
        self._backup_binlog_dir = backup_binlog_dir

def main():
    backup_base = BackupBase('mysqldump_1.sql', '/tmp')
    args = '--quick --single-transaction --all-databases'

    cmd = (
        'mysqldump -uHH -poracle -h192.168.1.233 -P3306'
        ' {args} > {dir}/{name}'.format(args = args,
                                        dir = '/tmp',
                                        name = 'mysqldump_1.sql')
    )


    print backup_base.backup_data(cmd)
    print backup_base.checksum()
    print backup_base.backup_size()
    print backup_base.compress()
    print backup_base.checksum()
    print backup_base.backup_size()
    print backup_base.send_backup('127.0.0.1', 'root', 'oracle', '/u01/backup/mysqldump_1.sql.tar.lzma')
    print backup_base.checksum_remote('127.0.0.1', 'root', 'oracle', '/u01/backup/mysqldump_1.sql.tar.lzma')
    print backup_base.backup_binlog(from_dir = '/root',
                                    to_dir = '/u01/backup/binlog',
                                    cmin = 86400)
    print backup_base.send_binlog('127.0.0.1', 'root', 'oracle', '/u02/backup/binlog')


if __name__ == '__main__':
    main()

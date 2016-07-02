# -*- coding: utf-8 -*-

# 导入项目路径
import os
import sys
path = os.path.split(os.path.realpath(sys.argv[0]))[0]
home = "{path}/..".format(path=path)
sys.path.append(home)

import time
from backup_base import BackupBase
from tool.tool_log import ToolLog
from tool.toolkit import Toolkit

class Xtrabackup(BackupBase):
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
        backup_binlog: 备份binlog日志
        send_binlog: 将binlog日志发送到远程
    """

    def __init__(self, name, dir, backup_bin_file='innobackupex', my_cnf='/etc/my.cnf'):
        """构造方法, 调用父类(BackupBase)的构造方法
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
            _backup_bin_file: 备份使用的 命令所在路径
            _my_cnf: 本地的源 my.cnf
            _backup_mycnf_file: 备份的 my.cnf
        """
        super(Xtrabackup, self).__init__(name, dir)
        self._backup_bin_file = backup_bin_file
        self._my_cnf = my_cnf
        self._backup_mycnf_file = None

    def backup_data(self, username='', password='', host='127.0.0.1',
                          port=3306, param=''):
        """执行备份
        将给与的命令在操作系统上运行
        
        Args:
            username: 链接MySQL的username信息
            password: 链接MySQL的password信息
            host: 链接MySQL的host信息
            port: 链接MySQL的端口信息
            param: mysqldump 需要的额外参数
        Return:
            True/False 返回命令执行成功还是失败
        """
        cmd = (
            '{backup_bin_file} --defaults-file={my_cnf} '
            '--user={username} --password={password} '
            '--host={host} --port={port} {dir} --no-timestamp '
            '{param} >> {output_log_file} 2>&1'.format(
                                     backup_bin_file = self.backup_bin_file,
                                     my_cnf = self.my_cnf,
                                     username = username,
                                     password = password,
                                     host = host,
                                     port = port,
                                     dir = super(Xtrabackup, self).backup_file,
                                     param = param,
                                     output_log_file = ToolLog.filename)
        )
        is_ok = super(Xtrabackup, self).backup_data(cmd)
         
        return is_ok

    def backup_mycnf(self, backup_mycnf_file=None):
        """备份MySQL配置文件
        通过传入的my.cnf备份位置, 执行操作系统cp命令实现备份.

        Args:
            backup_mycnf_file: MySQL配置文件备份路径
        Return: 
            True/False 返回是否备份成功
        Raise: None
        """
        # 先将备份 my.cnf路径进行赋值给backup_mycnf_file
        if backup_mycnf_file:
            self.backup_mycnf_file = backup_mycnf_file
        else:
            self.backup_mycnf_file = '{backup_dir}/my.cnf'.format(
                       backup_dir = super(Xtrabackup, self).backup_file)

        is_ok = False
        # 构造 cp 备份命令
        cmd = 'cp {my_cnf} {backup_mycnf_file}'.format(
                             my_cnf = self.my_cnf,
                             backup_mycnf_file = self.backup_mycnf_file)
        is_ok = Toolkit.exec_cmd(cmd)

        return is_ok

    def valid(self, host = '127.0.0.1', username = '', password = ''):
        """验证备份集是否正确
        通过比较本地的备份和传输到远程备份的md5值来判断是否正确,
        如果没有传输到远程的文件则无法校验是否正确.

        Args:
            host: 需要对远程md5的host
            username: 远程用户名
            password: 远程密码
        """

        msg = ''
        is_ok = False

        # 如果备份没有传输到远程则无法进行校验
        if not super(Xtrabackup, self).remote_backup_file:
            msg = '没有远程备份集'
            return is_ok, msg

        # 构造返回信息
        if super(Xtrabackup, self).compress_file:
            msg = '压缩备份 ({status})'
        elif super(Xtrabackup, self).backup_file:
            msg = '未压缩备份 ({status})'
        else:
            msg = '没有备份集'
            return is_ok, msg

        # 比较本地备份集合远程备份集的md5值是否相等
        if (super(Xtrabackup, self).checksum() ==
            super(Xtrabackup, self).checksum_remote(host = host,
                                            username = username,
                                            password = password)):
            is_ok = True

        if is_ok:
            msg = msg.format(status = '成功')
        else:
            msg = msg.format(status = '失败')
            
        return is_ok, msg
            

    @property
    def backup_bin_file(self):
        return self._backup_bin_file

    @backup_bin_file.setter
    def backup_bin_file(self, backup_bin_file):
        self._backup_bin_file = backup_bin_file

    @property
    def my_cnf(self):
        return self._my_cnf

    @my_cnf.setter
    def my_cnf(self, my_cnf):
        self._my_cnf = my_cnf

    @property
    def backup_mycnf_file(self):
        return self._backup_mycnf_file

    @backup_mycnf_file.setter
    def backup_mycnf_file(self, backup_mycnf_file):
        self._backup_mycnf_file = backup_mycnf_file


def main():
    my_cnf = '/etc/my_3306.cnf'
    param = '--parallel=2'
    backup_bin_file = '/usr/local/percona-xtrabackup/bin/innobackupex'
    backup_name = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    backup_date = time.strftime("%Y-%m-%d", time.localtime())
    backup_dir = '/tmp/backup/{date}'.format(date=backup_date)

    db_conf = {
        'username' : 'HH',
        'password' : 'oracle',
        'host' : '127.0.0.1',
        'port' : 3306
    }

    os_conf = {
        'username' : 'root',
        'password' : 'oracle',
        'host' : '127.0.0.1'
    }

    xtrabackup = Xtrabackup(backup_name, backup_dir, my_cnf=my_cnf)

    remote_dir = '/u01/backup/{backup_date}/{backup_name}'.format(
                                      backup_date = backup_date,
                                      backup_name = backup_name)
    remote_file = '{remote_dir}.tar.gz'.format(remote_dir=remote_dir)
    print '-------------backup data--------------'
    print xtrabackup.backup_data(param = param, **db_conf)
    print '-------------backup mycnf--------------'
    print xtrabackup.backup_mycnf()
    print '-------------send backup--------------'
    print xtrabackup.send_backup(remote_file = remote_dir,
                                 **os_conf)

    print '-------------backup size--------------'
    print xtrabackup.backup_size()
    print '-------------compress backup--------------'
    print xtrabackup.compress(compress_type='gzip', file_type='dir')
    print '-------------backup checksum--------------'
    print xtrabackup.checksum()
    print '-------------backup size--------------'
    print xtrabackup.backup_size()
    print '-------------send backup--------------'
    print xtrabackup.send_backup(
           remote_file = remote_file,
           **os_conf)

    print '-------------checksum remote--------------'
    print xtrabackup.checksum_remote(**os_conf)
    binlog_dir = '{backup_dir}/binlog'.format(backup_dir=xtrabackup.dir)
    print '-------------backup binlog--------------'
    print xtrabackup.backup_binlog(from_dir = '/root',
                                  to_dir = binlog_dir,
                                  cmin = 86400)

    # 设置远程的binlog位置
    remote_binlog_dir = '{remote_dir}/../binlog/'.format(
                                    remote_dir=remote_dir)
    print '-------------send binlog--------------'
    print xtrabackup.send_binlog(remote_dir = remote_binlog_dir,
                                **os_conf)

    print '-------------valid--------------'
    print xtrabackup.valid(**os_conf)


if __name__ == '__main__':
    main()

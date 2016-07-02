# -*- coding: utf-8 -*-

# 导入项目路径
import os
import sys
path = os.path.split(os.path.realpath(sys.argv[0]))[0]
home = "{path}/..".format(path=path)
sys.path.append(home)

from backup_base import BackupBase
from backup_base import BackupBase

class Mysqldump(BackupBase):
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

    def __init__(self, name, dir, backup_bin_file='mysqldump'):
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
        """
        super(Mysqldump, self).__init__(name, dir)
        self._backup_bin_file = backup_bin_file

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
            '{backup_bin_file} -u{username} -p{password} -h{host} -P{port}'
            ' {param} > {dir}/{name}'.format(
                                     backup_bin_file = self.backup_bin_file,
                                     username = username,
                                     password = password,
                                     host = host,
                                     port = port,
                                     param = param,
                                     dir = super(Mysqldump, self).dir,
                                     name = super(Mysqldump, self).name)
        )
        is_ok = super(Mysqldump, self).backup_data(cmd)
         
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
        if not super(Mysqldump, self).remote_backup_file:
            msg = '没有远程备份集'
            return is_ok, msg

        # 构造返回信息
        if super(Mysqldump, self).compress_file:
            msg = '压缩备份 ({status})'
        elif super(Mysqldump, self).backup_file:
            msg = '未压缩备份 ({status})'
        else:
            msg = '没有备份集'
            return is_ok, msg

        # 比较本地备份集合远程备份集的md5值是否相等
        if (super(Mysqldump, self).checksum() ==
            super(Mysqldump, self).checksum_remote(host = host,
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


def main():
    param = '--quick --single-transaction --all-databases'
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

    mysqldump = Mysqldump('mysqldump_2.sql', '/tmp')

    print mysqldump.backup_data(param = param, **db_conf)
    print mysqldump.checksum()
    print mysqldump.send_backup(remote_file = '/u01/backup/mysqldump_2.sql',
                                **os_conf)

    print mysqldump.checksum_remote(**os_conf)
    print mysqldump.backup_size()
    print mysqldump.compress(compress_type='gzip', file_type='file')
    print mysqldump.checksum()
    print mysqldump.backup_size()
    print mysqldump.send_backup(
                    remote_file = '/u01/backup/mysqldump_2.sql.tar.gz',
                    **os_conf)

    print mysqldump.valid(**os_conf)
    print mysqldump.checksum_remote(**os_conf)
    print mysqldump.backup_binlog(from_dir = '/root',
                                  to_dir = '/u01/backup/binlog',
                                  cmin = 86400)

    print mysqldump.send_binlog(remote_dir = '/u02/backup/binlog',
                                **os_conf)


if __name__ == '__main__':
    main()

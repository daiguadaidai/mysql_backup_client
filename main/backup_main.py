# -*- coding: utf-8 -*-

# 导入项目路径
import os
import sys
path = os.path.split(os.path.realpath(sys.argv[0]))[0]
home = "{path}/..".format(path=path)
sys.path.append(home)

from datetime import datetime
from model.models import *
from dao.dao_base import DaoBase
from service.mysqldump import Mysqldump
from service.xtrabackup import Xtrabackup
from tool.tool_log import ToolLog
from tool.toolkit import Toolkit
from tool.tool_ssh import ToolSSH


class BackupMain(object):
    """ 这个类包含了备份的基本逻辑, 和需要的参数
    """
 
    def __init__(self, backup_instance_id=-1):
        # 创建一个 DAO 实例
        self.dao_base = DaoBase()

        # 获得需要备份的 MySQL 实例信息
        self.backup_instance = self.dao_base.get_obj_by_pri(
                                       DbmpMysqlBackupInstance,
                                       backup_instance_id)

        # 获得数据库实例 dbmp_mysql_instance
        self.instance = self.dao_base.get_obj_by_pri(
                                 DbmpMysqlInstance,
                                 DbmpMysqlBackupInstance.mysql_instance_id)

        if not self.backup_instance or not self.backup_instance:
            ToolLog.log_error('cannot find backup instance or MySQL instance')
            Toolkit.send_mail()
            sys.exit(1)
 
        # 获得MySQL instance 额外信息
        self.instance_infos = self.dao_base.get_objs_by_col(
                                 DbmpMysqlInstanceInfo,
                                 DbmpMysqlInstanceInfo.mysql_instance_id,
                                 self.instance.mysql_instance_id)
        self.instance_info = None
        if self.instance_infos:
            self.instance_info = self.instance_infos[0]

        # 指定备份名称(没有指定则使用时间)
        if self.backup_instance.backup_name:
            self.backup_name = self.backup_instance.backup_name

        # 如果指定的是<强制指定实例备份>, 则不需要高可用实例
        if self.backup_instance.backup_type != 1:
            # 通过实例ID获得高可用 MySQL 实例组mysql_ha_group_id
            cols = [DbmpMysqlHaGroupDetail.mysql_ha_group_id]
            ha_instances = self.dao_base.get_objs_by_col(DbmpMysqlHaGroupDetail,
                                        DbmpMysqlHaGroupDetail.mysql_instance_id,
                                        self.backup_instance.mysql_instance_id,
                                        cols = cols)
            ha_instance = None
            if ha_instances:
                ha_instance = ha_instances[0]

            # 通过高可用组ID mysql_ha_group_id获得所有高可用的实例
            self.ha_instances = self.dao_base.get_objs_by_col(DbmpMysqlHaGroupDetail,
                                        DbmpMysqlHaGroupDetail.mysql_ha_group_id,
                                        ha_instance.mysql_ha_group_id)

        self.backup_instance_id = backup_instance_id
        # 定义备份名如果没有填写则按时间
        self.backup_name = None
        if self.backup_instance.backup_name:
            self.backup_name = self.backup_instance.backup_name
        else:
            self.backup_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        self.backup_date = datetime.now().strftime('%Y-%m-%d')

        # 备份目录格式 {指定的目录}/{备份日期}/{实例端口}
        self.backup_dir = '{dir}/{date}/{port}'.format(
                                 dir = self.backup_instance.backup_dir,
                                 date = self.backup_date,
                                 port = self.instance.port)

        # 获得完整的本地备份 目录 或 文件
        self.backup_full_path = '{backup_dir}/{backup_name}'.format(
                           backup_dir = self.backup_dir,
                           backup_name = self.backup_name)

        # 设置MySQL实例信息
        self.db_conf = {
            'username' : self.instance.username,
            'password' : self.instance.password,
            'host' : Toolkit.num2ip(self.instance.host),
            'port' : self.instance.port
        }

        # 定义备份工具
        self.backup_tool = None

    def save_begin_backup_info(self):
        # 备份开始, 保存备份信息
        backup_info = DbmpMysqlBackupInfo(
                mysql_instance_id = self.backup_instance.mysql_instance_id,
                thread_id = os.getpid(),
                backup_dir = self.backup_full_path)

        is_ok, self.backup_info = self.dao_base.insert_obj(backup_info)

        if not is_ok: # 如果保存失败则直接退出
            ToolLog.log_error('!!!save dbmp_mysql_backup_info table fail!!!')
            ToolLog.log_error('sys exit.')
            Toolkit.send_mail()
            sys.exit(1)

    def create_backup_tool(self):
        """更具选择的备份工具创建相关备份实例
        # 1、mysqldump, 2、mysqlpump, 3、mydumper, 4、xtrabackup
        """

        if self.backup_instance.backup_tool == 1: # mysqldump
            self.backup_tool = Mysqldump(self.backup_name,
                 self.backup_dir,
                 backup_bin_file = self.backup_instance.backup_tool_file,
                 my_cnf = self.instance_info.my_cnf_path)

        elif self.backup_instance.backup_tool == 2: # mysqlpump
            pass
        elif self.backup_instance.backup_tool == 3: # mydumper
            pass
        elif self.backup_instance.backup_tool == 4: # xtrabackup
            self.backup_tool = Xtrabackup(self.backup_name,
                      self.backup_dir,
                      backup_bin_file = self.backup_instance.backup_tool_file,
                      my_cnf = self.instance_info.my_cnf_path)

        else: # 如果没有备份工具 则退出失败
            ToolLog.log_error('!!!can not find backup tool!!!')
            ToolLog.log_error('sys exit.')
            # 记录备份失败信息
            update_info = {'message': '没有找到相应的备份工具'}
            is_ok, self.backup_info = self.update_backup_info(update_info)

            Toolkit.send_mail()
            sys.exit(1)
                
        # 记录使用的备份工具
        ToolLog.log_info('use backup tool is: {tool}'.format(
                                tool = self.backup_instance.backup_tool_file))
        return self.backup_tool
        
    def backup_data(self):
        """使用Xtrabckup备份数据
        """
        # 开始执行备份
        is_ok = self.backup_tool.backup_data(
                        param = self.backup_instance.backup_tool_param,
                        **self.db_conf)

        # 如果备份失败世界返回
        if not is_ok:
            ToolLog.log_error('xtrabackup fail !!!')
            # 记录备份失败信息
            update_info = {'message': '备份数据失败', 'backup_data_status': 2}
            self.update_backup_info(update_info)
        else: # 记录备份成功
            update_info = {'backup_data_status': 3}
            self.update_backup_info(update_info)

        # 记录备份结束时间
        self.update_backup_info({'backup_end_time': datetime.now()})

        return is_ok

    def backup_binlog(self):
        """运行备份binlog
        """
        is_ok = False
        if self.backup_instance.is_binlog: # 判断是否需要备份binlog
            # 获得binlog路径
            value =  self.dao_base.get_global_variable(
                                          db_conf = self.db_conf,
                                          param = 'log_bin_basename')
            binlog_path, binlog_name = ToolSSH.get_file_path_and_name(value)
 
            # 拼凑binglog备份路径
            to_dir = '{backup_dir}/binlog'.format(backup_dir=self.backup_dir)
            is_ok = self.backup_tool.backup_binlog(from_dir = binlog_path,
                                             to_dir = to_dir,
                                             cmin = 1440)
            
            # 更新 备份binlog状态
            update_info = {}
            if is_ok: # 完成备份
                update_info['binlog_status'] = 3
            else: # 备份失败
                update_info['binlog_status'] = 2

            self.update_backup_info(update_info)

        return is_ok

    def compress_data(self):
        """压缩备份的数据
        """
        is_ok = False
        if self.backup_instance.is_compress:
            is_ok = self.backup_tool.compress(compress_type='gzip',
                                        file_type='dir')
            update_info = {}
            if is_ok: # 压缩完成 
                update_info['compress_status'] = 3
            else: # 压缩失败
                update_info['compress_status'] = 2

            self.update_backup_info(update_info)

        return is_ok

    def send_data(self):
        """将备份数据发送到远程
        """
        is_ok = False
        if self.backup_instance.is_to_remote:
            # 获得远程备份目录和远程OS主机ID
            backup_remotes = self.dao_base.get_objs_by_col(
                                 DbmpMysqlBackupRemote,
                                 DbmpMysqlBackupRemote.mysql_instance_id,
                                 self.instance.mysql_instance_id)

            # 如果有数据则进行获取操作系统信息
            if not backup_remotes:
                return is_ok

            # 获得远程备份MySQL实例信息
            backup_remote = backup_remotes.pop()

            # 通过远程备份信息, 获得操作系统信息
            cmdb_os = self.dao_base.get_obj_by_pri(
                                     CmdbO,
                                     backup_remote.os_id)
            if not cmdb_os: # 如果没有相关远程OS信息退出远程备份
                return is_ok       

            # 构造出远程备份文件名
            local_file = None
            if self.backup_tool.compress_file:
                local_file = self.backup_tool.compress_file
            elif self.backup_tool.backup_file:
                local_file = self.backup_tool.backup_file

            # 获得之前备份的名称
            parent_path, file_name = ToolSSH.get_file_path_and_name(
                                             local_file)

            # 备份文件名: {指定的远程目录}/{备份日期}/{MySQL实例端口}/{备份名称}
            remote_file = '{remote_dir}/{date}/{port}/{file_name}'.format(
                           remote_dir = backup_remote.remote_dir,
                           date = self.backup_date,
                           port = self.instance.port,
                           file_name = file_name)

            # 记录远程备份 目录 或 文件名
            self.update_backup_info({'remote_backup_dir': remote_file})

            # 记录发送开始时间
            self.update_backup_info({'trans_start_time': datetime.now()})

            # 备份发送到远程
            is_ok = self.backup_tool.send_backup(remote_file = remote_file,
                                    username = cmdb_os.username,
                                    password = cmdb_os.password,
                                    host = Toolkit.num2ip(cmdb_os.ip))
            # 记录发送结束时间
            self.update_backup_info({'trans_end_time': datetime.now()})
             
            update_info = {}
            if is_ok: # 传输数据到远程成功
                update_info['trans_data_status'] = 3
            else: # 传输数据到远程成功
                update_info['trans_data_status'] = 2

            self.update_backup_info(update_info)
    
        return is_ok
                    

    def send_binlog(self):
        """将备份的binlog发送到远程
        """
        # 判断是否需要备份binlog, 和是否需要将备份发送至远程
        is_ok = False
        if (self.backup_instance.is_to_remote and
            self.backup_instance.is_binlog): 
            # 获得远程备份目录和远程OS主机ID
            backup_remotes = self.dao_base.get_objs_by_col(
                                 DbmpMysqlBackupRemote,
                                 DbmpMysqlBackupRemote.mysql_instance_id,
                                 self.instance.mysql_instance_id)

            # 如果有数据则进行获取操作系统信息
            if not backup_remotes:
                return is_ok

            # 获得远程备份MySQL实例信息
            backup_remote = backup_remotes.pop()

            # 通过远程备份信息, 获得操作系统信息
            cmdb_os = self.dao_base.get_obj_by_pri(CmdbO,
                                            backup_remote.os_id)
            if not cmdb_os: # 如果没有相关远程OS信息退出远程备份
                return is_ok       

            # 构造远程binlog目录
            # 结构: {指定的远程目录}/{备份日期}/{MySQL实例端口}/binlog
            remote_binlog_dir = '{remote_dir}/{date}/{port}/binlog'.format(
                           remote_dir = backup_remote.remote_dir,
                           date = self.backup_date,
                           port = self.instance.port)
            # 传输binlog至远程
            is_ok = self.backup_tool.send_binlog(
                                   remote_dir = remote_binlog_dir,
                                   username = cmdb_os.username,
                                   password = cmdb_os.password,
                                   host = Toolkit.num2ip(cmdb_os.ip))
            update_info = {}
            if is_ok: # 传输binlog到远程成功
                update_info['trans_binlog_status'] = 3
            else: # 传输binlog到远程成功
                update_info['trans_binlog_status'] = 2

            self.update_backup_info(update_info)

        return is_ok
        
    def run_backup(self):
        """运行Xtrabackup的相关备份流程
        """
        # 1 备份数据
        backup_data_is_ok = self.backup_data()
        if not backup_data_is_ok: # 备份失败
            return backup_data_is_ok

        # 2 备份 binlog 
        backup_binlog_is_ok = self.backup_binlog()
            
        # 3 备份 my.cnf 
        self.backup_tool.backup_mycnf()

        # 4 压缩备份集
        compress_is_ok = self.compress_data()

        # 5 获得备份集大小并记录数据库
        backup_size = self.backup_tool.backup_size()
        update_info = {'backup_size': backup_size}
        self.update_backup_info(update_info)

        # 6 发送备份数据至远程
        send_data_is_ok, remote_file = self.send_data()

        # 7 发送备份binlog值远程
        send_binlog_is_ok, remote_binlog = self.send_binlog()

        # 8 更新备份状态信息
        update_info = {'backup_status': 3} # 初始设置为备份完成

        # 如果遇到备份返回信息和指定的备份形式不一样则设置为备份完成但和指定的有差异
        if (backup_binlog_is_ok != self.backup_instance.is_binlog or
            compress_is_ok != self.backup_instance.is_compress or
            send_data_is_ok != self.backup_instance.is_to_remote or
            send_binlog_is_ok != self.backup_instance.is_to_remote):

            update_info = {'backup_status': 5}
        self.update_backup_info(update_info)

        ToolLog.log_info('backup complete !')

        return backup_data_is_ok

    def run(self):
        """执行备份主逻辑
        """

        # 开始备份
        # 记录正在备份
        update_info = {'backup_status': 2}
        self.update_backup_info(update_info)

        # 创建备份工具实例
        self.create_backup_tool()

        # 判断备份的类型是什么类型, 并根据不同类型执行备份
        if self.backup_instance.backup_type == 1: # 强制指定实例备份
            self.run_backup()  
        elif self.backup_instance.backup_type == 2: # 强制寻找备份
            pass
        elif self.backup_instance.backup_type == 3: # 最优型备份
            pass
        else:
            return False

    def update_backup_info(self, update_info={}):
        """更新备份信息
        在备份过程中备份状态会经常变动, 该方法就是为了变更备份信息用的

        Args: 
            update_info: dict类型, 需要更新的数据
        return: None
        Raise: None
        """
        if not update_info:
            return None

        is_ok, self.backup_info = self.dao_base.update_objs_by_pri(
                                DbmpMysqlBackupInfo,
                                self.backup_info.mysql_backup_info_id,
                                update_info = update_info)
        return is_ok


def main():
    backup_main = BackupMain(1)
    backup_main.save_begin_backup_info()
    backup_main.run()


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

# 导入项目路径
import os
import sys
path = os.path.split(os.path.realpath(sys.argv[0]))[0]
home = "{path}/..".format(path=path)
sys.path.append(home)

from dao_base import DaoBase
from model.models import SysMysqlBackupInstance
from tool.toolkit import Toolkit
from tool.tool_log import ToolLog


class DaoSysMysqlBackupInstance(DaoBase):
    """操作系统的数据库操作类"""
   
    def __init__(self):
        super(DaoSysMysqlBackupInstance, self).__init__()
        
    def insert_obj(self, obj):
        """添加数据到数据库中
        Args:
            obj: 需要插入的对象
        Return: 
            True & False: 代表插入是否成功
        Raise: None
        """

        return super(DaoSysMysqlBackupInstance, self).insert_obj(obj)


    def get_obj_by_pri(self, pri_value, cols=[]):
        """通过主键获得数据
        Args:
            pri_value: sys_mysql_backup_instance 表的id值
            cols: 需要的字段
        Return: 
            obj: 返回一个SysMysqlBackupInstance 对象
        Raise: None
        """

        obj = super(DaoSysMysqlBackupInstance, self).get_obj_by_pri(
            SysMysqlBackupInstance,
            pri_value,
            cols
        )

        return obj


def main():
    
    # 查询 SysO 对象
    dao_sys_mysql_backup_instance = DaoSysMysqlBackupInstance()
    cols = []
    cols = [SysMysqlBackupInstance.mysql_backup_instance_id,
            SysMysqlBackupInstance.mysql_instance_id,
            SysMysqlBackupInstance.backup_tool,
            SysMysqlBackupInstance.backup_name,
            SysMysqlBackupInstance.create_time,
            SysMysqlBackupInstance.update_time]

    sys_mysql_backup_instance = dao_sys_mysql_backup_instance.get_obj_by_pri(1, cols)
    print sys_mysql_backup_instance

    """
    # 插入一个对象
    dao_sys_mysql_backup_instance = DaoSysMysqlBackupInstance()
    sys_mysql_backup_instance = SysMysqlBackupInstance(
                                   hostname = 'normal_11',
                                   alias = 'normal_11',
                                   ip = Toolkit.ip2num('192.168.137.11'),
                                   username = 'root',
                                   password = 'oracle',
                                   remark = '虚拟主机 normal 11')

    print dao_sys_mysql_backup_instance.insert_obj(sys_os)
    """
    

if __name__ == '__main__':
    main()

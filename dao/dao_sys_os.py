# -*- coding: utf-8 -*-

# 导入项目路径
import os
import sys
path = os.path.split(os.path.realpath(sys.argv[0]))[0]
home = "{path}/..".format(path=path)
sys.path.append(home)

from dao_base import DaoBase
from model.models import SysO
from tool.toolkit import Toolkit
from tool.tool_log import ToolLog


class DaoSysO(DaoBase):
    """操作系统的数据库操作类"""
   
    def __init__(self):
        super(DaoSysO, self).__init__()

    def insert_obj(self, obj):
        """添加数据到数据库中
        Args:
            obj: 需要插入的对象
        Return: 
            True & False: 代表插入是否成功
        Raise: None
        """

        return super(DaoSysO, self).insert_obj(obj)


    def get_obj_by_pri(self, pri_value, cols=[]):
        """通过主键获得数据
        Args:
            pri_value: sys_os 表的id值
            cols: 需要的字段
        Return: 
            obj: 返回一个SysO 对象
        Raise: None
        """

        obj = super(DaoSysO, self).get_obj_by_pri(
            SysO,
            pri_value,
            cols
        )

        return obj


def main():
    
    # 查询 SysO 对象
    dao_sys_os = DaoSysO()
    cols = [SysO.os_id, SysO.username, SysO.password]
    sys_os = dao_sys_os.get_obj_by_pri(1, cols)
    print sys_os

    """
    # 插入一个对象
    dao_sys_os = DaoSysO()
    sys_os = SysO(hostname = 'normal_11',
                  alias = 'normal_11',
                  ip = Toolkit.ip2num('192.168.137.11'),
                  username = 'root',
                  password = 'oracle',
                  remark = '虚拟主机 normal 11')
    print dao_sys_os.insert_obj(sys_os)
    """
    

if __name__ == '__main__':
    main()

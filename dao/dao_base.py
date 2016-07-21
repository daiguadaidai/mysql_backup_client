# -*- coding: utf-8 -*-

# 导入项目路径
import os
import sys
path = os.path.split(os.path.realpath(sys.argv[0]))[0]
home = "{path}/..".format(path=path)
sys.path.append(home)

import traceback
from mysql_conn import MysqlConn
from model.models import *
from sqlalchemy.orm.exc import NoResultFound
from tool.toolkit import Toolkit
from tool.tool_log import ToolLog
from tool.tool_conf import ToolConf


class DaoBase(object):
    """操作系统的数据库操作类"""
   
    def __init__(self):
        # 默认配置文件路径 [/xxx/]tool/../conf/db.cnf
        tool_conf = ToolConf()
        self.db_conf = tool_conf.get_conf_dict('mysql')
        ToolLog.log_info('db config: {conf}'.format(conf = self.db_conf))
        
        self.mysql_conn = MysqlConn(**self.db_conf)

    def insert_obj(self, obj):
        """添加数据到数据库中
        Args:
            obj: 需要插入的对象
        Return: 
            True & False: 代表插入是否成功
        Raise: None
        """
        self.session = self.mysql_conn.get_session()

        tag = False

        try:
            self.session.add(obj)
            self.session.commit()

            # 执行下面两语句会将主键值塞入obj中
            primary_key = obj.__table__.primary_key.columns.items()[0][0]
            eval('obj.{key}'.format(key = primary_key))

            tag = True
        except Exception, e:
            ToolLog.log_error('insert {obj} fail'.format(obj = type(obj)))
            ToolLog.log_error(e)
            ToolLog.log_error(traceback.format_stack())
        finally:
            self.session.close()
            return tag, obj

    

    def get_obj_by_pri(self, obj, pri_value, cols=[]):
        """通过id获得数据
        Args:
            pri_value: cmdb_os 表的id值
            cols: 需要的字段
            obj: model 类的字符串
                如: 'CmdbO'
            key: model 的主键字符串
                如: 'os_id'
        Return: 
            obj: 返回一个CmdbO 对象
        Raise: None
        """

        # 构造Model类在主键
        # pri_key = '{obj}.{key}'.format(obj=obj, key=key)

        self.session = self.mysql_conn.get_session()
        result = None

        # 构造主键名称, 这边的主键指的是一个增加的主键
        primary_key = obj.__table__.primary_key.columns.items()[0][0]
        obj_primary_key = eval('obj.{key}'.format(key = primary_key))
        
        if not cols: # 如果没有指定 列则获取所有的列 
            cols = obj.__table__.columns

        try:
            # 查询返回的 对象
            result = (self.session.query(obj)
                          .with_entities(*cols)
                          .filter(obj_primary_key == pri_value)
                          .one())
        except Exception as e:
            ToolLog.log_error('can not find obj by primary key {obj}'.
                              format(obj = type(obj)))
            ToolLog.log_error(e)
            ToolLog.log_error(traceback.format_stack())
        finally:
            self.session.close()
            return result 

    def get_objs_by_col(self, obj, name, value, cols=[]):
        """通过id获得数据
        Args:
            obj: model 类的字符串
                如: 'CmdbO'
            name: 字段
                如: CmdbO.name
            value: 制度按
            cols: 需要的字段
        Return: 
            objs: 返回一个 obj 列表
        Raise: None
        """
        self.session = self.mysql_conn.get_session()
        objs = None

        if not cols: # 如果没有指定 列则获取所有的列 
            cols = obj.__table__.columns

        try:
            # 查找出说的记录
            objs = (self.session.query(obj)
                          .with_entities(*cols)
                          .filter(name == value)
                          .all())
        except NoResultFound as e:
            ToolLog.log_error('can not find obj by primary key {obj}'.
                              format(obj = type(obj)))
            ToolLog.log_error(e)
            ToolLog.log_error(traceback.format_stack())
        finally:
            self.session.close()
            return objs

    def update_objs_by_pri(self, obj, value, update_info={}):
        """通过id跟新数据
        Args:
            obj: model 类
                如: 'CmdbO'
            value: 主键id值
            update_info: 跟新的信息就向 set 后边的信息
                {'name': 'aa', 'age': 12}
        Return: 
            is_ok, obj: 返回一个是否更新成功和obj
        Raise: None
        """
        self.session = self.mysql_conn.get_session()
        cmdb_os = None

        # 构造主键名称, 这边的主键指的是一个增加的主键
        primary_key = obj.__table__.primary_key.columns.items()[0][0]
        obj_primary_key = eval('obj.{key}'.format(key = primary_key))
        
        is_ok = False
        if not update_info: # 如果没有指定 列则获取所有的列 
            err_msg = 'update table: {table} not value'.format(
                                        table = obj.__table__.name)
            ToolLog.log_error(err_msg)
            return is_ok, obj

        try:
            # 查询返回的 对象
            (self.session.query(obj)
                         .filter(obj_primary_key == value)
                         .update(update_info))
            self.session.commit()
            is_ok = True
        except NoResultFound as e:
            ToolLog.log_error('can not find obj by primary key {obj}'.
                              format(obj = type(obj)))
            ToolLog.log_error(e)
            ToolLog.log_error(traceback.format_stack())
        finally:
            self.session.close()
            return is_ok, obj

    def exec_sql(self, db_conf={}, sql=None):
        """通过给定的SQL和数据库链接参数执行sql并返回数据
        
        Args:
            db_conf: 数据库连接参数
            sql: 执行的SQL
        Return:
            result 执行sql返回的数据
        Raise: None
        """
        if not sql: # 如果没有sql直接返回 None
            return None 

        result = None
        if not db_conf: # 如果没有传输数据库参数就查询 应用的MySQL
            try:
                self.session = self.mysql_conn.get_session()
                self.session.execute(sql)
            except NoResultFound as e:
                ToolLog.log_error('sql execute in self App MySQL')
                ToolLog.log_error('sql execute error: {sql}'.format(sql=sql))
                ToolLog.log_error(e)
                ToolLog.log_error(traceback.format_stack())
            finally:
                self.session.close()
        else: # 执行指定db_conf的SQL
            try:
                mysql_conn = MysqlConn(**db_conf)
                session = mysql_conn.get_session()
                # 执行SQL
                result = session.execute(sql).fetchall()
            except NoResultFound as e:
                ToolLog.log_error('db config: {conf}'.format(conf=db_conf))
                ToolLog.log_error('sql execute error: {sql}'.format(sql=sql))
                ToolLog.log_error(e)
                ToolLog.log_error(traceback.format_stack())
            finally:
                self.session.close()

        return result

    def get_global_variable(self, db_conf={}, param=None):
        """获得MySQL全局变量值

        Args:
            db_conf: 数据库链接参数
            param: 全局变量key
        Return:
            value 全局变量值
        Raise: None
        """
        pass
        if not param or not db_conf:
            return None
        
        # 创建 SHOW global vairables sql
        sql = 'SHOW GLOBAL VARIABLES LIKE "{param}"'.format(param=param)
 
        result = self.exec_sql(db_conf=db_conf, sql=sql)
        if not result:
            return result

        key, value = result.pop()
        return value

            

def main():
    
    """
    # 查询 CmdbO 对象
    dao_cmdb_os = DaoCmdbO()
    cols = [CmdbO.os_id, CmdbO.username, CmdbO.password]
    cmdb_os = dao_cmdb_os.get_obj_by_pri(1, cols)
    print cmdb_os.os_id
    """

    # 插入一个对象
    dao_cmdb_os = DaoCmdbO()
    cmdb_os = CmdbO(hostname = 'normal_11',
                  alias = 'normal_11',
                  ip = Toolkit.ip2num('192.168.137.11'),
                  username = 'root',
                  password = 'oracle',
                  remark = '虚拟主机 normal 11')
    print dao_cmdb_os.insert_obj(cmdb_os)
    

if __name__ == '__main__':
    main()

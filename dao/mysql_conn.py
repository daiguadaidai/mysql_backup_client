# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class MysqlConn(object):
    """MySQL 数据源的类
    
    Attribute:
        engine: sqlalchemy 的引擎
        DBSession: sqlalchemy 的session
    """

    def __init__(self, username='', password='', host='127.0.0.1', 
                       port=3306, database=''):
        self.db_config_string = ('mysql://{username}:{password}'
                                 '@{host}:{port}/{database}'
                                 '?charset=utf8'.format(username = username,
                                                        password = password,
                                                        host = host,
                                                        port = port,
                                                        database=database))
        self.engine = create_engine(self.db_config_string)
        self.DBSession = sessionmaker(bind=self.engine)

    def get_session(self):
        """获得数据库链接
   
        Args:
            conf: 数据库链接参数一般不带有数据库名,如下显示:
                conf = {
                  'host'     : '192.168.1.233',
                  'port'     : '3306',
                  'user'     : 'HH',
                  'password' : 'oracle'
                  'database' : 'my_free'
                }
        Return:
            返回一个数据库session对象
        """

        self.session = self.DBSession()
        return self.session

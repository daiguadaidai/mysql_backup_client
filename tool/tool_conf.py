# -*- coding: utf-8 -*-

import os
import sys
path = os.path.split(os.path.realpath(sys.argv[0]))[0]
sys.path.append('{path}/..'.format(path=path))

import ConfigParser

class ToolConf(object):
    """这是一个解析配置文件的工具
    """
    # 定义配置文件名称
    CONF_FILE = '{path}/../conf/db.cnf'.format(path=path)

    def __init__(self, db_cnf = CONF_FILE):
        self.db_cnf = db_cnf
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(self.db_cnf) 
        self.sections = self.cf.sections()

    def get_conf_dict(self, section='mysql'):
        """读取配置文件中的配置并转化成一个dict对象
        Args:
            section: 需要获取的配置部分
        Return:
            conf_dict: 将配置转化后的对象
        Raise: None
        """
        items = self.cf.items(section)
        conf_dict = dict(items)
        return conf_dict 

def main():
    tool_conf = ToolConf()
    db_conf = tool_conf.get_conf_dict()
    print db_conf

if __name__ == '__main__':
    main()

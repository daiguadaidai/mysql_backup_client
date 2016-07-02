# -*- coding: utf-8 -*-

import os
import sys
path = os.path.split(os.path.realpath(sys.argv[0]))[0]
home = "{path}/..".format(path=path)
sys.path.append(home)

import logging

file_name = '{home}/log/backup.log'.format(home=home)
# 设置日志格式
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    filename = file_name,
    filemode = 'a',
    datefmt = '%Y-%m-%d %X'
)

class ToolLog(object):
    """这个是专门记录日志信息的类
    """

    filename = file_name

    def __init__(self):
        pass
        
    @classmethod
    def log_info(self, msg):
        """记录日志
        将给定的信息记入日志

        Args:
            msg: 给定的信息
        Return: None
        Raise: None
        """
        logging.info(msg)
    
    @classmethod
    def log_error(self, msg):
        """记录日志
        将给定的信息记入日志

        Args:
            msg: 给定的信息
        Return: None
        Raise: None
        """
        logging.error(msg)
    
    @classmethod
    def log_warning(self, msg):
        """记录日志
        将给定的信息记入日志

        Args:
            msg: 给定的信息
        Return: None
        Raise: None
        """
        logging.warning(msg)
    
    @classmethod
    def log_debug(self, msg):
        """记录日志
        将给定的信息记入日志

        Args:
            msg: 给定的信息
        Return: None
        Raise: None
        """
        logging.debug(msg)
    

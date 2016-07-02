# -*- coding: utf-8 -*-

import os
import sys
path = os.path.split(os.path.realpath(sys.argv[0]))[0]
sys.path.append("{path}/..".format(path=path))

import tarfile
import subprocess
from tool_log import ToolLog
from toolkit import Toolkit

class ToolCompress(object):
    """这是一个(压缩/解压)文件工具类
    """

    def __init__(self):
       pass

    @classmethod
    def targz(self, from_file, to_file=None, from_file_type='file'):
        """压缩文件 tar.gz
        将给定的文件压缩成 gzip 格式的文件
        注意: 压缩文件的存放位置暂时只支持在from_file 文件的目录下
        Args:
            from_file: 需要压缩的文件
            to_file: 压缩成为的文件
            from_file_type: from_file 文件的类型 是文件 还是 目录
        Return:
            返回一个压缩的文件路径和文件名称
        Raise: None
        """

        if not to_file: # 判断并构造压缩文件名
            to_file = '{file}.tar.gz'.format(file=from_file)

        # 获得文件名和文件所在路径
        form_file_path, from_file_name = self.get_file_path_and_name(from_file)

        cmd = 'cd {file_path} && tar -zcf {to_file} {file_name}'.format(
            file_path = form_file_path,
            to_file = to_file,
            file_name = from_file_name,
        )

        # 执行打包命令
        is_ok = Toolkit.exec_cmd(cmd)

        return is_ok, to_file, cmd

    @classmethod
    def tarbz2(self, from_file, to_file=None, from_file_type='file'):
        """压缩文件 tar.bz2
        将给定的文件压缩成 bzip2 格式的文件
        注意: 压缩文件的存放位置暂时只支持在from_file 文件的目录下
        Args:
            from_file: 需要压缩的文件
            to_file: 压缩成为的文件
            from_file_type: from_file 文件的类型 是文件 还是 目录
        Return:
            返回一个压缩的文件路径和文件名称
        Raise: None
        """

        if not to_file: # 判断并构造压缩文件名
            to_file = '{file}.tar.bz2'.format(file=from_file)

        # 获得文件名和文件所在路径
        form_file_path, from_file_name = self.get_file_path_and_name(from_file)

        cmd = 'cd {file_path} && tar -jcf {to_file} {file_name}'.format(
            file_path = form_file_path,
            to_file = to_file,
            file_name = from_file_name,
        )

        # 执行打包命令
        is_ok = Toolkit.exec_cmd(cmd)

        return is_ok, to_file, cmd

    @classmethod
    def tarxz(self, from_file, to_file=None, from_file_type='file'):
        """压缩文件 tar.xz
        将给定的文件压缩成 xz 格式的文件
        注意: 压缩文件的存放位置暂时只支持在from_file 文件的目录下
        Args:
            from_file: 需要压缩的文件
            to_file: 压缩成为的文件
            from_file_type: from_file 文件的类型 是文件 还是 目录
        Return:
            返回一个压缩的文件路径和文件名称
        Raise: None
        """

        if not to_file: # 判断并构造压缩文件名
            to_file = '{file}.tar.xz'.format(file=from_file)

        # 获得文件名和文件所在路径
        form_file_path, from_file_name = self.get_file_path_and_name(from_file)

        cmd = 'cd {file_path} && tar -Jcf {to_file} {file_name}'.format(
            file_path = form_file_path,
            to_file = to_file,
            file_name = from_file_name,
        )

        # 执行打包命令
        is_ok = Toolkit.exec_cmd(cmd)

        return is_ok, to_file, cmd

    @classmethod
    def tarlzma(self, from_file, to_file=None, from_file_type='file'):
        """压缩文件 tar.lzma
        将给定的文件压缩成 lzma 格式的文件
        注意: 压缩文件的存放位置暂时只支持在from_file 文件的目录下
        Args:
            from_file: 需要压缩的文件
            to_file: 压缩成为的文件
            from_file_type: from_file 文件的类型 是文件 还是 目录
        Return:
            返回一个压缩的文件路径和文件名称
        Raise: None
        """

        if not to_file: # 判断并构造压缩文件名
            to_file = '{file}.tar.lzma'.format(file=from_file)

        # 获得文件名和文件所在路径
        form_file_path, from_file_name = self.get_file_path_and_name(from_file)

        cmd = 'cd {file_path} && tar -c --lzma -f {to_file} {file_name}'.format(
            file_path = form_file_path,
            to_file = to_file,
            file_name = from_file_name,
        )

        # 执行打包命令
        is_ok = Toolkit.exec_cmd(cmd)

        return is_ok, to_file, cmd

    @classmethod
    def ziper(self, from_file, to_file=None, from_file_type='file'):
        """压缩文件 zip
        将给定的文件压缩成 zip 格式的文件
        注意: 压缩文件的存放位置暂时只支持在from_file 文件的目录下
        Args:
            from_file: 需要压缩的文件
            to_file: 压缩成为的文件
            from_file_type: from_file 文件的类型 是文件 还是 目录
        Return:
            返回一个压缩的文件路径和文件名称
        Raise: None
        """

        if not to_file: # 判断并构造压缩文件名
            to_file = '{file}.zip'.format(file=from_file)

        # 获得文件名和文件所在路径
        form_file_path, from_file_name = self.get_file_path_and_name(from_file)

        cmd = 'cd {file_path} && zip -r {to_file} {file_name}'.format(
            file_path = form_file_path,
            to_file = to_file,
            file_name = from_file_name,
        )

        # 执行打包命令
        is_ok = Toolkit.exec_cmd(cmd)

        return is_ok, to_file, cmd
        
    @classmethod
    def get_file_path_and_name(self, path):
        """获得文件所在目录和文件名称名称
        Args:
            path: 文件的完整路径
        Return:
            (parent_path, file_name) 文件或目录的父路径 和 文件名称
        Raise: None
        """
        file_name = os.path.basename(path)
        parent_path = os.path.dirname(path)
      
        return parent_path, file_name


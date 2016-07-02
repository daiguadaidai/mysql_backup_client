# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class SysMysqlBackupInfo(Base):
    __tablename__ = 'sys_mysql_backup_info'

    mysql_backup_info_id = Column(Integer, primary_key=True)
    mysql_instance_id = Column(Integer, nullable=False, index=True)
    backup_status = Column(Integer, nullable=False, server_default=text("'1'"))
    backup_data_status = Column(Integer, nullable=False, server_default=text("'1'"))
    check_status = Column(Integer, nullable=False, server_default=text("'1'"))
    binlog_status = Column(Integer, nullable=False, server_default=text("'1'"))
    trans_data_status = Column(Integer, nullable=False, server_default=text("'1'"))
    trans_binlog_status = Column(Integer, nullable=False, server_default=text("'1'"))
    compress_status = Column(Integer, nullable=False, server_default=text("'1'"))
    thread_id = Column(Integer, nullable=False, server_default=text("'-1'"))
    backup_folder = Column(String(50), nullable=False, server_default=text("''"))
    backup_size = Column(BigInteger, nullable=False, server_default=text("'0'"))
    backup_start_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    backup_end_time = Column(DateTime)
    check_start_time = Column(DateTime)
    check_end_time = Column(DateTime)
    trans_start_time = Column(DateTime)
    trans_end_time = Column(DateTime)
    message = Column(String(50), nullable=False, server_default=text("''"))


class SysMysqlBackupInstance(Base):
    __tablename__ = 'sys_mysql_backup_instance'

    mysql_backup_instance_id = Column(Integer, primary_key=True)
    mysql_instance_id = Column(Integer, nullable=False, unique=True)
    backup_tool = Column(Integer, nullable=False, server_default=text("'4'"))
    backup_type = Column(Integer, nullable=False, server_default=text("'1'"))
    is_all_instance = Column(Integer, nullable=False, server_default=text("'1'"))
    is_binlog = Column(Integer, nullable=False, server_default=text("'1'"))
    is_compress = Column(Integer, nullable=False, server_default=text("'1'"))
    is_to_remote = Column(Integer, nullable=False, server_default=text("'0'"))
    backup_dir = Column(String(200), nullable=False, server_default=text("''"))
    backup_tool_file = Column(String(200), nullable=False, server_default=text("''"))
    backup_tool_param = Column(String(200), nullable=False, server_default=text("''"))
    backup_name = Column(String(100), nullable=False, server_default=text("''"))
    create_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class SysMysqlBackupRemote(Base):
    __tablename__ = 'sys_mysql_backup_remote'

    mysql_backup_remote_id = Column(Integer, primary_key=True)
    os_id = Column(Integer, nullable=False, index=True)
    mysql_instance_id = Column(Integer, nullable=False, unique=True)
    remote_dir = Column(String(200), nullable=False, server_default=text("''"))
    create_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class SysMysqlBusinessGroup(Base):
    __tablename__ = 'sys_mysql_business_group'

    mysql_business_group_id = Column(Integer, primary_key=True)
    alias = Column(String(40), nullable=False, server_default=text("''"))
    remark = Column(String(50), nullable=False, server_default=text("''"))
    create_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class SysMysqlHaGroup(Base):
    __tablename__ = 'sys_mysql_ha_group'

    mysql_ha_group_id = Column(Integer, primary_key=True)
    alias = Column(String(40), nullable=False, server_default=text("''"))
    remark = Column(String(50), nullable=False, server_default=text("''"))
    create_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class SysMysqlHaGroupDetail(Base):
    __tablename__ = 'sys_mysql_ha_group_detail'

    mysql_ha_group_detail_id = Column(Integer, primary_key=True)
    mysql_instance_id = Column(Integer, nullable=False, unique=True)
    mysql_ha_group_id = Column(Integer, nullable=False, index=True)
    backup_priority = Column(Integer, nullable=False, server_default=text("'0'"))
    create_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class SysMysqlInstance(Base):
    __tablename__ = 'sys_mysql_instance'

    mysql_instance_id = Column(Integer, primary_key=True)
    os_id = Column(Integer, nullable=False, index=True)
    host = Column(Integer, nullable=False, server_default=text("'0'"))
    port = Column(Integer, nullable=False, server_default=text("'0'"))
    username = Column(String(30), nullable=False, server_default=text("''"))
    password = Column(String(200), nullable=False, server_default=text("''"))
    remark = Column(String(50), nullable=False, server_default=text("''"))
    create_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class SysMysqlInstanceInfo(Base):
    __tablename__ = 'sys_mysql_instance_info'

    mysql_instance_info_id = Column(Integer, primary_key=True)
    mysql_instance_id = Column(Integer, nullable=False, index=True)
    my_cnf_path = Column(String(200), nullable=False, server_default=text("''"))
    create_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class SysO(Base):
    __tablename__ = 'sys_os'

    os_id = Column(Integer, primary_key=True)
    hostname = Column(String(50), nullable=False, server_default=text("''"))
    alias = Column(String(40), nullable=False, server_default=text("''"))
    ip = Column(Integer, nullable=False, server_default=text("'0'"))
    username = Column(String(30), nullable=False, server_default=text("''"))
    password = Column(String(200), nullable=False, server_default=text("''"))
    remark = Column(String(50), nullable=False, server_default=text("''"))
    create_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

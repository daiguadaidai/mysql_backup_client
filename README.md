# mysql_backup_client #

MySQL 备份客户端，主要用于日常对MySQL的备份。

------------------------------

1. **安装Python相关模块**

需要相关的MySQL ORM模块

    $ pip install sqlalchemy
    $ pip install MySQL-python


2. **确保在需要备份的操作系统上能使用mysqldump和pt工具(xtrabackup)能正常的备份** <br />

确保类似如下命令能正常使用：

	$ mysqldump -uxxxx -pxxxx -hxxxx -pxxxx --all-database > db.sql

    $ innobackupex \
          --defaults-file=/etc/my.cnf \
          --user=xxxx \
          --password=xxxx \
          --host=xxxx \
          --port=3306 /tmp \
          --no-timestamp  >> /tmp/xtrabckup.log 2>&1 

3、**创建数据库，用户记录源信息**

在项目的 sql 目录里面有一个 my_free.sql 文件
导入数据库:

    $ mysql -uxxxx -pxxxx -hxxxx -pxxxx < my_free.sql

4、**添加备份源信息**

具体的字段名请对照 my_free.sql 或 使用 SHOW CREATE TABLE xxx; 来查看

    -- 添加操作系统信息
    INSERT INTO sys_os VALUES(1, 'hostname', 'alias', inet_aton('xxx.xxx.xxx.xxx'), 'username', 'password', 'this is remark', NOW(), NOW());
    
    -- 添加 MySQL 实例信息
    INSERT INTO sys_mysql_instance VALUES(1, 1, inet_aton('xxx.xxx.xxx.xxx'), 3306, 'username', 'password', '数据库实例信息', NOW(), NOW());
    
    -- 添加 MySQL 实例额外信息
    INSERT INTO sys_mysql_instance_info VALUES(1, 1, '/etc/my_3306.cnf', NOW(), NOW());
    
    -- 添加需要备份的 MySQL 实例信息
    INSERT INTO sys_mysql_backup_instance VALUES(1, 1, 4, 1, 1, 1, 1, 1, '/tmp/backup', '/usr/local/percona-xtrabackup/bin/innobackupex', '', 'xtrabackup', NOW(), NOW());
    
    -- 添加将备份传输到远程的目录
    INSERT INTO sys_mysql_backup_remote VALUES(1, 1, 1, '/u01/backup', NOW(), NOW());

5、**配置数据库源信息数据库的参数**

文件：conf/db.cnf

    [mysql]
    username = HH
    password = oracle
    database = my_free
    host = 192.168.137.11
    port = 3306

6、主程序参数讲解
文件：main/backup_main.py
方法：
def main():
    backup_main = BackupMain(1)
    backup_main.save_begin_backup_info()
    backup_main.run()
    
> 需要注意的是 BackupMain(1)，这边的1代表的是需要备份的 MySQL 实例信息ID，也就是表sys_mysql_backup_instance中记录的主键ID。

7、**运行备份**

    $ python main/backup_main.py

8、**在运行的过程中的日志都输出到了log目录**

文件：log/backup.log

可以在备份的时候跟踪查看log日志

    tail -f log/backup.log

> **Tip**：如果需要对`MySQL`表映射成`sqlalchemy`的`model`就需要安装`sqlautocode` 的`Python`模块
> 
>     -- 安装 sqlautocode 模块
>     $ pip install sqlautocode
>     
>     -- 生成 model
>     sqlautocode MySQL://username:password@host:port/database -o model_name.py -t table_name -e --force


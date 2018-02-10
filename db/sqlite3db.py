# -*- coding: utf-8 -*-
'''
Created on 2018-02-08 18:29
---------
@summary: python 自带的轻量级数据库
可视化客户端推荐 SQLiteStudio
---------
@author: Boris
'''
import sys
sys.path.append('../')
import init

import sqlite3
import utils.tools as tools
from utils.log import log

DB        = tools.get_conf_value('config.conf', 'sqlite3', 'db')

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls)

        return cls._inst


class Sqlite3(Singleton):
    def __init__(self,db = DB):
        '''
        @summary:
        ---------
        @param db: D:/test.db
        ---------
        @result:
        '''

        super(Sqlite3, self).__init__()

        if not hasattr(self,'conn'):
            try:
                self.conn = sqlite3.connect(db, check_same_thread=False)
                self.cursor = self.conn.cursor()
            except Exception as e:
                raise
            else:
                log.debug('连接到数据库 %s'%db)

    def create_table(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.debug(e)
            return False

        return True

    def find(self, sql, fetch_one = False):
        result = []
        if fetch_one:
            result =  self.cursor.execute(sql).fetchone()
        else:
            result =  self.cursor.execute(sql).fetchall()

        return result

    def add(self, sql, exception_callfunc = ''):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            if exception_callfunc:
                exception_callfunc(e)

            return False
        else:
            return True

    def add_batch(self, sql, datas):
        '''
        @summary: 批量添加
        ---------
        @param sql:INSERT INTO book VALUES (?, ?, ?, ?, ?)
        @param datas:
        datas = [
                    (1, 1, 'Cook Recipe', 3.12, 1),
                    (2, 3, 'Python Intro', 17.5, 2),
                    (3, 2, 'OS Intro', 13.6, 2),
                ]
        ---------
        @result:
        '''
        try:
            self.cursor.executemany(sql, datas)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            if exception_callfunc:
                exception_callfunc(e)

            return False
        else:
            return True



    def update(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            return False
        else:
            return True

    def delete(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            log.error(e)
            return False
        else:
            return True

    def set_unique_key(self, table, key):
        try:
            sql = 'alter table %s add unique (%s)'%(table, key)
            self.cursor.execute(sql)
            self.conn.commit()

        except Exception as e:
            log.error(table + ' ' + str(e) + ' key = '+ key)
        else:
            log.debug('%s表创建唯一索引成功 索引为 %s'%(table, key))

    def set_primary_key(self, table, key = "ID"):
        try:
            sql = 'alter table {table_name} add constraint pk_{key} primary key ({key})'.format(table_name = table, key = key)
            self.cursor.execute(sql)
            self.conn.commit()

        except Exception as e:
            log.error(table + ' ' + str(e) + ' key = '+ key)
        else:
            log.debug('%s表创建主键成功 主键为 %s'%(table, key))

    def close(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    sqlite3db = Sqlite3()

    sql = '''
            CREATE TABLE if not exists sogou_cookies (
            id                  INTEGER          PRIMARY KEY AUTOINCREMENT,
            cookie              VARCHAR( 1000 )  UNIQUE,
            is_available        BOOLEAN          DEFAULT ( 1 ),
            un_available_time   DATETIME,
            un_available_times  INTEGER          DEFAULT ( 0 )
        )
    '''

    sqlite3db.create_table(sql)


